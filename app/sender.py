# app/sender.py
import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

async def send_brevo_email(subject: str, content: str):
    api_key = os.getenv("BREVO_API_KEY")
    sender = os.getenv("MAIL_FROM")
    receiver = os.getenv("MAIL_RECEIVER")

    if not api_key or not sender or not receiver:
        raise HTTPException(status_code=500, detail="Email configuration incomplete.")

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"email": sender},
        "to": [{"email": receiver}],
        "subject": subject,
        "textContent": content
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)

    print("Brevo API response:", r.status_code, r.text)

    if r.status_code != 201:
        raise HTTPException(status_code=500, detail="No se pudo enviar el correo.")

    return True
