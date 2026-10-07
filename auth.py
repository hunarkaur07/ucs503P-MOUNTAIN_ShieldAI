from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from database import get_db


# =========================
# ROUTER
# =========================

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD HASHING
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================
# REQUEST MODELS
# =========================

class RegisterRequest(BaseModel):

    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


# =========================
# PASSWORD FUNCTIONS
# =========================

def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =========================
# CREATE JWT TOKEN
# =========================

def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================
# VERIFY JWT TOKEN
# =========================

def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            return None

        return int(user_id)

    except (JWTError, ValueError):

        return None


# =========================
# REGISTER
# =========================

@router.post("/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = db.execute(
        text("""
            SELECT id
            FROM users
            WHERE email = :email
        """),
        {
            "email": user.email
        }
    ).fetchone()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # Hash password
    hashed_password = hash_password(
        user.password
    )


    # Insert user
    result = db.execute(
        text("""
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (
                :name,
                :email,
                :password_hash
            )
            RETURNING id, name, email
        """),
        {
            "name": user.name,
            "email": user.email,
            "password_hash": hashed_password
        }
    ).fetchone()


    db.commit()


    return {

        "message": "User registered successfully",

        "user": {

            "id": result[0],

            "name": result[1],

            "email": result[2]

        }

    }


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    user: LoginRequest,
    db: Session = Depends(get_db)
):

    result = db.execute(
        text("""
            SELECT
                id,
                name,
                email,
                password_hash
            FROM users
            WHERE email = :email
        """),
        {
            "email": user.email
        }
    ).fetchone()


    if not result:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


    user_id = result[0]
    name = result[1]
    email = result[2]
    password_hash = result[3]


    # Verify password
    if not verify_password(
        user.password,
        password_hash
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


    # Create JWT
    access_token = create_access_token(

        data={

            "sub": str(user_id),

            "email": email

        }

    )


    return {

        "access_token": access_token,

        "token_type": "bearer",

        "user": {

            "id": user_id,

            "name": name,

            "email": email

        }

    }


# =========================
# CURRENT USER
# =========================

security = HTTPBearer()


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):

    token = credentials.credentials


    # Verify token
    user_id = verify_access_token(
        token
    )


    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


    # Get user
    result = db.execute(
        text("""
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = :id
        """),
        {
            "id": user_id
        }
    ).fetchone()


    if not result:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    return {

        "id": result[0],

        "name": result[1],

        "email": result[2]

    }