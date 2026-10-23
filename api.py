from flask import Flask, request, jsonify
import logging

from engine.brain import Brain
from engine.knowledge_engine import KnowledgeEngine
from engine.web_engine import WebEngine
from engine.ai_engine import AIEngine

from engine.action_engine import ActionEngine
from engine.calculator_engine import CalculatorEngine
from engine.command_engine import CommandEngine
from engine.context_engine import ContextEngine
from engine.conversation_engine import ConversationEngine
from engine.formatter_engine import FormatterEngine
from engine.intent_engine import IntentEngine
from engine.memory_engine import MemoryEngine
from engine.notes_engine import NotesEngine
from engine.profile_engine import ProfileEngine
from engine.reply_engine import ReplyEngine
from engine.response_engine import ResponseEngine
from engine.time_engine import TimeEngine
from engine.weather_engine import WeatherEngine

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def build_engines():
    """Initialize available engine objects without crashing the API."""
    classes = {
        "action_engine": ActionEngine,
        "calculator_engine": CalculatorEngine,
        "command_engine": CommandEngine,
        "context_engine": ContextEngine,
        "conversation_engine": ConversationEngine,
        "formatter_engine": FormatterEngine,
        "intent_engine": IntentEngine,
        "knowledge_engine": KnowledgeEngine,
        "memory_engine": MemoryEngine,
        "notes_engine": NotesEngine,
        "profile_engine": ProfileEngine,
        "reply_engine": ReplyEngine,
        "response_engine": ResponseEngine,
        "time_engine": TimeEngine,
        "weather_engine": WeatherEngine,
        "web_engine": WebEngine,
        "ai_engine": AIEngine,
    }

    engines = {}
    failures = {}

    for name, engine_class in classes.items():
        try:
            engines[name] = engine_class()
        except Exception as exc:
            failures[name] = str(exc)
            app.logger.exception("Could not initialize %s", name)

    return engines, failures


ENGINES, ENGINE_FAILURES = build_engines()
brain = Brain(engines=ENGINES)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "AkshAI API",
        "brain": "connected",
        "brain_status": brain.status(),
        "configured_engines": sorted(ENGINES.keys()),
        "engine_count": len(ENGINES),
        "engine_initialization_failures": ENGINE_FAILURES,
    })


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        user_name = str(data.get("user_name", "Akshay")).strip()

        if not message:
            return jsonify({
                "success": False,
                "answer": "",
                "error": "Message is empty",
            }), 400

        brain.user_name = user_name or "Akshay"
        result = brain.process(message)

        if hasattr(result, "to_dict"):
            payload = result.to_dict()
        elif isinstance(result, dict):
            payload = result.copy()
        else:
            payload = {
                "success": bool(result),
                "answer": str(result) if result is not None else "",
            }

        payload["user_name"] = brain.user_name
        return jsonify(payload)

    except Exception as exc:
        app.logger.exception("AkshAI chat request failed")
        return jsonify({
            "success": False,
            "answer": "",
            "error": str(exc),
        }), 500


if __name__ == "__main__":
    print("AkshAI API starting...")
    print("Registered engines:", len(ENGINES))
    print("URL: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)