"""
AkshAI - Command Engine v1.0
--------------------------------
Purpose:
- Detect explicit commands.
- Extract command name, arguments and subcommands.
- Provide structured command data to Brain.
- Do NOT handle normal natural-language questions.

Examples:
    /help
    /weather Delhi
    /calculate 25 * 4
    /search latest JEE news
    /note add Physics formulas
    /remember my exam is tomorrow
    /time
    /status

Normal conversation such as:
    "Hello AkshAI"
    "Explain Newton's second law"
    "Why is the sky blue?"
should NOT become commands.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ============================================================
# COMMAND DATA
# ============================================================

@dataclass
class Command:
    """
    Structured representation of an explicit command.
    """

    name: str
    args: List[str] = field(default_factory=list)
    raw_args: str = ""
    subcommand: Optional[str] = None
    is_command: bool = True

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "args": self.args,
            "raw_args": self.raw_args,
            "subcommand": self.subcommand,
            "is_command": self.is_command,
        }


# ============================================================
# COMMAND DEFINITIONS
# ============================================================

COMMAND_ALIASES = {
    "calc": "calculate",
    "cal": "calculate",
    "math": "calculate",

    "weather": "weather",
    "forecast": "weather",

    "search": "search",
    "web": "search",
    "google": "search",

    "note": "notes",
    "notes": "notes",

    "remember": "memory",
    "memory": "memory",

    "me": "profile",
    "profile": "profile",

    "clock": "time",
    "date": "time",
    "time": "time",

    "commands": "help",
    "?": "help",

    "quit": "exit",
    "bye": "exit",

    "reset": "clear",
}

SUPPORTED_COMMANDS = {
    "help",
    "calculate",
    "weather",
    "search",
    "notes",
    "memory",
    "profile",
    "time",
    "status",
    "clear",
    "exit",
}


# Commands that are allowed without arguments.
NO_ARGUMENT_COMMANDS = {
    "help",
    "status",
    "time",
    "clear",
    "exit",
}


# ============================================================
# PREFIXES
# ============================================================

COMMAND_PREFIXES = (
    "/",
    "!",
)


# ============================================================
# COMMAND ENGINE
# ============================================================

class CommandEngine:
    """
    Detects and parses explicit commands.

    The Command Engine does NOT try to understand every sentence.

    Example:

        /weather Delhi
            -> command

        /calculate 25 * 5
            -> command

        Explain Newton's second law
            -> not a command
    """

    def __init__(self):
        self.commands = set(SUPPORTED_COMMANDS)
        self.aliases = dict(COMMAND_ALIASES)

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize command input without changing its meaning.
        """

        if text is None:
            return ""

        return " ".join(str(text).strip().split())

    # --------------------------------------------------------
    # CHECK COMMAND
    # --------------------------------------------------------

    def is_command(self, text: str) -> bool:
        """
        Return True only when the user explicitly starts
        a command with a supported command prefix.

        Examples:
            /help           -> True
            /weather Delhi  -> True
            !calculate 5+5  -> True

            hello           -> False
            calculate 5+5   -> False
            explain physics -> False
        """

        text = self.normalize_text(text)

        if not text:
            return False

        if text[0] not in COMMAND_PREFIXES:
            return False

        without_prefix = text[1:].strip()

        if not without_prefix:
            return False

        command_word = without_prefix.split(maxsplit=1)[0].lower()

        command_word = self.aliases.get(
            command_word,
            command_word
        )

        return command_word in self.commands

    # --------------------------------------------------------
    # COMMAND NAME
    # --------------------------------------------------------

    def get_command_name(self, text: str) -> Optional[str]:
        """
        Extract normalized command name.
        """

        if not self.is_command(text):
            return None

        text = self.normalize_text(text)

        command_word = text[1:].split(maxsplit=1)[0].lower()

        return self.aliases.get(
            command_word,
            command_word
        )

    # --------------------------------------------------------
    # ARGUMENT STRING
    # --------------------------------------------------------

    def get_raw_args(self, text: str) -> str:
        """
        Return everything after the command name.
        """

        if not self.is_command(text):
            return ""

        text = self.normalize_text(text)

        content = text[1:].strip()

        parts = content.split(maxsplit=1)

        if len(parts) == 1:
            return ""

        return parts[1].strip()

    # --------------------------------------------------------
    # ARGUMENT LIST
    # --------------------------------------------------------

    def get_args(self, text: str) -> List[str]:
        """
        Split command arguments.

        Example:
            /weather Delhi India

        becomes:
            ["Delhi", "India"]
        """

        raw_args = self.get_raw_args(text)

        if not raw_args:
            return []

        return raw_args.split()

    # --------------------------------------------------------
    # SUBCOMMAND
    # --------------------------------------------------------

    def get_subcommand(self, text: str) -> Optional[str]:
        """
        Detect a subcommand for commands such as:

            /notes add Physics
            /notes list
            /notes delete 3

        Returns:
            add
            list
            delete
            None
        """

        command_name = self.get_command_name(text)

        if command_name not in {
            "notes",
            "memory",
            "profile",
        }:
            return None

        args = self.get_args(text)

        if not args:
            return None

        return args[0].lower()

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    def parse(self, text: str) -> Optional[Command]:
        """
        Parse an explicit command.

        Returns:
            Command object
            OR
            None if input is normal conversation.
        """

        if not self.is_command(text):
            return None

        name = self.get_command_name(text)
        raw_args = self.get_raw_args(text)
        args = self.get_args(text)
        subcommand = self.get_subcommand(text)

        return Command(
            name=name,
            args=args,
            raw_args=raw_args,
            subcommand=subcommand,
            is_command=True,
        )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    def validate(self, command: Optional[Command]) -> bool:
        """
        Validate a parsed command.
        """

        if command is None:
            return False

        if not command.is_command:
            return False

        if command.name not in self.commands:
            return False

        if (
            command.name in NO_ARGUMENT_COMMANDS
            and command.name != "help"
            and command.args
        ):
            # Extra arguments are allowed to exist;
            # Brain can decide how to handle them.
            return True

        return True

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    def get_help(self) -> Dict[str, str]:
        """
        Return command help information.

        Brain / AI can later turn this into a natural-language
        response.
        """

        return {
            "help": "Show available commands.",
            "calculate": "Calculate a mathematical expression.",
            "weather": "Get weather information.",
            "search": "Search the web.",
            "notes": "Create, read or manage notes.",
            "memory": "Store or manage memories.",
            "profile": "View or manage profile information.",
            "time": "Show current time/date.",
            "status": "Show AkshAI system status.",
            "clear": "Clear current conversation/context.",
            "exit": "Exit AkshAI.",
        }

    # --------------------------------------------------------
    # COMMAND INFO
    # --------------------------------------------------------

    def get_command_info(self, name: str) -> Optional[Dict]:
        """
        Return metadata for one command.
        """

        name = str(name).lower().strip()

        name = self.aliases.get(name, name)

        if name not in self.commands:
            return None

        return {
            "name": name,
            "supported": True,
            "requires_arguments": name not in NO_ARGUMENT_COMMANDS,
            "aliases": [
                alias
                for alias, target in self.aliases.items()
                if target == name
            ],
        }

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def get_status(self) -> Dict:
        """
        Return Command Engine status.
        """

        return {
            "engine": "command_engine",
            "version": "1.0",
            "status": "ready",
            "supported_commands": len(self.commands),
            "aliases": len(self.aliases),
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

command_engine = CommandEngine()


# ============================================================
# SIMPLE FUNCTIONS FOR BRAIN
# ============================================================

def is_command(text: str) -> bool:
    return command_engine.is_command(text)


def parse_command(text: str) -> Optional[Dict]:
    command = command_engine.parse(text)

    if command is None:
        return None

    return command.to_dict()


def command_name(text: str) -> Optional[str]:
    return command_engine.get_command_name(text)


def command_args(text: str) -> List[str]:
    return command_engine.get_args(text)


def command_help() -> Dict[str, str]:
    return command_engine.get_help()


# ============================================================
# SELF TEST
# ============================================================

def run_command_engine_test() -> bool:
    """
    Complete Command Engine test.
    """

    engine = CommandEngine()

    # --------------------------------------------------------
    # Positive command tests
    # --------------------------------------------------------

    positive_tests = [
        "/help",
        "/weather Delhi",
        "!weather Delhi",
        "/calculate 25 + 5",
        "/calc 25 + 5",
        "/search JEE latest news",
        "/web JEE",
        "/notes add Physics formulas",
        "/memory save my exam is tomorrow",
        "/profile",
        "/time",
        "/status",
        "/clear",
        "/exit",
        "/bye",
    ]

    for text in positive_tests:
        if not engine.is_command(text):
            print("FAILED command detection:", text)
            return False

    # --------------------------------------------------------
    # Negative tests
    # --------------------------------------------------------

    negative_tests = [
        "Hello AkshAI",
        "hello",
        "Explain Newton's second law",
        "What is photosynthesis?",
        "Calculate 25 + 5",
        "weather in Delhi",
        "search JEE news",
        "I want to remember something",
        "Tell me the time",
        "Can you help me?",
        "What is 25 + 5?",
        "",
        "   ",
        None,
    ]

    for text in negative_tests:
        if engine.is_command(text):
            print("FAILED normal conversation detection:", text)
            return False

    # --------------------------------------------------------
    # Parse tests
    # --------------------------------------------------------

    command = engine.parse("/weather Delhi India")

    if command is None:
        print("FAILED weather parsing")
        return False

    if command.name != "weather":
        print("FAILED command name")
        return False

    if command.args != ["Delhi", "India"]:
        print("FAILED arguments:", command.args)
        return False

    # --------------------------------------------------------
    # Alias test
    # --------------------------------------------------------

    command = engine.parse("/calc 100 / 4")

    if command is None:
        print("FAILED alias parsing")
        return False

    if command.name != "calculate":
        print("FAILED alias normalization")
        return False

    # --------------------------------------------------------
    # Subcommand test
    # --------------------------------------------------------

    command = engine.parse("/notes add Physics formulas")

    if command is None:
        print("FAILED notes parsing")
        return False

    if command.subcommand != "add":
        print("FAILED subcommand detection")
        return False

    # --------------------------------------------------------
    # Raw args test
    # --------------------------------------------------------

    raw = engine.get_raw_args("/search latest JEE news")

    if raw != "latest JEE news":
        print("FAILED raw argument extraction")
        return False

    # --------------------------------------------------------
    # Help test
    # --------------------------------------------------------

    help_data = engine.get_help()

    if "calculate" not in help_data:
        print("FAILED help data")
        return False

    # --------------------------------------------------------
    # Status test
    # --------------------------------------------------------

    status = engine.get_status()

    if status["status"] != "ready":
        print("FAILED status")
        return False

    # --------------------------------------------------------
    # Dictionary test
    # --------------------------------------------------------

    parsed = parse_command("/weather Delhi")

    if not isinstance(parsed, dict):
        print("FAILED dictionary output")
        return False

    if parsed["name"] != "weather":
        print("FAILED dictionary command name")
        return False

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print("Command detection tests passed:", len(positive_tests))
    print("Normal conversation tests passed:", len(negative_tests))
    print("Parsing tests passed")
    print("Alias tests passed")
    print("Subcommand tests passed")
    print("Help tests passed")
    print("Status tests passed")
    print("COMMAND ENGINE TEST PASSED ✅")

    return True


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":
    run_command_engine_test()