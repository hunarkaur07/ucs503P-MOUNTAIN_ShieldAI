import redis.asyncio as redis
import json


# =========================
# REDIS CONNECTION
# =========================

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# =========================
# REDIS STREAM NAME
# =========================

CHAT_STREAM = "mountainshield_chat"


# =========================
# ADD MESSAGE TO STREAM
# =========================

async def publish_chat_message(
    user_id: int,
    geofence_id: int,
    message: str
):

    await redis_client.xadd(

        CHAT_STREAM,

        {

            "user_id": str(user_id),

            "geofence_id": str(geofence_id),

            "message": message

        }

    )


# =========================
# READ STREAM MESSAGES
# =========================

async def get_recent_messages(
    count: int = 20
):

    messages = await redis_client.xrevrange(

        CHAT_STREAM,

        max="+",

        min="-",

        count=count

    )

    result = []

    for message_id, data in reversed(messages):

        result.append(

            {

                "id": message_id,

                "user_id":
                    int(data["user_id"]),

                "geofence_id":
                    int(data["geofence_id"]),

                "message":
                    data["message"]

            }

        )

    return result