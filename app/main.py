from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.api.dashboard import router as dashboard_router
from app.api.email import router as email_router
from app.api.template import router as template_router
from app.api.user import router as user_router

from app.api.marketing.sender_account import router as sender_account_router
from app.api.marketing.contact import router as contact_router
from app.api.marketing.contact_list import router as contact_list_router
from app.api.marketing.campaign import router as campaign_router
from app.api.marketing.tracking import router as tracking_router
from app.api.marketing.unsubscribe import router as unsubscribe_router

from app.models.email import Email
from app.models.template import Template
from app.models.user import User

from app.models.marketing.sender_account import SenderAccount
from app.models.marketing.contact import Contact
from app.models.marketing.contact_list import ContactList
from app.models.marketing.contact_list_contact import ContactListContact
from app.models.marketing.campaign import Campaign
from app.models.marketing.email_delivery import EmailDelivery

from app.services.marketing.scheduler import start_scheduler


app = FastAPI(
    title="Email AI Platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs(
    "uploads/avatars",
    exist_ok=True,
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


app.include_router(email_router)
app.include_router(user_router)
app.include_router(dashboard_router)
app.include_router(template_router)

app.include_router(sender_account_router)
app.include_router(contact_router)
app.include_router(contact_list_router)
app.include_router(campaign_router)
app.include_router(tracking_router)
app.include_router(unsubscribe_router)


@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.get("/")
def home():
    return {
        "status": "Running"
    }
