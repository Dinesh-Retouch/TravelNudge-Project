# Temporary test endpoint (for checking email setup)
from app.utils.email import send_email
from fastapi import APIRouter
from app.routers.auth import auth_router

@auth_router.get("/test-email")
def test_email():
    send_email(
        to="jagadeeshkadavakuti5@gmail.com",  # 🔹 Replace with your real email
        subject="Test Email from TravelNudge",
        body="<h2>This is a test email from your FastAPI app.</h2>"
    )
    return {"message": "Test email sent!"}
