import json

from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.core.config import ANTHROPIC_API_KEY, MODEL
from app.prompts.email_prompt import SYSTEM_PROMPT
from app.repositories.email_repository import save_email


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def create_email_content(data):

    user_prompt = f"""
Purpose:
{data.purpose}

Description:
{data.description}

Tone:
{data.tone}

Language:
{data.language}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=1,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    text = response.content[0].text

    return json.loads(text)


def generate_email(
    db: Session,
    user_id: int,
    data,
):
    result = create_email_content(data)

    save_email(
        db=db,
        user_id=user_id,
        purpose=data.purpose,
        description=data.description,
        tone=data.tone,
        language=data.language,
        subject=result["subject"],
        body=result["body"],
    )

    return result
