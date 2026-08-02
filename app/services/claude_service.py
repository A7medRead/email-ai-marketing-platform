import json

from anthropic import Anthropic
from sqlalchemy.orm import Session

from app.core.config import ANTHROPIC_API_KEY, MODEL
from app.prompts.email_prompt import SYSTEM_PROMPT
from app.repositories.email_repository import save_email



client = Anthropic(api_key=ANTHROPIC_API_KEY)

AI_ACTIONS = {
    "generate": "Generate a brand-new marketing email.",
    "improve": "Improve the email while keeping the same intent.",
    "rewrite": "Rewrite the email in a different way while preserving the meaning.",
    "shorten": "Rewrite the email to be shorter and more concise.",
    "lengthen": "Expand the email with more useful details.",
    "professional": "Rewrite the email using a professional business tone.",
    "friendly": "Rewrite the email using a warm and friendly tone.",
}



def parse_claude_json(text):
    import json
    import re

    text = text.strip()

    if "```json" in text:
        text = text.replace("```json", "")
        text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end+1]

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        subject_match = re.search(
            r'"subject"\s*:\s*"([^"]*)"',
            text,
            re.DOTALL
        )

        body_match = re.search(
            r'"body"\s*:\s*"(.*)',
            text,
            re.DOTALL
        )

        if subject_match and body_match:

            body = body_match.group(1)

            body = body.rsplit('"', 1)[0]

            return {
                "subject": subject_match.group(1),
                "body": body
            }

        raise

def create_email_content(
    data,
    action: str = "generate",
):

    instruction = AI_ACTIONS.get(
        action,
        AI_ACTIONS["generate"],
    )

    user_prompt = f"""
Instruction:
{instruction}

Purpose:
{data.purpose}

Description:
{data.description}

Tone:
{data.tone}

Language:
{data.language}

Return ONLY valid JSON.

Important:
- The body HTML must be a single-line string.
- Escape all quotes correctly.
- Do not add newline characters inside JSON strings.


The email body must be a complete HTML email design.

Requirements:
- Return HTML only inside the "body" field.
- Use inline CSS styles.
- Make it mobile friendly.
- Avoid double quotes inside HTML attributes. Use single quotes.
- Escape all JSON characters correctly.
- Create a professional marketing email layout.
- Include:
  - headline section
  - short marketing copy
  - offer/highlight section when relevant
  - CTA button
  - closing/signature
- Do not use Markdown.
- Do not wrap HTML in code blocks.

Return this exact JSON format:

{{
  "subject": "Email subject",
  "body": "<html email content>"
}}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        temperature=1,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    text = ""

    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    if not text:
        raise Exception("Claude returned no text content")

    return parse_claude_json(text)


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

def edit_email_content(data):
    instruction = AI_ACTIONS.get(
        data.action,
        AI_ACTIONS["improve"],
    )

    user_prompt = f"""
Instruction:
{instruction}

Subject:
{data.subject}

Body:
{data.body}

Return ONLY valid JSON in this format:

{{
    "subject": "...",
    "body": "..."
}}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        temperature=1,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    text = ""

    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    if not text:
        raise Exception("Claude returned no text content")

    return json.loads(text)

