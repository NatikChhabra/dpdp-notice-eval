"""A small Gemini client: pacing for the free tier, retries, and clear errors.

Everything that calls a model goes through `LLM.generate`, so tests can swap in a fake.
"""

from __future__ import annotations

import os
import re
import time
from typing import Protocol

from pydantic import BaseModel


class LLMError(RuntimeError):
    pass


class QuotaExhausted(LLMError):
    """The daily free quota is used up. Runs stop cleanly and resume next time."""


class LLM(Protocol):
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: str | None = None,
        schema: type[BaseModel] | None = None,
        temperature: float | None = None,
    ) -> str: ...


def _is_gemma(model: str) -> bool:
    return model.startswith("gemma")


class GeminiLLM:
    """google-genai client. Needs GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment."""

    def __init__(self, client=None, min_interval: float | None = None, max_attempts: int = 6):
        from google import genai
        from google.genai import errors, types

        self._types, self._errors = types, errors
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if client is None and not key:
            raise LLMError("Set GEMINI_API_KEY to call Gemini.")
        self.client = client or genai.Client(api_key=key, http_options=types.HttpOptions(timeout=120_000))
        # Free tier allows roughly 10 requests per minute per model; stay under it by default.
        self.min_interval = float(os.environ.get("DPDP_MIN_INTERVAL", 6.5)) if min_interval is None else min_interval
        self.max_attempts = max_attempts
        self._last_call: dict[str, float] = {}

    def _pace(self, model: str) -> None:
        # Gemma's free tier allows only 16K input tokens a minute, so space its calls out more.
        interval = max(self.min_interval, 15.0) if _is_gemma(model) and self.min_interval > 0 else self.min_interval
        wait = self._last_call.get(model, 0.0) + interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_call[model] = time.monotonic()

    def _config(self, model: str, system, schema, temperature):
        t = self._types
        kw: dict = {}
        if temperature is not None:
            kw["temperature"] = temperature
        if schema is not None:
            kw["response_mime_type"] = "application/json"
            kw["response_schema"] = schema
        if system and not _is_gemma(model):  # Gemma models on the API don't take a system instruction
            kw["system_instruction"] = system
        return t.GenerateContentConfig(**kw)

    def generate(self, model, prompt, *, system=None, schema=None, temperature=None) -> str:
        if system and _is_gemma(model):
            prompt = f"{system}\n\n{prompt}"
        config = self._config(model, system, schema, temperature)
        delay = 10.0
        for attempt in range(1, self.max_attempts + 1):
            self._pace(model)
            try:
                resp = self.client.models.generate_content(model=model, contents=prompt, config=config)
            except self._errors.APIError as e:
                msg = str(e)
                if e.code == 429 and re.search(r"per ?day|PerDay|daily", msg, re.I):
                    raise QuotaExhausted(f"{model}: daily quota used up") from e
                if e.code in (429, 500, 502, 503, 504) and attempt < self.max_attempts:
                    m = re.search(r"retry in ([\d.]+)s", msg)
                    time.sleep(float(m.group(1)) + 1 if m else delay)
                    delay = min(delay * 2, 120)
                    continue
                raise LLMError(f"{model}: {e.code} {getattr(e, 'message', '') or msg[:200]}") from e
            except Exception as e:  # network errors and timeouts
                if attempt < self.max_attempts:
                    time.sleep(delay)
                    delay = min(delay * 2, 120)
                    continue
                raise LLMError(f"{model}: {type(e).__name__}: {e}") from e
            text = resp.text or ""
            if not text.strip():
                reason = ""
                try:
                    reason = str(resp.candidates[0].finish_reason)
                except Exception:
                    pass
                if attempt < self.max_attempts:
                    continue
                raise LLMError(f"{model}: empty response {reason}")
            return text
        raise LLMError(f"{model}: gave up after {self.max_attempts} attempts")

    def list_models(self) -> list[str]:
        out = []
        for m in self.client.models.list():
            actions = getattr(m, "supported_actions", None) or []
            if "generateContent" in actions:
                out.append(m.name.removeprefix("models/"))
        return sorted(out)
