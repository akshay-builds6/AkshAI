# ========================================================
# AKSHAI REPLY ENGINE v1.0
# Natural • Polite • Attractive • Emotion-Aware
# ========================================================

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import random
import re


# ========================================================
# ENGINE CONFIG
# ========================================================

ENGINE_NAME = "AkshAI Reply Engine"
ENGINE_VERSION = "1.0"


# ========================================================
# RESULT MODEL
# ========================================================

@dataclass
class ReplyResult:

    success: bool

    query: str = ""

    answer: str = ""

    intent: str = ""

    emotion: str = ""

    language: str = ""

    error: str = ""

    error_type: str = ""

    source: str = "reply_engine"


# ========================================================
# TEXT HELPERS
# ========================================================

def clean_text(text: Any) -> str:

    if text is None:
        return ""

    text = str(text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        ).strip()

        lines.append(line)

    return "\n".join(lines).strip()


def normalize_text(text: Any) -> str:

    text = clean_text(text)

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ========================================================
# LANGUAGE DETECTION
# ========================================================

def detect_language(text: str) -> str:

    text = clean_text(text)

    if not text:
        return "unknown"

    has_devanagari = bool(
        re.search(
            r"[\u0900-\u097F]",
            text
        )
    )

    words = normalize_text(text).split()

    roman_hindi_words = {
        "hai",
        "ho",
        "haan",
        "nahi",
        "nahin",
        "kya",
        "kaise",
        "kaisa",
        "kyu",
        "kyun",
        "mujhe",
        "mera",
        "meri",
        "mere",
        "aap",
        "aapka",
        "aapki",
        "tum",
        "tumhara",
        "tumhari",
        "batao",
        "bata",
        "chahiye",
        "krna",
        "karna",
        "karo",
        "acha",
        "achha",
        "theek",
        "thik",
        "bhai",
        "yaar",
        "ya",
        "mein",
        "main",
        "se",
        "ke",
        "ka",
        "ki",
        "ko",
        "par",
        "aur",
        "lekin",
        "abhi",
        "kal",
        "aaj",
    }

    hindi_count = sum(
        1
        for word in words
        if word in roman_hindi_words
    )

    if has_devanagari:

        if hindi_count > 0:
            return "hinglish"

        return "hindi"

    if hindi_count >= 2:

        return "hinglish"

    return "english"


# ========================================================
# EMOTION DETECTION
# ========================================================

def detect_emotion(text: str) -> str:

    q = normalize_text(text)

    if not q:
        return "neutral"

    sad_words = {
        "sad",
        "sadness",
        "upset",
        "cry",
        "crying",
        "hurt",
        "pain",
        "dukhi",
        "udaas",
        "pareshan",
        "tension",
        "tensed",
        "rona",
        "ro",
        "bura",
        "akela",
        "lonely",
    }

    happy_words = {
        "happy",
        "happiness",
        "great",
        "awesome",
        "amazing",
        "nice",
        "good",
        "khush",
        "mast",
        "badhiya",
        "accha",
        "achha",
        "badiya",
    }

    angry_words = {
        "angry",
        "anger",
        "mad",
        "gussa",
        "ghussa",
        "irritated",
        "irritation",
    }

    worried_words = {
        "worried",
        "worry",
        "fear",
        "scared",
        "dar",
        "darr",
        "chinta",
        "fikar",
    }

    excited_words = {
        "excited",
        "exciting",
        "wow",
        "yay",
        "lets",
        "celebrate",
        "congrats",
        "congratulations",
    }

    if any(word in q for word in sad_words):
        return "sad"

    if any(word in q for word in angry_words):
        return "angry"

    if any(word in q for word in worried_words):
        return "worried"

    if any(word in q for word in excited_words):
        return "excited"

    if any(word in q for word in happy_words):
        return "happy"

    return "neutral"


# ========================================================
# INTENT DETECTION
# ========================================================

def detect_reply_intent(text: str) -> str:

    q = normalize_text(text)

    if not q:
        return "unknown"

    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
        "hiii",
        "namaste",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
    ]

    thanks = [
        "thank you",
        "thanks",
        "thank u",
        "thnx",
        "shukriya",
        "dhanyavaad",
    ]

    goodbye = [
        "bye",
        "goodbye",
        "see you",
        "see ya",
        "good night",
        "gn",
    ]

    acknowledgement = [
        "ok",
        "okay",
        "alright",
        "got it",
        "understood",
        "samajh gaya",
        "samajh gya",
        "theek hai",
        "thik hai",
        "acha",
        "achha",
    ]

    compliments = [
        "nice",
        "great",
        "awesome",
        "amazing",
        "good job",
        "well done",
        "badhiya",
        "badiya",
        "mast",
        "accha hai",
        "achha hai",
    ]

    if any(item in q for item in greetings):
        return "greeting"

    if any(item in q for item in thanks):
        return "thanks"

    if any(item in q for item in goodbye):
        return "goodbye"

    if any(item in q for item in acknowledgement):
        return "acknowledgement"

    if any(item in q for item in compliments):
        return "compliment"

    return "general"


# ========================================================
# REPLY ENGINE
# ========================================================

class ReplyEngine:

    def __init__(self):

        self.engine_name = ENGINE_NAME

        self.version = ENGINE_VERSION


    # ====================================================
    # GREETING REPLIES
    # ====================================================

    def _greeting_reply(
        self,
        language: str,
        emotion: str
    ) -> str:

        if language == "hindi":

            replies = [
                "🙏 नमस्ते! 😊 आप कैसे हैं?",
                "😊 नमस्ते! आपसे बात करके खुशी हुई। ❤️",
                "🌸 नमस्ते! बताइए, मैं आपकी किस तरह मदद कर सकता हूँ?",
            ]

        elif language == "hinglish":

            replies = [
                "🙏 Hey! 😊 Kaise ho? Batao, main aapki kis tarah help kar sakta hoon?",
                "😊 Hey! Aapse baat karke accha laga. ❤️ Batao, kya help chahiye?",
                "✨ Hello! Main ready hoon. Batao, aaj kya karna hai? 🚀",
            ]

        else:

            replies = [
                "👋 Hello! 😊 How are you doing?",
                "✨ Hey! It's great to hear from you. How can I help? 😊",
                "🤖 Hello! I'm ready to help. What would you like to do?",
            ]

        if emotion == "sad":

            return (
                "🫂 Hey! I'm here with you. ❤️\n\n"
                + random.choice(replies)
            )

        return random.choice(replies)


    # ====================================================
    # THANKS REPLIES
    # ====================================================

    def _thanks_reply(
        self,
        language: str
    ) -> str:

        if language == "hindi":

            return random.choice([
                "😊 आपका स्वागत है! ❤️",
                "🤗 कोई बात नहीं। मदद करके खुशी हुई!",
                "✨ हमेशा खुशी से! अगर कुछ और चाहिए तो बताइए।",
            ])

        if language == "hinglish":

            return random.choice([
                "😊 You're most welcome! ❤️",
                "🤗 Koi baat nahi! Help karke mujhe khushi hui.",
                "✨ Anytime! Agar aur kuch chahiye ho toh bata dena. 😊",
            ])

        return random.choice([
            "😊 You're very welcome! ❤️",
            "🤗 Anytime! Glad I could help.",
            "✨ My pleasure! Let me know if you need anything else.",
        ])


    # ====================================================
    # GOODBYE REPLIES
    # ====================================================

    def _goodbye_reply(
        self,
        language: str
    ) -> str:

        if language == "hindi":

            return random.choice([
                "👋 अलविदा! अपना ख्याल रखिए। ❤️",
                "😊 फिर मिलते हैं! आपका दिन अच्छा रहे। ✨",
                "🤗 ठीक है! अपना ध्यान रखिए और मुस्कुराते रहिए। ❤️",
            ])

        if language == "hinglish":

            return random.choice([
                "👋 Bye! Apna khayal rakhna. ❤️",
                "😊 Phir milte hain! Take care. ✨",
                "🤗 Okay! Dhyan rakhna aur haste rehna. ❤️",
            ])

        return random.choice([
            "👋 Goodbye! Take care. ❤️",
            "😊 See you soon! Have a great day. ✨",
            "🤗 Bye! Stay safe and keep smiling. ❤️",
        ])


    # ====================================================
    # ACKNOWLEDGEMENT
    # ====================================================

    def _acknowledgement_reply(
        self,
        language: str
    ) -> str:

        if language == "hindi":

            return random.choice([
                "👍 ठीक है! समझ गया। 😊",
                "✅ बिल्कुल! समझ गया।",
                "😊 ठीक है, आगे बढ़ते हैं।",
            ])

        if language == "hinglish":

            return random.choice([
                "👍 Theek hai! Samajh gaya. 😊",
                "✅ Bilkul! Got it.",
                "😊 Okay, samajh gaya. Aage badhte hain!",
            ])

        return random.choice([
            "👍 Got it! 😊",
            "✅ Understood!",
            "😊 Alright, let's move forward.",
        ])


    # ====================================================
    # COMPLIMENT
    # ====================================================

    def _compliment_reply(
        self,
        language: str
    ) -> str:

        if language == "hindi":

            return random.choice([
                "🥹❤️ बहुत-बहुत धन्यवाद! यह सुनकर सच में खुशी हुई।",
                "😊 शुक्रिया! आपकी बात ने मेरा mood अच्छा कर दिया। ❤️",
                "🤗 धन्यवाद! मैं आगे भी अपना best देने की कोशिश करूँगा।",
            ])

        if language == "hinglish":

            return random.choice([
                "🥹❤️ Thank you so much! Ye sunkar genuinely accha laga.",
                "😊 Thanks yaar! Aapki baat ne mood bana diya. ❤️",
                "🤗 Thank you! Main aage bhi apna best dene ki koshish karunga.",
            ])

        return random.choice([
            "🥹❤️ Thank you so much! That really means a lot.",
            "😊 Thanks! I'm really glad you liked it.",
            "🤗 Thank you! I'll keep doing my best.",
        ])


    # ====================================================
    # SUPPORTIVE REPLY
    # ====================================================

    def _supportive_reply(
        self,
        language: str,
        emotion: str
    ) -> str:

        if emotion == "sad":

            if language == "hindi":

                return (
                    "🫂 मुझे अफसोस है कि आप ऐसा महसूस कर रहे हैं। ❤️\n\n"
                    "आपको सब कुछ अकेले handle करने की जरूरत नहीं है। "
                    "अगर आप चाहें तो मुझे बता सकते हैं कि क्या हुआ।"
                )

            if language == "hinglish":

                return (
                    "🫂 I'm here for you. ❤️\n\n"
                    "Agar aap comfortable ho, toh batao kya hua. "
                    "Hum calmly baat kar sakte hain."
                )

            return (
                "🫂 I'm here to listen. ❤️\n\n"
                "If you feel comfortable, you can tell me what happened. "
                "We can take it one step at a time."
            )

        if emotion == "worried":

            if language == "hindi":

                return (
                    "🫂 चिंता मत कीजिए। एक-एक step करके situation ko handle "
                    "करने की कोशिश करते हैं। ❤️"
                )

            if language == "hinglish":

                return (
                    "🫂 Tension mat lo. Ek-ek step karke situation ko handle "
                    "karte hain. ❤️"
                )

            return (
                "🫂 Don't worry. Let's handle it one step at a time. ❤️"
            )

        if emotion == "angry":

            if language == "hindi":

                return (
                    "🫂 समझ सकता हूँ कि आपको गुस्सा आ रहा है। "
                    "पहले थोड़ा calm होते हैं, फिर situation ko dekhte hain."
                )

            if language == "hinglish":

                return (
                    "🫂 Samajh sakta hoon ki aap gusse mein ho. "
                    "Pehle thoda calm hote hain, phir situation ko properly dekhte hain."
                )

            return (
                "🫂 I understand that you're upset. "
                "Let's slow things down and look at the situation calmly."
            )

        return ""


    # ====================================================
    # GENERAL REPLY
    # ====================================================

    def _general_reply(
        self,
        language: str
    ) -> str:

        if language == "hindi":

            return (
                "😊 बिल्कुल! मैं आपकी मदद करने के लिए तैयार हूँ। "
                "बताइए, आपको किस चीज़ में help चाहिए?"
            )

        if language == "hinglish":

            return (
                "😊 Bilkul! Main aapki help karne ke liye ready hoon. "
                "Batao, kis cheez mein help chahiye?"
            )

        return (
            "😊 Absolutely! I'm ready to help. "
            "Tell me what you'd like to do."
        )


    # ====================================================
    # MAIN REPLY METHOD
    # ====================================================

    def generate_reply(
        self,
        query: str,
        intent: Optional[str] = None,
        emotion: Optional[str] = None,
        language: Optional[str] = None
    ) -> ReplyResult:

        original = clean_text(query)

        if not original:

            return ReplyResult(
                success=False,
                query="",
                error="Empty query.",
                error_type="empty_query"
            )

        if language is None:

            language = detect_language(
                original
            )

        if emotion is None:

            emotion = detect_emotion(
                original
            )

        if intent is None:

            intent = detect_reply_intent(
                original
            )

        # ------------------------------------------------
        # EMOTIONAL SUPPORT FIRST
        # ------------------------------------------------

        if emotion in {
            "sad",
            "worried",
            "angry"
        }:

            supportive = self._supportive_reply(
                language,
                emotion
            )

            if supportive:

                return ReplyResult(
                    success=True,
                    query=original,
                    answer=supportive,
                    intent=intent,
                    emotion=emotion,
                    language=language
                )

        # ------------------------------------------------
        # INTENT REPLIES
        # ------------------------------------------------

        if intent == "greeting":

            answer = self._greeting_reply(
                language,
                emotion
            )

        elif intent == "thanks":

            answer = self._thanks_reply(
                language
            )

        elif intent == "goodbye":

            answer = self._goodbye_reply(
                language
            )

        elif intent == "acknowledgement":

            answer = self._acknowledgement_reply(
                language
            )

        elif intent == "compliment":

            answer = self._compliment_reply(
                language
            )

        else:

            answer = self._general_reply(
                language
            )

        return ReplyResult(
            success=True,
            query=original,
            answer=answer,
            intent=intent,
            emotion=emotion,
            language=language
        )


    # ====================================================
    # SIMPLE REPLY
    # ====================================================

    def reply(
        self,
        query: str
    ) -> str:

        result = self.generate_reply(
            query
        )

        if not result.success:

            return (
                "😕 Sorry, I couldn't process that."
            )

        return result.answer


    # ====================================================
    # STATUS
    # ====================================================

    def status(self) -> Dict[str, Any]:

        return {
            "engine": self.engine_name,
            "version": self.version,
            "features": [
                "polite_replies",
                "natural_replies",
                "emotion_detection",
                "language_detection",
                "greetings",
                "thanks",
                "goodbye",
                "acknowledgements",
                "compliments",
                "supportive_replies",
                "emoji_support",
            ]
        }


# ========================================================
# GLOBAL ENGINE
# ========================================================

_reply_engine = ReplyEngine()


# ========================================================
# PUBLIC FUNCTIONS
# ========================================================

def generate_reply(
    query: str,
    intent: Optional[str] = None,
    emotion: Optional[str] = None,
    language: Optional[str] = None
) -> ReplyResult:

    return _reply_engine.generate_reply(
        query,
        intent,
        emotion,
        language
    )


def reply(
    query: str
) -> str:

    return _reply_engine.reply(
        query
    )


def reply_status() -> Dict[str, Any]:

    return _reply_engine.status()


# ========================================================
# SELF TEST
# ========================================================

def run_self_test() -> bool:

    print(
        "AkshAI Reply Engine v1.0"
    )

    print(
        "=" * 55
    )

    engine = ReplyEngine()

    passed = 0

    # ----------------------------------------------------
    # 1. Greeting
    # ----------------------------------------------------

    result = engine.generate_reply(
        "Hello AkshAI"
    )

    assert result.success
    assert result.intent == "greeting"

    print(
        "Greeting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 2. Hinglish
    # ----------------------------------------------------

    result = engine.generate_reply(
        "Bhai kaise ho?"
    )

    assert result.success
    assert result.language == "hinglish"

    print(
        "Hinglish detection test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 3. Thanks
    # ----------------------------------------------------

    result = engine.generate_reply(
        "Thank you"
    )

    assert result.success
    assert result.intent == "thanks"

    print(
        "Thanks test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 4. Goodbye
    # ----------------------------------------------------

    result = engine.generate_reply(
        "Bye AkshAI"
    )

    assert result.success
    assert result.intent == "goodbye"

    print(
        "Goodbye test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 5. Acknowledgement
    # ----------------------------------------------------

    result = engine.generate_reply(
        "Okay, got it"
    )

    assert result.success
    assert result.intent == "acknowledgement"

    print(
        "Acknowledgement test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 6. Compliment
    # ----------------------------------------------------

    result = engine.generate_reply(
        "You are awesome"
    )

    assert result.success
    assert result.intent == "compliment"

    print(
        "Compliment test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 7. Sad emotion
    # ----------------------------------------------------

    result = engine.generate_reply(
        "I am feeling sad"
    )

    assert result.success
    assert result.emotion == "sad"
    assert "❤️" in result.answer

    print(
        "Sad emotion test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 8. Worried emotion
    # ----------------------------------------------------

    result = engine.generate_reply(
        "I am worried"
    )

    assert result.success
    assert result.emotion == "worried"

    print(
        "Worried emotion test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 9. Angry emotion
    # ----------------------------------------------------

    result = engine.generate_reply(
        "I am angry"
    )

    assert result.success
    assert result.emotion == "angry"

    print(
        "Angry emotion test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 10. Hindi
    # ----------------------------------------------------

    result = engine.generate_reply(
        "नमस्ते, आप कैसे हैं?"
    )

    assert result.success
    assert result.language == "hindi"

    print(
        "Hindi detection test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 11. Empty query
    # ----------------------------------------------------

    result = engine.generate_reply(
        ""
    )

    assert not result.success
    assert result.error_type == "empty_query"

    print(
        "Empty query handling test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 12. Simple reply
    # ----------------------------------------------------

    answer = engine.reply(
        "Hello"
    )

    assert isinstance(
        answer,
        str
    )

    assert len(answer) > 0

    print(
        "Simple reply test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 13. Status
    # ----------------------------------------------------

    status = engine.status()

    assert status["engine"] == ENGINE_NAME
    assert status["version"] == ENGINE_VERSION
    assert len(status["features"]) > 0

    print(
        "Status test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # FINAL
    # ----------------------------------------------------

    print(
        "-" * 55
    )

    print(
        f"Tests passed: {passed}/13"
    )

    if passed == 13:

        print(
            "REPLY ENGINE TEST PASSED ✅"
        )

        return True

    print(
        "REPLY ENGINE TEST FAILED ❌"
    )

    return False


# ========================================================
# RUN DIRECTLY
# ========================================================

if __name__ == "__main__":

    run_self_test()