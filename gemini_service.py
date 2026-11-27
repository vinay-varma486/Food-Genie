"""
Genie Gemini Service
Handles interaction with Google's Gemini API (`v1beta/models/...:generateContent`)
for natural conversational intelligence, intent awareness, multilingual replies,
and grounded wholefood/diet recommendations.
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import httpx
from config import settings
from genie_agent_config import GENIE_SYSTEM_INSTRUCTION

logger = logging.getLogger("genie_gemini")


class GenieGeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        # Verified active Gemini API models (fallback cascade handles transient 503/429 spikes)
        self.model_candidates = [
            "gemini-3.5-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-3.5-flash",
            "gemini-2.5-flash-lite",
        ]
        self.primary_model = self.model_candidates[0]
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @staticmethod
    def _extract_text(data: Dict[str, Any]) -> str:
        """Extracts non-thought text parts from a Gemini generateContent JSON payload."""
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        texts = []
        for part in parts:
            if isinstance(part, dict) and not part.get("thought") and "text" in part:
                texts.append(part["text"])
        return "".join(texts).strip()

    def _headers(self) -> Dict[str, str]:
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def test_health(self) -> Dict[str, Any]:
        """
        Runs a live generation test against Gemini API and returns health status with latency.
        Never exposes the API key in the response.
        """
        if not self.api_key or "your-" in self.api_key:
            return {
                "status": "unconfigured",
                "healthy": False,
                "message": "GEMINI_API_KEY is not configured in environment.",
            }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Reply with 'Genie is healthy and ready' in 6 words or less."}],
                }
            ]
        }

        last_err = None
        for model in self.model_candidates[:3]:
            url = f"{self.base_url}/{model}:generateContent"
            t0 = time.time()
            try:
                with httpx.Client(timeout=8.0) as client:
                    res = client.post(url, headers=self._headers(), json=payload)
                    latency_ms = round((time.time() - t0) * 1000, 1)
                    if res.status_code == 200:
                        reply_text = self._extract_text(res.json())
                        return {
                            "status": "connected",
                            "healthy": True,
                            "model": model,
                            "latency_ms": latency_ms,
                            "test_reply": reply_text[:80],
                        }
                    last_err = f"HTTP {res.status_code} on {model}"
            except httpx.TimeoutException:
                last_err = f"Timeout on {model}"
            except Exception as e:
                last_err = str(e)

        return {
            "status": "unavailable",
            "healthy": False,
            "message": last_err or "Gemini API unavailable.",
        }

    def build_prompt_context(
        self,
        query: str,
        user_name: str,
        detected_language: str,
        health_goal: Optional[str] = None,
        dietary_preference: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        profile_summary: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        rag_context: Optional[List[Dict[str, Any]]] = None,
        restrictions_context: Optional[List[Dict[str, Any]]] = None,
        intent: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Builds valid alternating-role contents and grounded systemInstruction for Gemini API.
        """
        lang_labels = {
            "en": "English",
            "te": "Telugu (తెలుగు) — respond in pure Telugu script only (do not mix Kannada or other scripts)",
            "hi": "Hindi (हिन्दी) — respond in pure Devanagari Hindi script (or Hinglish if user wrote Hinglish)",
            "ta": "Tamil (தமிழ்) — respond in pure Tamil script",
            "kn": "Kannada (ಕನ್ನಡ) — respond in pure Kannada script",
            "ml": "Malayalam (മലയാളം) — respond in pure Malayalam script",
        }
        lang_desc = lang_labels.get(detected_language, detected_language)
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
                    f"- {name}" + (f" ({name_reg})" if name_reg and name_reg != name else "")
                    + f": Serving {portion} | Est. Price: ₹{price:.0f} (estimated) | "
                    + f"{cal} kcal, {prot}g protein, {carbs}g carbs, {fat}g fat, {fiber}g fiber"
                    + (f" | Vitamins: {vits}" if vits else "")
                    + (f" | Minerals: {mins}" if mins else "")
                    + (f" | Benefits: {benefits}" if benefits else "")
                    + (f" | Prep: {prep}" if prep else "")
                )
            nutrition_text = "\nVERIFIED NUTRITION DATABASE CONTEXT (ICMR-NIN / USDA — do NOT invent exact figures outside this or verified ranges; label estimates clearly):\n" + "\n".join(nutrition_items)

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

        full_system = f"{GENIE_SYSTEM_INSTRUCTION}\n\nCURRENT USER CONTEXT:\n{profile_text}{nutrition_text}{restriction_text}"

        # Build clean alternating user/model conversation history
        messages: List[Dict[str, Any]] = []
        if chat_history:
            for turn in chat_history[-10:]:
                role = "user" if turn.get("sender") == "user" else "model"
                text = (turn.get("text") or "").strip()
                if not text:
                    continue
                if messages and messages[-1]["role"] == role:
                    messages[-1]["parts"][0]["text"] += f"\n{text}"
                else:
                    messages.append({"role": role, "parts": [{"text": text}]})

        # Gemini requires first turn in contents to be 'user'
        while messages and messages[0]["role"] != "user":
            messages.pop(0)

        if messages and messages[-1]["role"] == "user":
            messages[-1]["parts"][0]["text"] += f"\n{query}"
        else:
            messages.append({"role": "user", "parts": [{"text": query}]})

        return messages, full_system

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
    ) -> Optional[str]:
        if not self.api_key or "your-" in self.api_key:
            return None

        contents, system_instruction = self.build_prompt_context(
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

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.65,
                "topP": 0.9,
                "maxOutputTokens": 1200,
            },
        }

        for model in self.model_candidates:
            url = f"{self.base_url}/{model}:generateContent"
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    res = await client.post(url, headers=self._headers(), json=payload)
                    if res.status_code == 200:
                        text_reply = self._extract_text(res.json())
                        if text_reply:
                            return text_reply
                    else:
                        logger.warning(f"Gemini {model} returned HTTP {res.status_code}")
            except Exception as e:
                logger.warning(f"Gemini async call error on {model}: {e}")

        return None

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
        timeout: float = 12.0,
    ) -> Optional[str]:
        if not self.api_key or "your-" in self.api_key:
            return None

        contents, system_instruction = self.build_prompt_context(
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

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.65,
                "topP": 0.9,
                "maxOutputTokens": 1200,
            },
        }

        for model in self.model_candidates:
            url = f"{self.base_url}/{model}:generateContent"
            try:
                with httpx.Client(timeout=timeout) as client:
                    res = client.post(url, headers=self._headers(), json=payload)
                    if res.status_code == 200:
                        text_reply = self._extract_text(res.json())
                        if text_reply:
                            return text_reply
                    else:
                        logger.warning(f"Gemini sync {model} returned HTTP {res.status_code}")
            except Exception as e:
                logger.warning(f"Gemini sync error on {model}: {e}")

        return None


gemini_service = GenieGeminiService()
