import pytest
from genie_ai_service import classify_user_intent, GenieAIService
from crud_chat import get_user_conversations, delete_conversation_by_session, record_chat_message, get_chat_history
from language_detector import language_detector
from database import SessionLocal

def test_classify_user_intent():
    assert classify_user_intent("Hi") == "casual_greeting"
    assert classify_user_intent("Hello!") == "casual_greeting"
    assert classify_user_intent("హాయ్") == "casual_greeting"
    assert classify_user_intent("How are you?") == "casual_status"
    assert classify_user_intent("Ela unnavu?") == "casual_status"
    assert classify_user_intent("Thank you") == "casual_thanks"
    assert classify_user_intent("Dhanyavadalu") == "casual_thanks"
    assert classify_user_intent("Who are you?") == "casual_identity"
    assert classify_user_intent("I want to gain weight") == "health_goal_gain"
    assert classify_user_intent("Weight loss meal plan") == "health_goal_loss"
    assert classify_user_intent("Which foods contain iron?") == "nutrition_question"
    assert classify_user_intent("Hair health foods") == "nutrition_question"

def test_casual_intent_returns_no_food_cards():
    db = SessionLocal()
    try:
        resp = GenieAIService.generate_friendly_response(
            db=db,
            query="Hi",
            preferred_language="en"
        )
        assert resp.intent == "casual_greeting"
        assert len(resp.recommended_foods) == 0
        assert "|" not in resp.summary
        assert "Hi" in resp.summary or "Hello" in resp.summary or "Hey" in resp.summary
    finally:
        db.close()

def test_english_query_with_regional_profile_fallback():
    lang, conf, _ = language_detector.detect_language("Suggest healthy breakfast", fallback_lang="te")
    assert lang == "en"
    assert conf >= 0.9

def test_chat_history_privacy_isolation():
    db = SessionLocal()
    try:
        # Unauthenticated call without session_id must never dump other users' records
        rows = get_chat_history(db, user_id=None, session_id=None)
        assert rows == []
    finally:
        db.close()

def test_nutrition_intent_returns_food_cards():
    db = SessionLocal()
    try:
        resp = GenieAIService.generate_friendly_response(
            db=db,
            query="Which foods contain iron?",
            preferred_language="en"
        )
        assert len(resp.recommended_foods) > 0
        assert resp.intent == "iron_rich"
    finally:
        db.close()


def test_openrouter_build_messages_openai_format():
    from openrouter_service import GenieOpenRouterService

    svc = GenieOpenRouterService()
    messages = svc.build_messages(
        query="Suggest iron-rich foods",
        user_name="Asha",
        detected_language="en",
        health_goal="energy",
        chat_history=[
            {"sender": "user", "text": "Hi"},
            {"sender": "genie", "text": "Hello! How can I help?"},
        ],
        rag_context=[
            {
                "name": "Spinach (Palak)",
                "calories_kcal": 23,
                "protein_g": 2.9,
                "carbs_g": 3.6,
                "fat_g": 0.4,
                "fiber_g": 2.2,
                "estimated_price_inr": 20,
                "serving_size": "100g",
            }
        ],
        intent="iron_rich",
    )

    assert messages[0]["role"] == "system"
    assert "Asha" in messages[0]["content"]
    assert "Spinach (Palak)" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "Hi"}
    assert messages[2] == {"role": "assistant", "content": "Hello! How can I help?"}
    assert messages[3] == {"role": "user", "content": "Suggest iron-rich foods"}


def test_openrouter_health_unconfigured():
    from openrouter_service import GenieOpenRouterService

    svc = GenieOpenRouterService()
    svc.api_key = ""
    res = svc.test_health()
    assert res["status"] == "unconfigured"
    assert res["healthy"] is False
    assert res["provider"] == "openrouter"


def test_openrouter_error_handling_and_reasoning_retry(monkeypatch):
    import json as _json
    import httpx
    from openrouter_service import GenieOpenRouterService

    class FakeStreamResponse:
        def __init__(self, status_code, payload=None):
            self.status_code = status_code
            self._payload = payload or {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def iter_bytes(self):
            yield _json.dumps(self._payload).encode("utf-8")

    svc = GenieOpenRouterService()
    svc.api_key = "dummy-test-key"

    for status_code in (401, 429):
        monkeypatch.setattr(httpx.Client, "stream", lambda self, *a, _c=status_code, **kw: FakeStreamResponse(_c))
        assert svc.generate_response_sync(query="Suggest breakfast", timeout=2.0) is None

    def raise_timeout(self, *args, **kwargs):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(httpx.Client, "stream", raise_timeout)
    assert svc.generate_response_sync(query="Suggest breakfast", timeout=2.0) is None

    calls = []

    def retry_without_reasoning(self, method, url, headers=None, json=None, **kwargs):
        calls.append(json)
        if len(calls) == 1:
            return FakeStreamResponse(400, {"error": "reasoning unsupported"})
        return FakeStreamResponse(200, {"choices": [{"message": {"content": "Oats and banana breakfast"}}]})

    monkeypatch.setattr(httpx.Client, "stream", retry_without_reasoning)
    reply = svc.generate_response_sync(query="Suggest breakfast", timeout=2.0)
    assert reply == "Oats and banana breakfast"
    assert "reasoning" in calls[0]
    assert "reasoning" not in calls[1]


def test_genie_ai_routes_to_openrouter(monkeypatch):
    import genie_ai_service as gai
    from openrouter_service import openrouter_service

    monkeypatch.setattr(gai.settings, "LLM_PROVIDER", "openrouter")
    monkeypatch.setattr(openrouter_service, "is_configured", lambda: True)
    monkeypatch.setattr(
        openrouter_service,
        "generate_response_sync",
        lambda **kwargs: "Mocked OpenRouter nutrition guidance",
    )

    out = GenieAIService._call_llm_provider(
        query="Healthy high protein vegetarian dinner",
        user_name="Ravi",
        detected_language="en",
    )
    assert out == "Mocked OpenRouter nutrition guidance"

