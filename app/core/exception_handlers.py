from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.campaign import (
    ContactListNotFound,
    ContactListEmpty,
)

from app.core.exceptions.sender_account import (
    SenderAccountNotFound,
    SenderAccountNotVerified,
)


async def sender_account_not_found_handler(
    request: Request,
    exc: SenderAccountNotFound,
):
    return JSONResponse(
        status_code=404,
        content={
            "error": "sender_account_not_found",
            "message": "Sender account not found.",
        },
    )


async def sender_account_not_verified_handler(
    request: Request,
    exc: SenderAccountNotVerified,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "sender_account_not_verified",
            "message": "Sender account is not verified.",
        },
    )


async def contact_list_not_found_handler(
    request: Request,
    exc: ContactListNotFound,
):
    return JSONResponse(
        status_code=404,
        content={
            "error": "contact_list_not_found",
            "message": "Contact list not found.",
        },
    )


async def contact_list_empty_handler(
    request: Request,
    exc: ContactListEmpty,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "contact_list_empty",
            "message": "Contact list is empty.",
        },
    )
