# engine/action_engine.py
# AkshAI Action Engine v1.1
# Direct Android App Launcher + Safe Call/Message Preparation

from dataclasses import dataclass, asdict
import subprocess
import webbrowser
import re


@dataclass
class ActionResult:
    success: bool
    action: str
    target: str
    answer: str
    requires_confirmation: bool = False
    executed: bool = False
    data: dict = None
    error: str = ""

    def to_dict(self):
        return asdict(self)


class ActionEngine:

    def __init__(self):
        self.name = "Action Engine"
        self.version = "1.1"

        # Android package names
        self.apps = {
            "youtube": {
                "name": "YouTube",
                "package": "com.google.android.youtube",
                "url": "https://www.youtube.com/"
            },
            "whatsapp": {
                "name": "WhatsApp",
                "package": "com.whatsapp",
                "url": "https://web.whatsapp.com/"
            },
            "instagram": {
                "name": "Instagram",
                "package": "com.instagram.android",
                "url": "https://www.instagram.com/"
            },
            "facebook": {
                "name": "Facebook",
                "package": "com.facebook.katana",
                "url": "https://www.facebook.com/"
            },
            "chrome": {
                "name": "Chrome",
                "package": "com.android.chrome",
                "url": "https://www.google.com/"
            },
            "spotify": {
                "name": "Spotify",
                "package": "com.spotify.music",
                "url": "https://open.spotify.com/"
            },
            "telegram": {
                "name": "Telegram",
                "package": "org.telegram.messenger",
                "url": "https://telegram.org/"
            },
            "gmail": {
                "name": "Gmail",
                "package": "com.google.android.gm",
                "url": "https://mail.google.com/"
            },
            "maps": {
                "name": "Google Maps",
                "package": "com.google.android.apps.maps",
                "url": "https://maps.google.com/"
            }
        }

        # Contacts
        self.contacts = {
            "mummy": {
                "name": "Mummy",
                "phone": ""
            },
            "mom": {
                "name": "Mummy",
                "phone": ""
            },
            "papa": {
                "name": "Papa",
                "phone": ""
            },
            "dad": {
                "name": "Papa",
                "phone": ""
            },
            "brother": {
                "name": "Brother",
                "phone": ""
            },
            "sister": {
                "name": "Sister",
                "phone": ""
            }
        }


    # =========================================================
    # ANDROID COMMAND
    # =========================================================

    def android_command(self, args):
        """
        Runs Android Activity Manager command.
        """

        try:
            result = subprocess.run(
                ["am"] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=8
            )

            return result.returncode == 0, result.stdout, result.stderr

        except Exception as error:
            return False, "", str(error)


    # =========================================================
    # CHECK INSTALLED APP
    # =========================================================

    def is_app_installed(self, package):
        """
        Checks whether Android package is installed.
        """

        success, stdout, stderr = self.android_command([
            "shell",
            "pm",
            "path",
            package
        ])

        return success and "package:" in stdout


    # =========================================================
    # OPEN INSTALLED APP
    # =========================================================

    def open_app(self, app_name):

        key = str(app_name).strip().lower()

        if key not in self.apps:
            return ActionResult(
                success=False,
                action="open_app",
                target=app_name,
                answer="",
                error="app_not_supported"
            )

        app = self.apps[key]
        display_name = app["name"]
        package = app["package"]

        # -----------------------------------------------------
        # Method 1: Direct Android package launch
        # -----------------------------------------------------

        success, stdout, stderr = self.android_command([
            "shell",
            "monkey",
            "-p",
            package,
            "1"
        ])

        if success:

            return ActionResult(
                success=True,
                action="open_app",
                target=key,
                answer=f"📱 I opened **{display_name}**.",
                requires_confirmation=False,
                executed=True,
                data={
                    "method": "android_app",
                    "package": package
                }
            )

        # -----------------------------------------------------
        # Method 2: Android VIEW intent
        # -----------------------------------------------------

        success, stdout, stderr = self.android_command([
            "shell",
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            app["url"]
        ])

        if success:

            return ActionResult(
                success=True,
                action="open_app",
                target=key,
                answer=f"📱 I opened **{display_name}**.",
                requires_confirmation=False,
                executed=True,
                data={
                    "method": "android_intent",
                    "package": package
                }
            )

        # -----------------------------------------------------
        # Method 3: Browser fallback
        # -----------------------------------------------------

        try:
            opened = webbrowser.open(app["url"])

            if opened:

                return ActionResult(
                    success=True,
                    action="open_app",
                    target=key,
                    answer=(
                        f"🌐 **{display_name}** app couldn't be opened directly, "
                        f"so I opened it through the browser."
                    ),
                    requires_confirmation=False,
                    executed=True,
                    data={
                        "method": "browser_fallback",
                        "package": package
                    }
                )

        except Exception as error:
            stderr = str(error)

        return ActionResult(
            success=False,
            action="open_app",
            target=key,
            answer=f"❌ I couldn't open **{display_name}**.",
            executed=False,
            error=stderr or "app_launch_failed"
        )


    # =========================================================
    # OPEN WEBSITE
    # =========================================================

    def open_website(self, url):

        url = str(url).strip()

        if not url:
            return ActionResult(
                success=False,
                action="open_website",
                target="",
                answer="",
                error="empty_url"
            )

        if not re.match(r"^https?://", url, re.I):
            url = "https://" + url

        try:
            opened = webbrowser.open(url)

            if opened:
                return ActionResult(
                    success=True,
                    action="open_website",
                    target=url,
                    answer=f"🌐 I opened **{url}**.",
                    executed=True
                )

        except Exception as error:
            return ActionResult(
                success=False,
                action="open_website",
                target=url,
                answer="",
                error=str(error)
            )

        return ActionResult(
            success=False,
            action="open_website",
            target=url,
            answer="",
            error="website_open_failed"
        )


    # =========================================================
    # PREPARE CALL
    # =========================================================

    def prepare_call(self, contact):

        key = str(contact).strip().lower()

        if key not in self.contacts:
            return ActionResult(
                success=False,
                action="call",
                target=contact,
                answer="",
                error="contact_not_found"
            )

        person = self.contacts[key]

        return ActionResult(
            success=True,
            action="call",
            target=person["name"],
            answer=(
                f"📞 I can prepare a call to **{person['name']}**.\n"
                f"Please confirm before the call is placed."
            ),
            requires_confirmation=True,
            executed=False,
            data={
                "phone": person["phone"]
            }
        )


    # =========================================================
    # PREPARE MESSAGE
    # =========================================================

    def prepare_message(self, contact, message):

        key = str(contact).strip().lower()
        message = str(message).strip()

        if key not in self.contacts:
            return ActionResult(
                success=False,
                action="message",
                target=contact,
                answer="",
                error="contact_not_found"
            )

        if not message:
            return ActionResult(
                success=False,
                action="message",
                target=self.contacts[key]["name"],
                answer="",
                error="empty_message"
            )

        person = self.contacts[key]

        return ActionResult(
            success=True,
            action="message",
            target=person["name"],
            answer=(
                f"💬 Message prepared for **{person['name']}**:\n\n"
                f"“{message}”\n\n"
                f"Please confirm before sending."
            ),
            requires_confirmation=True,
            executed=False,
            data={
                "phone": person["phone"],
                "message": message
            }
        )


    # =========================================================
    # NATURAL LANGUAGE ACTION PARSER
    # =========================================================

    def answer_query(self, query):

        query = str(query).strip()

        if not query:
            return ActionResult(
                success=False,
                action="unknown",
                target="",
                answer="",
                error="empty_query"
            )

        text = query.lower()

        # -----------------------------------------------------
        # OPEN APP
        # -----------------------------------------------------

        open_match = re.match(
            r"^(?:open|launch|start)\s+(.+?)$",
            text,
            re.I
        )

        if open_match:

            target = open_match.group(1).strip()

            # Remove common words
            target = re.sub(
                r"\bapp\b",
                "",
                target,
                flags=re.I
            ).strip()

            if target in self.apps:
                return self.open_app(target)

        # -----------------------------------------------------
        # CALL
        # -----------------------------------------------------

        call_match = re.match(
            r"^(?:call|phone|dial)\s+(.+?)$",
            text,
            re.I
        )

        if call_match:

            contact = call_match.group(1).strip()

            if contact in self.contacts:
                return self.prepare_call(contact)

        # -----------------------------------------------------
        # MESSAGE
        # -----------------------------------------------------

        message_patterns = [
            r"^(?:send|message|text)\s+(.+?)\s+(?:saying|that)\s+(.+)$",
            r"^(?:send|message|text)\s+(.+?)\s+message\s+(.+)$",
        ]

        for pattern in message_patterns:

            match = re.match(pattern, text, re.I)

            if match:

                contact = match.group(1).strip()
                message = match.group(2).strip()

                # Use original query to preserve message capitalization
                original_match = re.match(
                    pattern,
                    query,
                    re.I
                )

                if original_match:
                    contact = original_match.group(1).strip()
                    message = original_match.group(2).strip()

                return self.prepare_message(
                    contact,
                    message
                )

        # -----------------------------------------------------
        # WHATSAPP MESSAGE
        # -----------------------------------------------------

        whatsapp_match = re.match(
            r"^whatsapp\s+(.+?)\s+(?:saying|that)\s+(.+)$",
            query,
            re.I
        )

        if whatsapp_match:

            contact = whatsapp_match.group(1).strip()
            message = whatsapp_match.group(2).strip()

            return self.prepare_message(
                contact,
                message
            )

        return ActionResult(
            success=False,
            action="unknown",
            target=query,
            answer="",
            error="action_not_recognized"
        )


# =============================================================
# MODULE LEVEL API
# =============================================================

_ACTION_ENGINE = ActionEngine()


def get_action_engine():
    return _ACTION_ENGINE


def open_app(app_name):
    return _ACTION_ENGINE.open_app(app_name)


def open_website(url):
    return _ACTION_ENGINE.open_website(url)


def prepare_call(contact):
    return _ACTION_ENGINE.prepare_call(contact)


def prepare_message(contact, message):
    return _ACTION_ENGINE.prepare_message(contact, message)


def answer_query(query):
    return _ACTION_ENGINE.answer_query(query)


# =============================================================
# SELF TEST
# =============================================================

def action_self_test():

    tests = [
        "open youtube",
        "open whatsapp",
        "open instagram",
        "call mummy",
        "call papa",
        "send mummy saying hello",
        "message papa saying I will be late",
    ]

    results = []

    for query in tests:

        try:
            result = answer_query(query)
            results.append({
                "query": query,
                **result.to_dict()
            })

        except Exception as error:

            results.append({
                "query": query,
                "success": False,
                "action": "test",
                "target": "",
                "requires_confirmation": False,
                "executed": False,
                "answer": "",
                "error": str(error)
            })

    return results


if __name__ == "__main__":

    print("⚡ AkshAI Action Engine v1.1")

    for item in action_self_test():
        print(item)