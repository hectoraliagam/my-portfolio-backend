from fastapi import FastAPI, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas import ContactForm
from app.models import Contact, Base
from app.database import engine, SessionLocal
from app.auth import router as auth_router
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi import Limiter
from pydantic import SecretStr
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import httpx
import os

load_dotenv()

Base.metadata.create_all(bind=engine)

is_dev = os.getenv("IS_DEV", "false").lower() == "true"

app = FastAPI(
    docs_url=None if not is_dev else "/docs",
    redoc_url=None if not is_dev else "/redoc"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Por favor, reduce la velocidad."}
    )

frontend_urls = os.getenv("FRONTEND_URLS", "https://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MY_MAIL_USERNAME", ""),
    MAIL_PASSWORD=SecretStr(os.getenv("MY_MAIL_PASSWORD", "")),
    MAIL_FROM=os.getenv("MY_MAIL_FROM", ""),
    MAIL_PORT=587,
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def verify_recaptcha(recaptcha_token: str):
    secret = os.getenv("RECAPTCHA_SECRET_KEY")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": recaptcha_token}
        )
    result = response.json()
    print("reCAPTCHA verify response:", result)  # <-- debug
    return result.get("success", False) and result.get("score", 0) >= 0.5

@app.post("/contact")
@limiter.limit("3/minute")
async def send_contact(
    request: Request,
    form: ContactForm,
    db: Session = Depends(get_db),
    recaptcha_token: str = Header(...)
):
    if not await verify_recaptcha(recaptcha_token):
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed.")

    contact = Contact(name=form.name, email=form.email, message=form.message)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    mail_receiver = os.getenv("MAIL_RECEIVER")
    if not mail_receiver:
        raise HTTPException(status_code=500, detail="Receptor de correo no configurado.")
    
    message = MessageSchema(
        subject="New message from my portfolio",
        recipients=[mail_receiver],
        body=f"Name: {form.name}\nEmail: {form.email}\nMessage:\n{form.message}",
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Gracias por contactarme, te responderé de inmediato."}
