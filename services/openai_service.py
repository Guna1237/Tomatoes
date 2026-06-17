import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st


DEFAULT_MODEL = "gpt-4.1-mini"
LOCAL_SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "openai.local.toml"


def _local_secret(name: str) -> str:
    if not LOCAL_SECRETS_PATH.exists():
        return ""
    try:
        text = LOCAL_SECRETS_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(rf"^\s*{re.escape(name)}\s*=\s*['\"]([^'\"]+)['\"]", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, "") or os.environ.get(name, "") or _local_secret(name) or default
    except Exception:
        return os.environ.get(name, "") or _local_secret(name) or default


def _extract_text(response: dict) -> str:
    if response.get("output_text"):
        return str(response["output_text"]).strip()

    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(str(content["text"]))
    return "\n".join(chunks).strip()


class AIStudyService:
    @staticmethod
    def is_configured() -> bool:
        return bool(_secret("OPENAI_API_KEY"))

    @staticmethod
    def model_name() -> str:
        return _secret("OPENAI_MODEL", DEFAULT_MODEL)

    @staticmethod
    def generate_resource_plan(goal: str, resources: list[dict], user: dict) -> str:
        api_key = _secret("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        resource_lines = []
        for res in resources[:18]:
            resource_lines.append(
                "- {title} ({course_code}, {category}, {file_type}) - {course_name}".format(
                    title=res.get("title", "Untitled"),
                    course_code=res.get("course_code", "General"),
                    category=res.get("category", "Resource"),
                    file_type=(res.get("file_type") or "file").upper(),
                    course_name=res.get("course_name", ""),
                )
            )

        prompt = f"""
Student: {user.get('name', 'Student')}
Goal: {goal}

Available campus resources:
{chr(10).join(resource_lines) if resource_lines else "- No resources uploaded yet."}

Create a practical study plan using only the available resource list where possible.
Include:
1. The best 3-6 resources to start with.
2. A short sequence for what to study first, second, and third.
3. One gap or missing material the student should look for.
4. A concise next action the student can do today.
Keep it specific, friendly, and under 220 words.
""".strip()

        payload = {
            "model": AIStudyService.model_name(),
            "input": [
                {
                    "role": "system",
                    "content": "You are a concise campus study assistant. Do not invent files that are not listed.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_output_tokens": 450,
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI request failed ({exc.code}): {body[:240]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach OpenAI: {exc.reason}") from exc

        text = _extract_text(data)
        if not text:
            raise RuntimeError("OpenAI returned an empty response.")
        return text
