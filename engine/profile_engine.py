# ========================================================
# AKSHAI PROFILE ENGINE v1.0
# PART 1/3
# ========================================================

import json
import os
import tempfile

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ========================================================
# ENGINE CONFIGURATION
# ========================================================

ENGINE_NAME = "AkshAI Profile Engine"
ENGINE_VERSION = "1.0"

DATA_DIR = "/storage/emulated/0/AkshAI/data"
PROFILE_FILE = os.path.join(
    DATA_DIR,
    "profiles.json"
)

FOUNDER_USER_ID = "founder"


# ========================================================
# FOUNDER PROFILE
# ========================================================

FOUNDER_PROFILE = {
    "user_id": FOUNDER_USER_ID,

    "full_name": "Akshay Yadav",

    "nickname": "Akshu",

    "nicknames": [
        "Harshit",
        "Akshu"
    ],

    "age": 16,

    "role": "Founder & Developer",

    "started_akshai": "26 July 2026",

    "why_started_akshai": (
        "To build a powerful AI assistant that can help "
        "everyone in every possible useful way."
    ),

    "vision": (
        "To make AkshAI one of the world's best AI assistants."
    ),

    "class": "11th",

    "stream": "PCM",

    "school": "Government Inter College",

    "coaching": "Physics Wallah",

    "academic_goal": "JEE",

    "career_goal": "NDA Fighter Jet Pilot",

    "long_term_goals": [
        "Make AkshAI better",
        "Add more useful capabilities",
        "Build one of the world's best AI assistants"
    ],

    "skills": [
        "Coding & Programming"
    ],

    "hobbies": [
        "Playing cricket",
        "Singing",
        "Coding"
    ],

    "platform": [
        "Pydroid 3"
    ],

    "favourite_subject": "Mathematics",

    "current_goal": "To crack NDA",

    "important_akshai_features": (
        "Help everyone in every possible useful way."
    ),

    "languages": [
        "Hindi",
        "English",
        "Hinglish"
    ],

    "response_style": (
        "Natural, clear, useful and appropriately detailed."
    ),

    "bullets_numbering": True,

    "emojis": True,

    "complete_code_preference": True,

    "correct_mistakes": True,

    "special_preference": "I'm a boss",

    "father": {
        "name": "Mr. Lokendra Pal Singh",
        "relation": "Father of AkshAI founder/developer",
        "occupation": "Teacher",
        "qualifications": [
            "M.A.",
            "B.Ed."
        ],
        "qualities": [
            "Motivates Akshay day by day to achieve future goals",
            "Teaches Akshay the reality of life"
        ],
        "important_goal": "Akshay wants to make his father proud"
    },

    "mother": {
        "name": "Mrs. Rajani Yadav",
        "relation": "Mother of AkshAI founder/developer",
        "occupation": "Housewife",
        "qualities": [
            "Loves everyone",
            "Thinks less about herself and more about family"
        ]
    },

    "siblings": [
        {
            "name": "Akanksha Yadav",
            "relation": "Elder Sister",
            "interest": "Dancing"
        },
        {
            "name": "Pratigya Yadav",
            "relation": "Younger Sister",
            "interest": "Dancing"
        }
    ],

    "grandparents": {
        "grandmother": "Mrs. Yashoda Devi",
        "grandfather": "Mr. Prithviraj Singh Yadav"
    },

    "family_relationship": (
        "Very good relationships; everyone stays connected "
        "and together."
    ),

    "family_goal": "Make the family proud",

    "best_friend": "Hani Tiwari",

    "sports": [
        "Cricket"
    ],

    "video_game": "Garena Free Fire",

    "achievement": "Built AkshAI",

    "personal_strength": (
        "Whatever he decides to accomplish, he works to make it happen."
    ),

    "current_project": "AkshAI",

    "future_plan": "Build the world's best AI"
}


# ========================================================
# RESULT MODEL
# ========================================================

@dataclass
class ProfileResult:

    success: bool

    query: str = ""

    answer: str = ""

    error: str = ""

    error_type: str = ""

    source: str = ""

    profile: Optional[Dict[str, Any]] = None


# ========================================================
# UTILITY FUNCTIONS
# ========================================================

def clean_text(value: Any) -> str:

    if value is None:
        return ""

    return str(value).strip()


def normalize_query(query: Any) -> str:

    if query is None:
        return ""

    text = str(query).strip().lower()

    replacements = {
        "?": " ",
        "!": " ",
        ",": " ",
        ".": " ",
        ":": " ",
        ";": " ",
        "-": " ",
        "_": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(
        text.split()
    )


def now_utc() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


# ========================================================
# PROFILE ENGINE
# ========================================================

class ProfileEngine:

    def __init__(
        self,
        profile_file: str = PROFILE_FILE
    ):

        self.profile_file = profile_file

        self.profiles: Dict[str, Dict[str, Any]] = {}

        self._ensure_storage()

        self._load_profiles()


    # ====================================================
    # STORAGE
    # ====================================================

    def _ensure_storage(self):

        directory = os.path.dirname(
            self.profile_file
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )


    def _load_profiles(self):

        self.profiles = {}

        if not os.path.exists(
            self.profile_file
        ):
            return

        try:

            with open(
                self.profile_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):

                self.profiles = data

        except (
            OSError,
            json.JSONDecodeError,
            TypeError
        ):

            self.profiles = {}


    def _save_profiles(self) -> bool:

        directory = os.path.dirname(
            self.profile_file
        )

        try:

            os.makedirs(
                directory,
                exist_ok=True
            )

            fd, temp_path = tempfile.mkstemp(
                prefix="profiles_",
                suffix=".tmp",
                dir=directory
            )

            try:

                with os.fdopen(
                    fd,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        self.profiles,
                        file,
                        ensure_ascii=False,
                        indent=2
                    )

                    file.flush()

                    os.fsync(
                        file.fileno()
                    )

                os.replace(
                    temp_path,
                    self.profile_file
                )

                return True

            except Exception:

                try:
                    os.remove(temp_path)
                except OSError:
                    pass

                return False

        except OSError:

            return False


    # ====================================================
    # IDENTITY
    # ====================================================

    def is_founder(
        self,
        user_id: str
    ) -> bool:

        return clean_text(
            user_id
        ).lower() == FOUNDER_USER_ID


    def get_display_name(
        self,
        user_id: str
    ) -> str:

        user_id = clean_text(
            user_id
        )

        if self.is_founder(
            user_id
        ):
            return "Akshay Boss"

        profile = self.profiles.get(
            user_id
        )

        if not profile:
            return "User"

        nickname = clean_text(
            profile.get("nickname", "")
        )

        if nickname:
            return nickname

        nicknames = profile.get(
            "nicknames",
            []
        )

        if isinstance(
            nicknames,
            list
        ):

            for name in nicknames:

                name = clean_text(name)

                if name:
                    return name

        return clean_text(
            profile.get(
                "full_name",
                "User"
            )
        ) or "User"


    def get_profile(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:

        user_id = clean_text(
            user_id
        )

        if self.is_founder(
            user_id
        ):

            return dict(
                FOUNDER_PROFILE
            )

        profile = self.profiles.get(
            user_id
        )

        if profile is None:
            return None

        return dict(
            profile
        )


    # ====================================================
    # CREATE PROFILE
    # ====================================================

    def create_profile(
        self,
        user_id: str,
        full_name: str,
        nickname: str = "",
        nicknames: Optional[List[str]] = None,
        **extra_fields: Any,
    ) -> ProfileResult:

        user_id = clean_text(
            user_id
        )

        full_name = clean_text(
            full_name
        )

        nickname = clean_text(
            nickname
        )

        if not user_id:

            return ProfileResult(
                success=False,
                error="User ID is required.",
                error_type="invalid_user_id"
            )

        if self.is_founder(
            user_id
        ):

            return ProfileResult(
                success=False,
                error=(
                    "Founder profile is already predefined."
                ),
                error_type="founder_profile"
            )

        if not full_name:

            return ProfileResult(
                success=False,
                error="Full name is required.",
                error_type="invalid_name"
            )

        if user_id in self.profiles:

            return ProfileResult(
                success=False,
                error="Profile already exists.",
                error_type="profile_exists"
            )

        if nicknames is None:

            nicknames = []

        cleaned_nicknames = []

        for item in nicknames:

            item = clean_text(
                item
            )

            if item:
                cleaned_nicknames.append(
                    item
                )

        if (
            nickname
            and nickname not in cleaned_nicknames
        ):

            cleaned_nicknames.insert(
                0,
                nickname
            )

        timestamp = now_utc()

        profile = {

            "user_id": user_id,

            "full_name": full_name,

            "nickname": nickname,

            "nicknames": cleaned_nicknames,

            "created_at": timestamp,

            "updated_at": timestamp,
        }

        profile.update(
            extra_fields
        )

        self.profiles[
            user_id
        ] = profile

        if not self._save_profiles():

            self.profiles.pop(
                user_id,
                None
            )

            return ProfileResult(
                success=False,
                error="Could not save profile.",
                error_type="storage_error"
            )

        return ProfileResult(
            success=True,
            query=user_id,
            answer=self._format_user_profile(
                profile
            ),
            source="user_profile",
            profile=dict(profile)
        )


    # ====================================================
    # UPDATE PROFILE
    # ====================================================

    def update_profile(
        self,
        user_id: str,
        **updates: Any
    ) -> ProfileResult:

        user_id = clean_text(
            user_id
        )

        if not user_id:

            return ProfileResult(
                success=False,
                error="User ID is required.",
                error_type="invalid_user_id"
            )

        if self.is_founder(
            user_id
        ):

            return ProfileResult(
                success=False,
                error="Founder profile cannot be modified here.",
                error_type="founder_profile"
            )

        if user_id not in self.profiles:

            return ProfileResult(
                success=False,
                error="Profile not found.",
                error_type="profile_not_found"
            )

        profile = dict(
            self.profiles[user_id]
        )

        for key, value in updates.items():

            if key == "full_name":
                value = clean_text(value)

                if not value:
                    continue

            if key == "nickname":
                value = clean_text(value)

            profile[key] = value

        profile["updated_at"] = now_utc()

        old_profile = self.profiles[
            user_id
        ]

        self.profiles[
            user_id
        ] = profile

        if not self._save_profiles():

            self.profiles[
                user_id
            ] = old_profile

            return ProfileResult(
                success=False,
                error="Could not save updated profile.",
                error_type="storage_error"
            )

        return ProfileResult(
            success=True,
            query=user_id,
            answer=self._format_user_profile(
                profile
            ),
            source="user_profile",
            profile=dict(profile)
        )


    # ====================================================
    # DELETE PROFILE
    # ====================================================

    def delete_profile(
        self,
        user_id: str
    ) -> ProfileResult:

        user_id = clean_text(
            user_id
        )

        if not user_id:

            return ProfileResult(
                success=False,
                error="User ID is required.",
                error_type="invalid_user_id"
            )

        if self.is_founder(
            user_id
        ):

            return ProfileResult(
                success=False,
                error="Founder profile cannot be deleted.",
                error_type="founder_profile"
            )

        if user_id not in self.profiles:

            return ProfileResult(
                success=False,
                error="Profile not found.",
                error_type="profile_not_found"
            )

        deleted_profile = self.profiles.pop(
            user_id
        )

        if not self._save_profiles():

            self.profiles[
                user_id
            ] = deleted_profile

            return ProfileResult(
                success=False,
                error="Could not delete profile.",
                error_type="storage_error"
            )

        return ProfileResult(
            success=True,
            query=user_id,
            answer="Profile deleted successfully.",
            source="user_profile",
            profile=dict(deleted_profile)
        )
# ========================================================
# AKSHAI PROFILE ENGINE v1.0
# PART 2/3
# Paste directly after Part 1
# ========================================================


    # ====================================================
    # FOUNDER ANSWERS
    # ====================================================

    def _founder_about_answer(self):

        return (
            "👑 **Akshay Yadav** is the Founder & Developer "
            "of AkshAI.\n\n"

            "🎓 He is a Class 11th PCM student passionate "
            "about Coding & Programming.\n\n"

            "🎯 Academic Goal: JEE\n"
            "✈️ Career Goal: NDA Fighter Jet Pilot\n"
            "💻 Main Skill: Coding & Programming\n"
            "🏏 Hobbies: Cricket, Singing & Coding\n"
            "🤖 Started AkshAI: 26 July 2026\n\n"

            "💡 Vision: To build AkshAI into one of the "
            "world's best AI assistants.\n\n"

            "💪 Mindset: Whatever he decides to accomplish, "
            "he works to make it happen."
        )


    def _developer_answer(self):

        return (
            "💻 **Akshay Yadav** is the Founder & Developer "
            "of AkshAI.\n\n"

            "🎓 Class: 11th | Stream: PCM\n"
            "🏫 School: Government Inter College\n"
            "📚 Coaching: Physics Wallah\n"
            "🎯 Academic Goal: JEE\n"
            "✈️ Career Dream: NDA Fighter Jet Pilot\n"
            "💻 Skill: Coding & Programming\n"
            "🛠️ Platform: Pydroid 3\n\n"

            "🤖 His vision is to make AkshAI a powerful AI "
            "assistant that can help everyone in every "
            "possible useful way."
        )


    def _founder_short_answer(self):

        return (
            "👑 AkshAI was founded and developed by "
            "**Akshay Yadav**.\n\n"
            "He is a Class 11th PCM student and the creator "
            "of AkshAI."
        )


    def _parents_answer(self):

        return (
            "👨‍👩‍👦 **Akshay Yadav's Parents**\n\n"

            "👨 Father: **Mr. Lokendra Pal Singh**\n"
            "• Teacher\n"
            "• M.A., B.Ed.\n"
            "• Motivates Akshay to achieve his future goals.\n"
            "• Teaches him the reality of life.\n\n"

            "👩 Mother: **Mrs. Rajani Yadav**\n"
            "• Housewife\n"
            "• Loves everyone.\n"
            "• Thinks less about herself and more about family.\n\n"

            "❤️ Akshay wants to make his parents and family proud."
        )


    def _father_answer(self):

        return (
            "👨 **Mr. Lokendra Pal Singh** is Akshay "
            "Yadav's father.\n\n"

            "👨‍🏫 Occupation: Teacher\n"
            "🎓 Qualifications: M.A., B.Ed.\n\n"

            "💪 He motivates Akshay day by day to achieve "
            "his future goals and teaches him the reality "
            "of life.\n\n"

            "❤️ Akshay wants to make his father proud."
        )


    def _mother_answer(self):

        return (
            "👩 **Mrs. Rajani Yadav** is Akshay Yadav's mother.\n\n"

            "🏠 Occupation: Housewife\n\n"

            "❤️ She loves everyone and thinks less about "
            "herself and more about her family."
        )


    def _best_friend_answer(self):

        return (
            "🫂 Akshay Yadav's best friend is "
            "**Hani Tiwari**.\n\n"

            "She is listed in his founder profile as "
            "his best friend."
        )


    def _siblings_answer(self):

        return (
            "👧👧 **Akshay Yadav's Sisters**\n\n"

            "1. 👧 **Akanksha Yadav** — Elder Sister\n"
            "2. 👧 **Pratigya Yadav** — Younger Sister\n\n"

            "💃 Both are interested in dancing."
        )


    def _grandparents_answer(self):

        return (
            "👵 **Grandmother:** Mrs. Yashoda Devi\n"
            "👴 **Grandfather:** Mr. Prithviraj Singh Yadav\n\n"

            "❤️ They have a very good relationship with "
            "Akshay and the family stays connected and together."
        )


    def _family_answer(self):

        return (
            "👨‍👩‍👧‍👦 **Akshay Yadav's Family**\n\n"

            "👨 Father: Mr. Lokendra Pal Singh\n"
            "👩 Mother: Mrs. Rajani Yadav\n"
            "👧 Elder Sister: Akanksha Yadav\n"
            "👧 Younger Sister: Pratigya Yadav\n"
            "👵 Grandmother: Mrs. Yashoda Devi\n"
            "👴 Grandfather: Mr. Prithviraj Singh Yadav\n\n"

            "❤️ The family has very good relationships "
            "and stays connected and together."
        )


    def _akshai_answer(self):

        return (
            "🤖 **AkshAI** is an AI assistant project founded "
            "and developed by Akshay Yadav.\n\n"

            "🎯 Goal: Help everyone in every possible useful way.\n"
            "💡 Vision: Build one of the world's best AI assistants.\n"
            "🚀 Started: 26 July 2026\n"
            "💻 Developer: Akshay Yadav"
        )


    # ====================================================
    # FOUNDER QUERY ROUTER
    # ====================================================

    def answer_founder_query(
        self,
        query: str
    ) -> ProfileResult:

        q = normalize_query(
            query
        )

        if not q:

            return ProfileResult(
                success=False,
                query=clean_text(query),
                error="Empty query.",
                error_type="empty_query"
            )


        # ------------------------------------------------
        # BEST FRIEND
        # ------------------------------------------------

        if (
            "best friend" in q
            or "bestfriend" in q
            or "closest friend" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._best_friend_answer(),
                source="founder_profile"
            )
               # ------------------------------------------------
        # GRANDPARENTS
        # ------------------------------------------------

        if (
            "grandparent" in q
            or "grand parents" in q
            or "grandmother" in q
            or "grandfather" in q
            or "grandma" in q
            or "grandpa" in q
            or "dadi" in q
            or "nani" in q
            or "dada" in q
            or "nana" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._grandparents_answer(),
                source="founder_profile"
            )

        # ------------------------------------------------
        # PARENTS
        # ------------------------------------------------

        if (
            "parents" in q
            or "parent" in q
            or "mother and father" in q
            or "mom and dad" in q
            or "maa baap" in q
            or "mata pita" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._parents_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # FATHER
        # ------------------------------------------------

        if (
            "father" in q
            or "dad" in q
            or "papa" in q
            or "pita" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._father_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # MOTHER
        # ------------------------------------------------

        if (
            "mother" in q
            or "mom" in q
            or "maa" in q
            or "mummy" in q
            or "mama" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._mother_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # SIBLINGS / SISTERS
        # ------------------------------------------------

        if (
            "sister" in q
            or "sisters" in q
            or "sibling" in q
            or "siblings" in q
            or "behen" in q
            or "bahen" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._siblings_answer(),
                source="founder_profile"
            )

        # ------------------------------------------------
        # FAMILY
        # ------------------------------------------------

        if (
            "family" in q
            or "family members" in q
            or "parivaar" in q
            or "pariwar" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._family_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # AKSHAI
        # ------------------------------------------------

        if (
            "what is akshai" in q
            or "whats akshai" in q
            or "about akshai" in q
            or "tell me about akshai" in q
            or "akshai project" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._akshai_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # DEVELOPER / FOUNDER
        # ------------------------------------------------

        if (
            "developer" in q
            or "programmer" in q
            or "creator" in q
            or "founder" in q
            or "who made akshai" in q
            or "who created akshai" in q
            or "who developed akshai" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._developer_answer(),
                source="founder_profile"
            )


        # ------------------------------------------------
        # AKSHAY PROFILE
        # ------------------------------------------------

        if (
            "who is akshay" in q
            or "who is akshay yadav" in q
            or "tell me about akshay" in q
            or "tell me about akshay yadav" in q
            or "about akshay yadav" in q
            or "akshay yadav" in q
        ):

            return ProfileResult(
                success=True,
                query=query,
                answer=self._founder_about_answer(),
                source="founder_profile"
            )


        return ProfileResult(
            success=False,
            query=query,
            error="Founder information not found.",
            error_type="founder_info_not_found"
        )


    # ====================================================
    # FORMAT USER PROFILE
    # ====================================================

    def _format_user_profile(
        self,
        profile: Optional[Dict[str, Any]]
    ) -> str:

        if not profile:
            return "❌ No profile found."


        name = clean_text(
            profile.get(
                "full_name",
                "Unknown"
            )
        ) or "Unknown"


        nicknames = profile.get(
            "nicknames",
            []
        )

        if isinstance(
            nicknames,
            str
        ):

            nicknames = [
                nicknames
            ]


        role = clean_text(
            profile.get(
                "role",
                ""
            )
        )

        age = profile.get(
            "age",
            ""
        )

        class_name = clean_text(
            profile.get(
                "class",
                ""
            )
        )

        stream = clean_text(
            profile.get(
                "stream",
                ""
            )
        )

        school = clean_text(
            profile.get(
                "school",
                ""
            )
        )

        coaching = clean_text(
            profile.get(
                "coaching",
                ""
            )
        )

        academic_goal = clean_text(
            profile.get(
                "academic_goal",
                ""
            )
        )

        career_goal = clean_text(
            profile.get(
                "career_goal",
                ""
            )
        )

        skills = profile.get(
            "skills",
            []
        )

        hobbies = profile.get(
            "hobbies",
            []
        )

        languages = profile.get(
            "languages",
            []
        )


        if isinstance(
            skills,
            str
        ):
            skills = [skills]

        if isinstance(
            hobbies,
            str
        ):
            hobbies = [hobbies]

        if isinstance(
            languages,
            str
        ):
            languages = [languages]


        answer = (
            f"👤 **{name}**\n\n"
        )


        if nicknames:

            cleaned = [
                clean_text(x)
                for x in nicknames
                if clean_text(x)
            ]

            if cleaned:

                answer += (
                    "🏷️ Nicknames: "
                    + ", ".join(cleaned)
                    + "\n"
                )


        if age != "":

            answer += (
                f"🎂 Age: {age}\n"
            )


        if role:

            answer += (
                f"💼 Role: {role}\n"
            )


        if class_name:

            answer += (
                f"🎓 Class: {class_name}\n"
            )


        if stream:

            answer += (
                f"📚 Stream: {stream}\n"
            )


        if school:

            answer += (
                f"🏫 School: {school}\n"
            )


        if coaching:

            answer += (
                f"📖 Coaching: {coaching}\n"
            )


        if academic_goal:

            answer += (
                f"🎯 Academic Goal: "
                f"{academic_goal}\n"
            )


        if career_goal:

            answer += (
                f"✈️ Career Goal: "
                f"{career_goal}\n"
            )


        if skills:

            answer += (
                "💻 Skills: "
                + ", ".join(
                    str(x)
                    for x in skills
                    if clean_text(x)
                )
                + "\n"
            )


        if hobbies:

            answer += (
                "🎨 Hobbies: "
                + ", ".join(
                    str(x)
                    for x in hobbies
                    if clean_text(x)
                )
                + "\n"
            )


        if languages:

            answer += (
                "🌐 Languages: "
                + ", ".join(
                    str(x)
                    for x in languages
                    if clean_text(x)
                )
                + "\n"
            )


        return answer.strip()
# ========================================================
# AKSHAI PROFILE ENGINE v1.0
# PART 3/3
# Paste directly after Part 2
# ========================================================


    # ====================================================
    # MAIN PROFILE QUERY
    # ====================================================

    def answer_query(
        self,
        query: str,
        user_id: str = FOUNDER_USER_ID
    ) -> ProfileResult:

        original_query = clean_text(
            query
        )

        q = normalize_query(
            query
        )

        user_id = clean_text(
            user_id
        )


        if not q:

            return ProfileResult(
                success=False,
                query=original_query,
                error="Empty query.",
                error_type="empty_query"
            )


        # ------------------------------------------------
        # FOUNDER QUESTIONS
        # ------------------------------------------------

        founder_result = self.answer_founder_query(
            query
        )

        if founder_result.success:

            return founder_result


        # ------------------------------------------------
        # CURRENT USER / "ME" QUESTIONS
        # ------------------------------------------------

        me_patterns = [
            "who am i",
            "who i am",
            "tell me about me",
            "about me",
            "my profile",
            "my information",
            "my details",
            "what do you know about me",
            "mere bare mein batao",
            "mere baare mein batao",
            "main kaun hu",
            "mai kaun hu",
            "mera profile",
            "meri information",
            "meri details",
        ]


        if any(
            pattern in q
            for pattern in me_patterns
        ):

            profile = self.get_profile(
                user_id
            )

            if profile is None:

                return ProfileResult(
                    success=False,
                    query=original_query,
                    error=(
                        "No saved profile found for this user."
                    ),
                    error_type="profile_not_found",
                    source="user_profile"
                )


            return ProfileResult(
                success=True,
                query=original_query,
                answer=self._format_user_profile(
                    profile
                ),
                source=(
                    "founder_profile"
                    if self.is_founder(user_id)
                    else "user_profile"
                ),
                profile=profile
            )


        # ------------------------------------------------
        # DIRECT NAME QUERY
        # ------------------------------------------------

        profile = self.get_profile(
            user_id
        )

        if profile:

            name = normalize_query(
                profile.get(
                    "full_name",
                    ""
                )
            )

            if (
                name
                and name in q
            ):

                return ProfileResult(
                    success=True,
                    query=original_query,
                    answer=self._format_user_profile(
                        profile
                    ),
                    source="user_profile",
                    profile=profile
                )


        # ------------------------------------------------
        # UNKNOWN
        # ------------------------------------------------

        return ProfileResult(
            success=False,
            query=original_query,
            error="Profile information not found.",
            error_type="profile_info_not_found"
        )


    # ====================================================
    # PROFILE QUERY ALIAS
    # ====================================================

    def answer_profile_query(
        self,
        query: str,
        user_id: str = FOUNDER_USER_ID
    ) -> ProfileResult:

        return self.answer_query(
            query,
            user_id
        )


    # ====================================================
    # STATUS
    # ====================================================

    def status(self) -> Dict[str, Any]:

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "founder_id": FOUNDER_USER_ID,
            "founder_name": FOUNDER_PROFILE[
                "full_name"
            ],
            "stored_user_profiles": len(
                self.profiles
            ),
            "storage_file": self.profile_file,
            "storage_exists": os.path.exists(
                self.profile_file
            ),
        }


# ========================================================
# GLOBAL PROFILE ENGINE
# ========================================================

_profile_engine = ProfileEngine()


# ========================================================
# PUBLIC FUNCTIONS
# ========================================================

def create_profile(
    user_id: str,
    full_name: str,
    nickname: str = "",
    nicknames: Optional[List[str]] = None,
    **extra_fields: Any,
) -> ProfileResult:

    return _profile_engine.create_profile(
        user_id,
        full_name,
        nickname,
        nicknames,
        **extra_fields
    )


def get_profile(
    user_id: str
) -> Optional[Dict[str, Any]]:

    return _profile_engine.get_profile(
        user_id
    )


def get_display_name(
    user_id: str
) -> str:

    return _profile_engine.get_display_name(
        user_id
    )


def update_profile(
    user_id: str,
    **updates: Any
) -> ProfileResult:

    return _profile_engine.update_profile(
        user_id,
        **updates
    )


def delete_profile(
    user_id: str
) -> ProfileResult:

    return _profile_engine.delete_profile(
        user_id
    )


def answer_query(
    query: str,
    user_id: str = FOUNDER_USER_ID
) -> ProfileResult:

    return _profile_engine.answer_query(
        query,
        user_id
    )


def answer_profile_query(
    query: str,
    user_id: str = FOUNDER_USER_ID
) -> ProfileResult:

    return _profile_engine.answer_profile_query(
        query,
        user_id
    )


def is_founder(
    user_id: str
) -> bool:

    return _profile_engine.is_founder(
        user_id
    )


def profile_status() -> Dict[str, Any]:

    return _profile_engine.status()


# ========================================================
# SELF TEST
# ========================================================

def run_self_test():

    print(
        "AkshAI Profile Engine v1.0"
    )

    print(
        "=" * 55
    )


    # ----------------------------------------------------
    # TEMP TEST ENGINE
    # ----------------------------------------------------

    test_dir = os.path.join(
        DATA_DIR,
        "_profile_engine_test"
    )

    os.makedirs(
        test_dir,
        exist_ok=True
    )

    test_file = os.path.join(
        test_dir,
        "test_profiles.json"
    )


    try:

        if os.path.exists(
            test_file
        ):

            os.remove(
                test_file
            )


        engine = ProfileEngine(
            profile_file=test_file
        )


        passed = 0


        # ------------------------------------------------
        # 1. FOUNDER PROFILE
        # ------------------------------------------------

        founder = engine.get_profile(
            FOUNDER_USER_ID
        )

        assert founder is not None
        assert founder["full_name"] == "Akshay Yadav"

        print(
            "Founder profile test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 2. FOUNDER IDENTITY
        # ------------------------------------------------

        assert engine.is_founder(
            "founder"
        )

        assert not engine.is_founder(
            "user123"
        )

        print(
            "Founder identity test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 3. FOUNDER DISPLAY NAME
        # ------------------------------------------------

        assert (
            engine.get_display_name(
                "founder"
            )
            == "Akshay Boss"
        )

        print(
            "Founder display-name test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 4. USER CREATION
        # ------------------------------------------------

        result = engine.create_profile(
            user_id="user1",
            full_name="Test User",
            nickname="Tester"
        )

        assert result.success
        assert result.profile is not None

        print(
            "User creation test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 5. MULTI USER IDENTITY
        # ------------------------------------------------

        result2 = engine.create_profile(
            user_id="user2",
            full_name="Second User",
            nickname="Second"
        )

        assert result2.success

        assert (
            engine.get_display_name(
                "user1"
            )
            == "Tester"
        )

        assert (
            engine.get_display_name(
                "user2"
            )
            == "Second"
        )

        print(
            "Multi-user identity test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 6. FOUNDER ANSWER
        # ------------------------------------------------

        result = engine.answer_query(
            "Who is Akshay Yadav?"
        )

        assert result.success
        assert "Akshay Yadav" in result.answer

        print(
            "Founder answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 7. DEVELOPER ANSWER
        # ------------------------------------------------

        result = engine.answer_query(
            "Who is the developer of AkshAI?"
        )

        assert result.success
        assert "Akshay Yadav" in result.answer

        print(
            "Developer answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 8. PARENTS ANSWER
        # ------------------------------------------------

        result = engine.answer_query(
            "Who are Akshay Yadav's parents?"
        )

        assert result.success
        assert "Lokendra Pal Singh" in result.answer
        assert "Rajani Yadav" in result.answer

        print(
            "Parents answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 9. FATHER ANSWER
        # ------------------------------------------------

        result = engine.answer_query(
            "Who is Akshay's father?"
        )

        assert result.success
        assert "Lokendra Pal Singh" in result.answer

        print(
            "Father answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 10. MOTHER ANSWER
        # ------------------------------------------------

        result = engine.answer_query(
            "Who is Akshay's mother?"
        )

        assert result.success
        assert "Rajani Yadav" in result.answer

        print(
            "Mother answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 11. BEST FRIEND
        # ------------------------------------------------

        result = engine.answer_query(
            "Who is Akshay Yadav's best friend?"
        )

        assert result.success
        assert "Hani Tiwari" in result.answer

        print(
            "Best friend answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 12. SISTERS
        # ------------------------------------------------

        result = engine.answer_query(
            "Who are Akshay Yadav's sisters?"
        )

        assert result.success
        assert "Akanksha Yadav" in result.answer
        assert "Pratigya Yadav" in result.answer

        print(
            "Siblings answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 13. GRANDPARENTS
        # ------------------------------------------------

        result = engine.answer_query(
            "Who are Akshay Yadav's grandparents?"
        )

        assert result.success
        assert "Yashoda Devi" in result.answer
        assert "Prithviraj Singh Yadav" in result.answer

        print(
            "Grandparents answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 14. AKSHAI
        # ------------------------------------------------

        result = engine.answer_query(
            "Tell me about AkshAI"
        )

        assert result.success
        assert "AkshAI" in result.answer

        print(
            "AkshAI answer test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 15. CURRENT USER PROFILE
        # ------------------------------------------------

        result = engine.answer_query(
            "Who am I?",
            user_id="user1"
        )

        assert result.success
        assert "Test User" in result.answer

        print(
            "Current user profile test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 16. PERSISTENCE
        # ------------------------------------------------

        engine2 = ProfileEngine(
            profile_file=test_file
        )

        loaded = engine2.get_profile(
            "user1"
        )

        assert loaded is not None
        assert loaded["full_name"] == "Test User"

        print(
            "Persistence test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 17. UPDATE
        # ------------------------------------------------

        result = engine2.update_profile(
            "user1",
            full_name="Updated User",
            nickname="Updated"
        )

        assert result.success

        updated = engine2.get_profile(
            "user1"
        )

        assert updated is not None
        assert updated["full_name"] == "Updated User"
        assert updated["nickname"] == "Updated"

        print(
            "Profile update test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 18. DELETE
        # ------------------------------------------------

        result = engine2.delete_profile(
            "user2"
        )

        assert result.success

        assert (
            engine2.get_profile(
                "user2"
            )
            is None
        )

        print(
            "Profile deletion test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 19. UNKNOWN USER
        # ------------------------------------------------

        result = engine2.answer_query(
            "Who am I?",
            user_id="unknown_user"
        )

        assert not result.success
        assert (
            result.error_type
            == "profile_not_found"
        )

        print(
            "Unknown user handling test passed"
        )

        passed += 1


        # ------------------------------------------------
        # 20. STATUS
        # ------------------------------------------------

        status = engine2.status()

        assert (
            status["engine"]
            == ENGINE_NAME
        )

        assert (
            status["version"]
            == ENGINE_VERSION
        )

        print(
            "Status test passed"
        )

        passed += 1


        # ------------------------------------------------
        # FINAL
        # ------------------------------------------------

        print(
            "-" * 55
        )

        print(
            f"Tests passed: {passed}/20"
        )

        if passed == 20:

            print(
                "PROFILE ENGINE TEST PASSED ✅"
            )

            return True

        print(
            "PROFILE ENGINE TEST FAILED ❌"
        )

        return False


    finally:

        try:

            if os.path.exists(
                test_file
            ):
                os.remove(
                    test_file
                )

        except OSError:
            pass


# ========================================================
# RUN DIRECTLY
# ========================================================

if __name__ == "__main__":

    run_self_test()