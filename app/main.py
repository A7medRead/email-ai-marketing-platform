from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.features.analytics.api import router as dashboard_router
from app.features.email_generation.api import router as email_router
from app.features.templates.api import router as template_router
from app.features.users.api import router as user_router
from app.features.offers.api import router as offers_router
from app.features.responders.api import router as responders_router

from app.features.sender_accounts.api import router as sender_account_router
from app.features.contacts.api import router as contact_router
from app.features.contact_lists.api import router as contact_list_router
from app.features.campaigns.api import router as campaign_router
from app.features.tracking.api import router as tracking_router
from app.features.tracking.unsubscribe_api import router as unsubscribe_router

import app.features.model_registry  # noqa: F401 - register SQLAlchemy relationships

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
app.include_router(offers_router)
app.include_router(responders_router)

app.include_router(sender_account_router)
app.include_router(contact_router)
app.include_router(contact_list_router)
app.include_router(campaign_router)
app.include_router(tracking_router)
app.include_router(unsubscribe_router)


@app.get("/")
def home():
    return {
        "status": "Running"
    }
