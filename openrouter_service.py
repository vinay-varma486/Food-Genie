"""
Genie OpenRouter AI Service
Connects FoodGenie's Genie chatbot to OpenRouter using its OpenAI-compatible
Chat Completions API (`POST {OPENROUTER_BASE_URL}/chat/completions`).
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
import httpx
from config import settings
from genie_agent_config import GENIE_SYSTEM_INSTRUCTION

logger = logging.getLogger("genie_openrouter")

LANG_NAMES = {
    "en": "English",
    "te": "Telugu (తెలుగు) — respond in pure Telugu script only (do not mix Kannada or other scripts)",
    "hi": "Hindi (हिन्दी) — respond in pure Devanagari Hindi script (or Hinglish if user wrote Hinglish)",
    "ta": "Tamil (தமிழ்) — respond in pure Tamil script",
    "kn": "Kannada (ಕನ್ನಡ) — respond in pure Kannada script",
    "ml": "Malayalam (മലയാളം) — respond in pure Malayalam script",
}


class GenieOpenRouterService:
    def __init__(self):
        self.api_key = (settings.OPENROUTER_API_KEY or "").strip()
        self.base_url = (settings.OPENROUTER_BASE_URL or "https://openrouter.ai/api/v1").rstrip("/")
        self.model = (settings.OPENROUTER_MODEL or "nvidia/nemotron-3.5-super-vl:free").strip()

    def is_configured(self) -> bool:
        return bool(self.api_key and "your-" not in self.api_key.lower())

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "FoodGenie",
        }

    @staticmethod
    def _extract_content(data: Dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = [
                p.get("text", "")
                for p in content
                if isinstance(p, dict) and p.get("type") == "text"
            ]
            return "".join(parts).strip()
        return ""

    def build_messages(
        self,
        query: str,
        user_name: str = "Friend",
        detected_language: str = "en",
        health_goal: Optional[str] = None,
        dietary_preference: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        profile_summary: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[List[Dict[str, Any]]] = None,
        restrictions_context: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        lang_desc = LANG_NAMES.get(detected_language, detected_language)
        profile_parts = [f"User Name: {user_name}", f"Target Response Language: {lang_desc}"]
        if health_goal:
            profile_parts.append(f"Health Goal: {health_goal}")
        if dietary_preference:
            profile_parts.append(f"Dietary Preference: {dietary_preference}")
        if allergies:
            profile_parts.append(f"Known Allergies: {', '.join(allergies)}")
        if profile_summary:
            profile_parts.append(profile_summary)
        if intent:
            profile_parts.append(f"Detected Intent: {intent}")

        profile_text = " | ".join(profile_parts)

        nutrition_text = ""
        if rag_context:
            nutrition_items = []
            for item in rag_context[:10]:
                name = item.get("name", "")
                name_reg = item.get(f"name_{detected_language}") or item.get("name_te") or ""
                cal = item.get("calories_kcal", 0)
                prot = item.get("protein_g", 0)
                carbs = item.get("carbs_g", 0)
                fat = item.get("fat_g", 0)
                fiber = item.get("fiber_g", 0)
                price = item.get("estimated_price_inr", 15)
                portion = item.get("serving_size", "1 serving (100g)")
                benefits = item.get("benefit", "")
                prep = item.get("how_to_consume") or item.get("preparation_methods") or ""
                vits = ", ".join(item.get("vitamins_summary", []))
                mins = ", ".join(item.get("minerals_summary", []))
                nutrition_items.append(
                    f"- {name}"
                    + (f" ({name_reg})" if name_reg and name_reg != name else "")
                    + f": Serving {portion} | Est. Price: ₹{price:.0f} (estimated) | "
                    + f"{cal} kcal, {prot}g protein, {carbs}g carbs, {fat}g fat, {fiber}g fiber"
                    + (f" | Vitamins: {vits}" if vits else "")
                    + (f" | Minerals: {mins}" if mins else "")
                    + (f" | Benefits: {benefits}" if benefits else "")
                    + (f" | Prep: {prep}" if prep else "")
                )
            nutrition_text = (
                "\nVERIFIED NUTRITION DATABASE CONTEXT (ICMR-NIN / USDA — do NOT invent exact figures outside this or verified ranges; label estimates clearly):\n"
                + "\n".join(nutrition_items)
            )

        restriction_text = ""
        if restrictions_context:
            r_lines = []
            for r in restrictions_context[:6]:
                alts = ", ".join(r.get("safe_alternatives", [])[:3])
                r_lines.append(
                    f"- Limit/Avoid: {r.get('food_name')} ({r.get('category')}) — Why: {r.get('reason')}"
                    + (f" | Alternatives: {alts}" if alts else "")
                )
            restriction_text = "\nDIETARY SAFETY & RESTRICTIONS CONTEXT:\n" + "\n".join(r_lines)

        system_prompt = (
            f"{GENIE_SYSTEM_INSTRUCTION}\n\n"
            f"CURRENT USER CONTEXT:\n{profile_text}{nutrition_text}{restriction_text}"
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        if chat_history:
            for turn in chat_history[-10:]:
                role = "user" if turn.get("sender") == "user" else "assistant"
                text = (turn.get("text") or "").strip()
                if not text:
                    continue
                if len(messages) > 1 and messages[-1]["role"] == role:
                    messages[-1]["content"] += f"\n{text}"
                else:
                    messages.append({"role": role, "content": text})

        if len(messages) > 1 and messages[-1]["role"] == "user":
            messages[-1]["content"] += f"\n{query}"
        else:
            messages.append({"role": "user", "content": query})

        return messages

    def _build_payload(self, messages: List[Dict[str, str]], include_reasoning: bool = True, max_tokens: int = 900) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.65,
            "top_p": 0.9,
            "max_tokens": max_tokens,
        }
        if include_reasoning:
            payload["reasoning"] = {"effort": "low"}
        return payload

    def test_health(self) -> Dict[str, Any]:
        """
        Runs a live OpenAI-compatible chat completion ping against OpenRouter.
        Never exposes the API key in logs or responses.
        """
        if not self.is_configured():
            return {
                "status": "unconfigured",
                "healthy": False,
                "provider": "openrouter",
                "base_url": self.base_url,
                "model": self.model,
                "message": "OPENROUTER_API_KEY is not configured in environment.",
            }

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "Reply with 'Genie OpenRouter ready' in 5 words or less."}
            ],
            "reasoning": {"effort": "low"},
            "max_tokens": 180,
        }

        t0 = time.time()
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, headers=self._headers(), json=payload)
                latency_ms = round((time.time() - t0) * 1000, 1)
                if res.status_code == 200:
                    reply_text = self._extract_content(res.json())
                    return {
                        "status": "connected",
                        "healthy": True,
                        "provider": "openrouter",
                        "base_url": self.base_url,
                        "model": self.model,
                        "latency_ms": latency_ms,
                        "test_reply": reply_text[:100],
                    }
                return {
                    "status": "error",
                    "healthy": False,
                    "provider": "openrouter",
                    "base_url": self.base_url,
                    "model": self.model,
                    "http_status": res.status_code,
                    "latency_ms": latency_ms,
                    "message": f"OpenRouter API returned HTTP {res.status_code}.",
                }
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "healthy": False,
                "provider": "openrouter",
                "model": self.model,
                "message": "OpenRouter API request timed out.",
            }
        except Exception as e:
            return {
                "status": "connection_error",
                "healthy": False,
                "provider": "openrouter",
                "model": self.model,
                "message": f"Connection error: {type(e).__name__}",
            }

    def generate_response_sync(
        self,
        query: str,
        user_name: str = "Friend",
        detected_language: str = "en",
        health_goal: Optional[str] = None,
        dietary_preference: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        profile_summary: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[List[Dict[str, Any]]] = None,
        restrictions_context: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
        timeout: float = 20.0,
    ) -> Optional[str]:
        if not self.is_configured():
            return None

        messages = self.build_messages(
            query=query,
            user_name=user_name,
            detected_language=detected_language,
            health_goal=health_goal,
            dietary_preference=dietary_preference,
            allergies=allergies,
            profile_summary=profile_summary,
            chat_history=chat_history,
            rag_context=rag_context,
            restrictions_context=restrictions_context,
            intent=intent,
        )

        url = f"{self.base_url}/chat/completions"
        wall_deadline = time.monotonic() + float(timeout)
        req_timeout = httpx.Timeout(connect=5.0, read=min(10.0, float(timeout)), write=8.0, pool=5.0)

        for include_reasoning in (True, False):
            payload = self._build_payload(messages, include_reasoning=include_reasoning)
            try:
                with httpx.Client(timeout=req_timeout) as client:
                    with client.stream("POST", url, headers=self._headers(), json=payload) as res:
                        if res.status_code == 200:
                            chunks = []
                            for chunk in res.iter_bytes():
                                if time.monotonic() > wall_deadline:
                                    raise httpx.TimeoutException("Wall-clock deadline exceeded while reading OpenRouter response")
                                if chunk:
                                    chunks.append(chunk)
                            raw_body = b"".join(chunks).decode("utf-8", errors="replace").strip()
                            if not raw_body:
                                return None
                            text = self._extract_content(json.loads(raw_body))
                            if text:
                                return text
                            logger.warning(f"OpenRouter {self.model} returned empty content.")
                            return None
                        if res.status_code == 400 and include_reasoning:
                            logger.info("OpenRouter returned HTTP 400 with reasoning option; retrying without reasoning.")
                            continue
                        if res.status_code in (401, 403):
                            logger.warning(f"OpenRouter authentication/access rejected (HTTP {res.status_code}).")
                        elif res.status_code == 429:
                            logger.warning("OpenRouter rate limit reached (HTTP 429). Falling back safely.")
                        elif res.status_code == 402:
                            logger.warning("OpenRouter credits/quota exhausted (HTTP 402). Falling back safely.")
                        else:
                            logger.warning(f"OpenRouter returned HTTP {res.status_code}.")
                        return None
            except httpx.TimeoutException:
                logger.warning(f"OpenRouter request timed out after {timeout}s on model {self.model}.")
                return None
            except httpx.RequestError as e:
                logger.warning(f"OpenRouter network request failed ({type(e).__name__}).")
                return None
            except ValueError as e:
                logger.warning(f"OpenRouter returned invalid JSON ({e}).")
                return None
            except Exception as e:
                logger.warning(f"Unexpected OpenRouter error ({type(e).__name__}).")
                return None

        return None

    async def generate_response(
        self,
        query: str,
        user_name: str = "Friend",
        detected_language: str = "en",
        health_goal: Optional[str] = None,
        dietary_preference: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        profile_summary: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[List[Dict[str, Any]]] = None,
        restrictions_context: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
        timeout: float = 20.0,
    ) -> Optional[str]:
        if not self.is_configured():
            return None

        messages = self.build_messages(
            query=query,
            user_name=user_name,
            detected_language=detected_language,
            health_goal=health_goal,
            dietary_preference=dietary_preference,
            allergies=allergies,
            profile_summary=profile_summary,
            chat_history=chat_history,
            rag_context=rag_context,
            restrictions_context=restrictions_context,
            intent=intent,
        )

        url = f"{self.base_url}/chat/completions"

        for include_reasoning in (True, False):
            payload = self._build_payload(messages, include_reasoning=include_reasoning)
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    res = await client.post(url, headers=self._headers(), json=payload)
                    if res.status_code == 200:
                        text = self._extract_content(res.json())
                        if text:
                            return text
                        return None
                    if res.status_code == 400 and include_reasoning:
                        continue
                    logger.warning(f"OpenRouter async call returned HTTP {res.status_code}.")
                    return None
            except Exception as e:
                logger.warning(f"OpenRouter async error ({type(e).__name__}).")
                return None

        return None


openrouter_service = GenieOpenRouterService()

