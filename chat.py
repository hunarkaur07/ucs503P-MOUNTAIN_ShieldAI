from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ChatMessage

from auth import verify_access_token
from redis_stream import publish_chat_message

from collections import defaultdict, deque
from datetime import datetime, timedelta


# =========================
# RATE LIMIT CONFIGURATION
# =========================

MAX_MESSAGES = 10
RATE_LIMIT_WINDOW_SECONDS = 60


# =========================
# CONNECTION MANAGER
# =========================

class ConnectionManager:

    def __init__(self):

        # WebSocket connections per geofence
        self.active_connections = {}

        # Online users per geofence
        self.online_users = {}

        # Message timestamps per geofence
        self.geofence_message_times = defaultdict(deque)


    # =========================
    # CHECK GEOFENCE RATE LIMIT
    # =========================

    def is_rate_limited(
        self,
        geofence_id: int
    ):

        now = datetime.utcnow()

        cutoff = now - timedelta(
            seconds=RATE_LIMIT_WINDOW_SECONDS
        )

        message_times = self.geofence_message_times[
            geofence_id
        ]


        # Remove timestamps outside rate-limit window
        while (
            message_times
            and message_times[0] < cutoff
        ):

            message_times.popleft()


        # Check limit
        if len(message_times) >= MAX_MESSAGES:

            return True


        # Record this message
        message_times.append(
            now
        )

        return False


    # =========================
    # CONNECT USER
    # =========================

    async def connect(
        self,
        websocket: WebSocket,
        geofence_id: int,
        user_id: int
    ):

        await websocket.accept()


        # Create geofence room if needed
        if geofence_id not in self.active_connections:

            self.active_connections[
                geofence_id
            ] = []


        # Add WebSocket
        self.active_connections[
            geofence_id
        ].append(websocket)


        # Create presence room if needed
        if geofence_id not in self.online_users:

            self.online_users[
                geofence_id
            ] = set()


        # Mark user online
        self.online_users[
            geofence_id
        ].add(user_id)


        # Broadcast presence update
        await self.broadcast(

            {
                "type": "presence",
                "user_id": user_id,
                "status": "online"
            },

            geofence_id

        )


    # =========================
    # DISCONNECT USER
    # =========================

    async def disconnect(
        self,
        websocket: WebSocket,
        geofence_id: int,
        user_id: int
    ):

        # Remove WebSocket connection
        if geofence_id in self.active_connections:

            if websocket in self.active_connections[
                geofence_id
            ]:

                self.active_connections[
                    geofence_id
                ].remove(websocket)


            # Remove empty room
            if not self.active_connections[
                geofence_id
            ]:

                del self.active_connections[
                    geofence_id
                ]


        # Mark user offline
        if geofence_id in self.online_users:

            self.online_users[
                geofence_id
            ].discard(user_id)


            # Remove empty presence room
            if not self.online_users[
                geofence_id
            ]:

                del self.online_users[
                    geofence_id
                ]


        # Broadcast offline presence update
        await self.broadcast(

            {
                "type": "presence",
                "user_id": user_id,
                "status": "offline"
            },

            geofence_id

        )


    # =========================
    # BROADCAST MESSAGE
    # =========================

    async def broadcast(
        self,
        message: dict,
        geofence_id: int
    ):

        if geofence_id not in self.active_connections:

            return


        disconnected_connections = []


        for connection in list(
            self.active_connections[
                geofence_id
            ]
        ):

            try:

                await connection.send_json(
                    message
                )

            except Exception:

                disconnected_connections.append(
                    connection
                )


        # Remove broken connections
        for connection in disconnected_connections:

            if connection in self.active_connections.get(
                geofence_id,
                []
            ):

                self.active_connections[
                    geofence_id
                ].remove(
                    connection
                )


        # Remove empty room
        if (
            geofence_id in self.active_connections
            and not self.active_connections[
                geofence_id
            ]
        ):

            del self.active_connections[
                geofence_id
            ]


    # =========================
    # GET ONLINE USERS
    # =========================

    def get_online_users(
        self,
        geofence_id: int
    ):

        if geofence_id not in self.online_users:

            return []


        return list(
            self.online_users[
                geofence_id
            ]
        )


# =========================
# CONNECTION MANAGER INSTANCE
# =========================

manager = ConnectionManager()


# =========================
# SAVE CHAT MESSAGE
# =========================

async def save_chat_message(
    user_id: int,
    geofence_id: int,
    message: str
):

    db: Session = SessionLocal()


    try:

        chat_message = ChatMessage(

            user_id=user_id,

            geofence_id=geofence_id,

            message=message

        )


        db.add(
            chat_message
        )

        db.commit()

        db.refresh(
            chat_message
        )

        return chat_message


    finally:

        db.close()


# =========================
# WEBSOCKET CHAT
# =========================

async def chat_websocket(
    websocket: WebSocket,
    geofence_id: int
):

    # =========================
    # GET JWT TOKEN
    # =========================

    token = websocket.query_params.get(
        "token"
    )


    if not token:

        await websocket.close(
            code=1008
        )

        return


    # =========================
    # VERIFY JWT TOKEN
    # =========================

    user_id = verify_access_token(
        token
    )


    if user_id is None:

        await websocket.close(
            code=1008
        )

        return


    # =========================
    # CONNECT AUTHENTICATED USER
    # =========================

    await manager.connect(

        websocket=websocket,

        geofence_id=geofence_id,

        user_id=user_id

    )


    try:

        while True:

            data = await websocket.receive_json()

            message_text = data.get(
                "message"
            )


            # =========================
            # EMPTY MESSAGE CHECK
            # =========================

            if (

                not message_text

                or not message_text.strip()

            ):

                await websocket.send_json(

                    {
                        "type": "error",
                        "message":
                            "Message cannot be empty"
                    }

                )

                continue


            message_text = message_text.strip()


            # =========================
            # GEOFENCE RATE LIMIT CHECK
            # =========================

            if manager.is_rate_limited(
                geofence_id
            ):

                await websocket.send_json(

                    {
                        "type": "error",
                        "message":
                            "Too many messages in this geofence. Please wait."
                    }

                )

                continue


            # =========================
            # SAVE TO POSTGRESQL
            # =========================

            saved_message = await save_chat_message(

                user_id=user_id,

                geofence_id=geofence_id,

                message=message_text

            )


            # =========================
            # PUBLISH TO REDIS STREAM
            # =========================

            await publish_chat_message(

                user_id=user_id,

                geofence_id=geofence_id,

                message=message_text

            )


            # =========================
            # BROADCAST MESSAGE
            # =========================

            await manager.broadcast(

                {
                    "type": "message",

                    "id":
                        saved_message.id,

                    "user_id":
                        saved_message.user_id,

                    "geofence_id":
                        saved_message.geofence_id,

                    "message":
                        saved_message.message,

                    "created_at":
                        saved_message.created_at.isoformat()
                },

                geofence_id

            )


    # =========================
    # USER DISCONNECTED
    # =========================

    except WebSocketDisconnect:

        await manager.disconnect(

            websocket=websocket,

            geofence_id=geofence_id,

            user_id=user_id

        )