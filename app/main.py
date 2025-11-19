from fastapi import FastAPI, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas import ContactForm
from app.models import Contact, Base
from app.database import engine, SessionLocal
from app.auth import router as auth_router
from app.recaptcha import verify_recaptcha
from app.sender import send_brevo_email
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
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


@app.post("/contact")
@limiter.limit("3/minute")
async def send_contact(
    request: Request,
    form: ContactForm,
    db: Session = Depends(get_db),
    recaptcha_token: str = Header(...)
):
    # 1. reCAPTCHA
    if not await verify_recaptcha(recaptcha_token):
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed.")

    # 2. Save to DB
    contact = Contact(name=form.name, email=form.email, message=form.message)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    # 3. Send email with Brevo API
    await send_brevo_email(
        subject="New message from my portfolio",
        content=f"Name: {form.name}\nEmail: {form.email}\nMessage:\n{form.message}"
    )

    return {"message": "Gracias por contactarme, te responderé de inmediato."}
