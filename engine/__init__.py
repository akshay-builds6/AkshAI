"""
AkshAI Engine Package
=====================

This package contains all internal engines used by AkshAI.

All engines are designed to work together through brain.py.

Project:
    AkshAI

Package:
    engine

Version:
    1.0
"""

# ============================================================
# PACKAGE INFORMATION
# ============================================================

ENGINE_PACKAGE_NAME = "AkshAI Engine Package"
ENGINE_PACKAGE_VERSION = "1.0"
ENGINE_PACKAGE_READY = True


# ============================================================
# ENGINE REGISTRY
# ============================================================
#
# We keep the registry here so Brain can later know which
# engines are available.
#
# The actual engine modules will be added one by one.
#

AVAILABLE_ENGINES = [
    "calculator_engine",
    "command_engine",
    "context_engine",
    "conversation_engine",
    "formatter_engine",
    "intent_engine",
    "internet_engine",
    "knowledge_engine",
    "memory_engine",
    "notes_engine",
    "profile_engine",
    "reply_engine",
    "response_engine",
    "response_formatter",
    "time_engine",
    "weather_engine",
    "web_engine",
    "ai_engine",
]


# ============================================================
# PACKAGE HELPERS
# ============================================================

def get_engine_count() -> int:
    """Return the number of planned AkshAI engines."""
    return len(AVAILABLE_ENGINES)


def get_available_engines():
    """Return a copy of the engine registry."""
    return AVAILABLE_ENGINES.copy()


def is_engine_planned(engine_name: str) -> bool:
    """Check whether an engine is part of AkshAI's architecture."""

    if not isinstance(engine_name, str):
        return False

    return engine_name.strip().lower() in AVAILABLE_ENGINES


# ============================================================
# PACKAGE STATUS
# ============================================================

def get_package_status() -> dict:
    """Return package information for diagnostics."""

    return {
        "name": ENGINE_PACKAGE_NAME,
        "version": ENGINE_PACKAGE_VERSION,
        "ready": ENGINE_PACKAGE_READY,
        "planned_engines": get_engine_count(),
        "engines": get_available_engines(),
    }


# ============================================================
# SELF TEST
# ============================================================

def run_package_test() -> bool:
    """Test the engine package foundation."""

    print("=" * 65)
    print("AkshAI Engine Package v1.0")
    print("=" * 65)

    print(f"Package: {ENGINE_PACKAGE_NAME}")
    print(f"Version: {ENGINE_PACKAGE_VERSION}")
    print(f"Ready: {ENGINE_PACKAGE_READY}")
    print(f"Planned engines: {get_engine_count()}")

    print("\nEngine registry:")

    for index, engine in enumerate(
        AVAILABLE_ENGINES,
        start=1
    ):
        print(f"{index:02d}. {engine}")

    print("\nTesting helpers...")

    assert get_engine_count() == len(AVAILABLE_ENGINES)
    assert is_engine_planned("calculator_engine")
    assert is_engine_planned("weather_engine")
    assert is_engine_planned("ai_engine")
    assert not is_engine_planned("unknown_engine")

    status = get_package_status()

    assert status["ready"] is True
    assert status["planned_engines"] == len(
        AVAILABLE_ENGINES
    )

    print("✅ Package registry working")
    print("✅ Package helpers working")
    print("✅ Package status working")

    print("\nENGINE PACKAGE TEST PASSED ✅")
    print("=" * 65)

    return True


# ============================================================
# RUN ONLY WHEN FILE IS EXECUTED DIRECTLY
# ============================================================

if __name__ == "__main__":
    run_package_test()