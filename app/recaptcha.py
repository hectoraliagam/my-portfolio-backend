# app/recaptcha.py
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def verify_recaptcha(recaptcha_token: str) -> bool:
    secret = os.getenv("RECAPTCHA_SECRET_KEY")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": recaptcha_token}
        )

    result = response.json()
    print("reCAPTCHA verify response:", result)

    return result.get("success", False) and result.get("score", 0) >= 0.5
