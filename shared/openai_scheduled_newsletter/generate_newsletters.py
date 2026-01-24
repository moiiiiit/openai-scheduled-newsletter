import json
import os

from openai import OpenAI

from .logger import logger
from .send_email import send_email

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def load_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key


def load_prompts():
    prompts_json = os.environ.get("PROMPTS_JSON")
    if not prompts_json:
        raise ValueError("PROMPTS_JSON not found in environment variables")
    return json.loads(prompts_json)


def call_openai_api(api_key, model, prompt):
    try:
        client = OpenAI()
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            reasoning={"effort": "medium"},
            input=prompt,
        )
        return response.output_text
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return {"error": str(e)}


# This function generates a newsletter for a single prompt and sends email
def generate_newsletter_for_prompt(prompt_obj, sender_email, bcc_emails):
    api_key = load_api_key()
    model = prompt_obj["model"]
    prompt = prompt_obj["prompt"]
    logger.info(f"Generating newsletter for model={model}")
    try:
        result = call_openai_api(api_key, model, prompt)
    except Exception as e:
        logger.error(f"Error for model={model}: {e}")
        result = {"error": str(e)}
    if result and not (isinstance(result, dict) and "error" in result):
        subject = f"Newsletter for model: {model}"
        body = str(result)
        try:
            send_email(subject, body, sender_email, bcc_emails)
            logger.info(f"Newsletter sent for model={model}")
        except Exception as e:
            logger.error(f"Email send failed for model={model}: {e}")
    else:
        logger.error(f"Skipping email for model={model} due to error: {result}")


# Utility to get all prompts (for scheduler setup)
def get_all_prompts():
    return load_prompts()
