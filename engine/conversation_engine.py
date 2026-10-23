"""
AkshAI - Conversation Engine v1.0
-----------------------------------
Purpose:
- Manage complete conversations.
- Store user and assistant turns.
- Generate conversation history.
- Create conversation summaries.
- Track conversation IDs.
- Work with Context Engine.
- Provide clean data to Brain / AI Engine.

Important:
Conversation Engine manages the conversation.
Context Engine understands short-term context.
Memory Engine will later handle long-term user memory.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


# ============================================================
# CONVERSATION MESSAGE
# ============================================================

@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


# ============================================================
# CONVERSATION
# ============================================================

@dataclass
class Conversation:
    conversation_id: str
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    title: str = "New Conversation"

    messages: List[ConversationMessage] = field(
        default_factory=list
    )

    active: bool = True

    def add_message(
        self,
        role: str,
        content: str
    ) -> ConversationMessage:

        message = ConversationMessage(
            role=role,
            content=content
        )

        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

        return message

    def to_dict(self) -> Dict[str, Any]:

        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "active": self.active,
            "message_count": len(self.messages),
            "messages": [
                message.to_dict()
                for message in self.messages
            ],
        }


# ============================================================
# CONVERSATION ENGINE
# ============================================================

class ConversationEngine:

    def __init__(
        self,
        max_messages: int = 100
    ):

        self.max_messages = max(
            1,
            max_messages
        )

        self.conversations: Dict[
            str,
            Conversation
        ] = {}

        self.active_conversation_id: Optional[str] = None

        self.total_turns = 0

        self.create_conversation()

    # ========================================================
    # CREATE CONVERSATION
    # ========================================================

    def create_conversation(
        self,
        title: str = "New Conversation"
    ) -> Conversation:

        conversation_id = str(
            uuid.uuid4()
        )

        conversation = Conversation(
            conversation_id=conversation_id,
            title=title
        )

        self.conversations[
            conversation_id
        ] = conversation

        self.active_conversation_id = (
            conversation_id
        )

        return conversation

    # ========================================================
    # GET ACTIVE CONVERSATION
    # ========================================================

    def get_active_conversation(
        self
    ) -> Optional[Conversation]:

        if not self.active_conversation_id:
            return None

        return self.conversations.get(
            self.active_conversation_id
        )

    # ========================================================
    # SWITCH CONVERSATION
    # ========================================================

    def switch_conversation(
        self,
        conversation_id: str
    ) -> bool:

        if conversation_id not in self.conversations:
            return False

        self.active_conversation_id = (
            conversation_id
        )

        for cid, conversation in self.conversations.items():
            conversation.active = (
                cid == conversation_id
            )

        return True

    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        role: str,
        content: str
    ) -> Optional[ConversationMessage]:

        content = str(content).strip()

        if not content:
            return None

        conversation = (
            self.get_active_conversation()
        )

        if conversation is None:
            conversation = self.create_conversation()

        message = conversation.add_message(
            role,
            content
        )

        self.total_turns += 1

        self._trim_messages(
            conversation
        )

        return message

    # ========================================================
    # USER MESSAGE
    # ========================================================

    def add_user_message(
        self,
        content: str
    ) -> Optional[ConversationMessage]:

        return self.add_message(
            "user",
            content
        )

    # ========================================================
    # ASSISTANT MESSAGE
    # ========================================================

    def add_assistant_message(
        self,
        content: str
    ) -> Optional[ConversationMessage]:

        return self.add_message(
            "assistant",
            content
        )

    # ========================================================
    # SYSTEM MESSAGE
    # ========================================================

    def add_system_message(
        self,
        content: str
    ) -> Optional[ConversationMessage]:

        return self.add_message(
            "system",
            content
        )

    # ========================================================
    # TRIM
    # ========================================================

    def _trim_messages(
        self,
        conversation: Conversation
    ) -> None:

        if len(conversation.messages) > self.max_messages:

            conversation.messages = (
                conversation.messages[
                    -self.max_messages:
                ]
            )

    # ========================================================
    # GET MESSAGES
    # ========================================================

    def get_messages(
        self,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return []

        messages = conversation.messages

        if limit is not None:
            limit = max(1, limit)
            messages = messages[-limit:]

        return [
            message.to_dict()
            for message in messages
        ]

    # ========================================================
    # GET LAST MESSAGE
    # ========================================================

    def get_last_message(
        self,
        role: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Optional[Dict[str, str]]:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return None

        for message in reversed(
            conversation.messages
        ):

            if role is None or message.role == role:
                return message.to_dict()

        return None

    # ========================================================
    # GET LAST USER MESSAGE
    # ========================================================

    def get_last_user_message(
        self
    ) -> Optional[Dict[str, str]]:

        return self.get_last_message(
            role="user"
        )

    # ========================================================
    # GET LAST ASSISTANT MESSAGE
    # ========================================================

    def get_last_assistant_message(
        self
    ) -> Optional[Dict[str, str]]:

        return self.get_last_message(
            role="assistant"
        )

    # ========================================================
    # CONVERSATION TEXT
    # ========================================================

    def get_conversation_text(
        self,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> str:

        messages = self.get_messages(
            conversation_id,
            limit
        )

        lines = []

        for message in messages:

            role = message["role"].capitalize()

            lines.append(
                f"{role}: {message['content']}"
            )

        return "\n".join(lines)

    # ========================================================
    # AI FORMAT
    # ========================================================

    def get_ai_messages(
        self,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:

        """
        Return messages in a format suitable
        for a future LLM / AI Engine.
        """

        messages = self.get_messages(
            conversation_id,
            limit
        )

        result = []

        for message in messages:

            result.append({
                "role": message["role"],
                "content": message["content"],
            })

        return result

    # ========================================================
    # TITLE
    # ========================================================

    def set_title(
        self,
        title: str,
        conversation_id: Optional[str] = None
    ) -> bool:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return False

        title = str(title).strip()

        if not title:
            return False

        conversation.title = title

        conversation.updated_at = (
            datetime.now().isoformat()
        )

        return True

    # ========================================================
    # AUTO TITLE
    # ========================================================

    def generate_title(
        self,
        conversation_id: Optional[str] = None
    ) -> str:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return "New Conversation"

        for message in conversation.messages:

            if message.role == "user":

                text = message.content.strip()

                if not text:
                    continue

                words = text.split()

                title = " ".join(
                    words[:7]
                )

                if len(words) > 7:
                    title += "..."

                conversation.title = title

                return title

        return "New Conversation"

    # ========================================================
    # SUMMARY
    # ========================================================

    def get_summary(
        self,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return {}

        user_messages = [
            message.content
            for message in conversation.messages
            if message.role == "user"
        ]

        assistant_messages = [
            message.content
            for message in conversation.messages
            if message.role == "assistant"
        ]

        return {
            "conversation_id":
                conversation.conversation_id,

            "title":
                conversation.title,

            "message_count":
                len(conversation.messages),

            "user_message_count":
                len(user_messages),

            "assistant_message_count":
                len(assistant_messages),

            "first_user_message":
                user_messages[0]
                if user_messages
                else "",

            "last_user_message":
                user_messages[-1]
                if user_messages
                else "",

            "last_assistant_message":
                assistant_messages[-1]
                if assistant_messages
                else "",
        }

    # ========================================================
    # LIST CONVERSATIONS
    # ========================================================

    def list_conversations(
        self
    ) -> List[Dict[str, Any]]:

        result = []

        for conversation in (
            self.conversations.values()
        ):

            result.append({
                "conversation_id":
                    conversation.conversation_id,

                "title":
                    conversation.title,

                "message_count":
                    len(conversation.messages),

                "active":
                    conversation.active,

                "created_at":
                    conversation.created_at,

                "updated_at":
                    conversation.updated_at,
            })

        return result

    # ========================================================
    # DELETE CONVERSATION
    # ========================================================

    def delete_conversation(
        self,
        conversation_id: str
    ) -> bool:

        if conversation_id not in self.conversations:
            return False

        del self.conversations[
            conversation_id
        ]

        if (
            self.active_conversation_id
            == conversation_id
        ):

            self.active_conversation_id = None

            if self.conversations:

                newest = list(
                    self.conversations.keys()
                )[-1]

                self.active_conversation_id = (
                    newest
                )

                for cid, conversation in (
                    self.conversations.items()
                ):

                    conversation.active = (
                        cid == newest
                    )

            else:
                self.create_conversation()

        return True

    # ========================================================
    # CLEAR ACTIVE CONVERSATION
    # ========================================================

    def clear_active_conversation(
        self
    ) -> bool:

        conversation = (
            self.get_active_conversation()
        )

        if conversation is None:
            return False

        conversation.messages.clear()

        conversation.title = (
            "New Conversation"
        )

        conversation.updated_at = (
            datetime.now().isoformat()
        )

        return True

    # ========================================================
    # END CONVERSATION
    # ========================================================

    def end_conversation(
        self,
        conversation_id: Optional[str] = None
    ) -> bool:

        conversation = self._get_conversation(
            conversation_id
        )

        if conversation is None:
            return False

        conversation.active = False

        if (
            conversation.conversation_id
            == self.active_conversation_id
        ):

            self.active_conversation_id = None

        return True

    # ========================================================
    # INTERNAL GET
    # ========================================================

    def _get_conversation(
        self,
        conversation_id: Optional[str]
    ) -> Optional[Conversation]:

        if conversation_id is None:

            return self.get_active_conversation()

        return self.conversations.get(
            conversation_id
        )

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self) -> Dict[str, Any]:

        active = (
            self.get_active_conversation()
        )

        return {
            "engine": "conversation_engine",
            "version": "1.0",
            "status": "ready",
            "conversation_count":
                len(self.conversations),
            "active_conversation_id":
                self.active_conversation_id,
            "active_message_count":
                len(active.messages)
                if active
                else 0,
            "total_turns":
                self.total_turns,
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

conversation_engine = ConversationEngine()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def new_conversation(
    title: str = "New Conversation"
) -> Dict[str, Any]:

    return conversation_engine.create_conversation(
        title
    ).to_dict()


def add_user_message(
    text: str
) -> Optional[Dict[str, str]]:

    message = conversation_engine.add_user_message(
        text
    )

    return (
        message.to_dict()
        if message
        else None
    )


def add_assistant_message(
    text: str
) -> Optional[Dict[str, str]]:

    message = conversation_engine.add_assistant_message(
        text
    )

    return (
        message.to_dict()
        if message
        else None
    )


def get_conversation(
    limit: Optional[int] = None
) -> List[Dict[str, str]]:

    return conversation_engine.get_messages(
        limit=limit
    )


def get_ai_messages(
    limit: Optional[int] = None
) -> List[Dict[str, str]]:

    return conversation_engine.get_ai_messages(
        limit=limit
    )


def get_last_user_message() -> Optional[Dict[str, str]]:

    return conversation_engine.get_last_user_message()


def get_last_assistant_message() -> Optional[Dict[str, str]]:

    return conversation_engine.get_last_assistant_message()


def clear_conversation() -> bool:

    return conversation_engine.clear_active_conversation()


def conversation_status() -> Dict[str, Any]:

    return conversation_engine.get_status()


# ============================================================
# SELF TEST
# ============================================================

def run_conversation_engine_test() -> bool:

    engine = ConversationEngine(
        max_messages=5
    )

    # --------------------------------------------------------
    # Create test
    # --------------------------------------------------------

    conversation = engine.get_active_conversation()

    if conversation is None:
        print("FAILED conversation creation")
        return False

    print("Conversation creation test passed")

    # --------------------------------------------------------
    # User message
    # --------------------------------------------------------

    engine.add_user_message(
        "Hello AkshAI"
    )

    if len(conversation.messages) != 1:
        print("FAILED user message")
        return False

    print("User message test passed")

        # --------------------------------------------------------
    # Assistant message
    # --------------------------------------------------------

    engine.add_assistant_message(
        "Hello! How can I help you?"
    )

    if len(conversation.messages) != 2:
        print("FAILED assistant message")
        return False

    print("Assistant message test passed")

    # --------------------------------------------------------
    # Last message
    # --------------------------------------------------------

    last_user = engine.get_last_user_message()

    if last_user is None:
        print("FAILED last user message")
        return False

    if last_user["content"] != "Hello AkshAI":
        print("FAILED last user content")
        return False

    print("Last message test passed")

    # --------------------------------------------------------
    # Conversation text
    # --------------------------------------------------------

    text = engine.get_conversation_text()

    if "Hello AkshAI" not in text:
        print("FAILED conversation text")
        return False

    if "How can I help" not in text:
        print("FAILED assistant text")
        return False

    print("Conversation text test passed")

    # --------------------------------------------------------
    # AI messages
    # --------------------------------------------------------

    ai_messages = engine.get_ai_messages()

    if len(ai_messages) != 2:
        print("FAILED AI messages")
        return False

    if ai_messages[0]["role"] != "user":
        print("FAILED AI role")
        return False

    print("AI message format test passed")

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = engine.generate_title()

    if not title:
        print("FAILED title generation")
        return False

    print("Title generation test passed")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = engine.get_summary()

    if summary["message_count"] != 2:
        print("FAILED summary")
        return False

    print("Summary test passed")

    # --------------------------------------------------------
    # Multiple conversations
    # --------------------------------------------------------

    first_id = engine.active_conversation_id

    second = engine.create_conversation(
        "Physics"
    )

    second_id = second.conversation_id

    if first_id == second_id:
        print("FAILED unique conversation IDs")
        return False

    if len(engine.conversations) != 2:
        print("FAILED multiple conversations")
        return False

    print("Multiple conversation test passed")

    # --------------------------------------------------------
    # Switch
    # --------------------------------------------------------

    if not engine.switch_conversation(first_id):
        print("FAILED conversation switching")
        return False

    if engine.active_conversation_id != first_id:
        print("FAILED active conversation")
        return False

    print("Conversation switching test passed")

    # --------------------------------------------------------
    # Message limit
    # --------------------------------------------------------

    for i in range(10):
        engine.add_user_message(
            f"Test message {i}"
        )

    if len(
        engine.get_active_conversation().messages
    ) > 5:
        print("FAILED message limit")
        return False

    print("Message limit test passed")

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    if not engine.clear_active_conversation():
        print("FAILED clear")
        return False

    if engine.get_active_conversation().messages:
        print("FAILED conversation clear")
        return False

    print("Conversation clear test passed")

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = engine.get_status()

    if status["status"] != "ready":
        print("FAILED status")
        return False

    print("Status test passed")

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("CONVERSATION ENGINE TEST PASSED ✅")

    return True


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":
    run_conversation_engine_test()