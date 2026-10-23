"""
AkshAI Notes Engine v1.0
Persistent note management with JSON storage.
"""

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


ENGINE_NAME = "AkshAI Notes Engine"
ENGINE_VERSION = "1.0"

BASE_DIR = "/storage/emulated/0/AkshAI"
NOTES_DIR = os.path.join(BASE_DIR, "data")
NOTES_FILE = os.path.join(NOTES_DIR, "notes.json")


# ==========================================================
# DATA MODEL
# ==========================================================

@dataclass
class Note:
    note_id: str
    title: str
    content: str
    category: str = "general"
    tags: Optional[List[str]] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

        if not self.created_at:
            self.created_at = datetime.now().isoformat(
                timespec="seconds"
            )

        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            note_id=str(data.get("note_id", "")),
            title=str(data.get("title", "")),
            content=str(data.get("content", "")),
            category=str(data.get("category", "general")),
            tags=list(data.get("tags", [])),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )


# ==========================================================
# RESULT MODEL
# ==========================================================

@dataclass
class NoteResult:
    success: bool
    action: str
    message: str = ""
    note: Optional[Dict[str, Any]] = None
    notes: Optional[List[Dict[str, Any]]] = None
    count: int = 0
    error: str = ""
    error_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==========================================================
# NOTES ENGINE
# ==========================================================

class NotesEngine:

    def __init__(self, notes_file: str = NOTES_FILE):
        self.notes_file = notes_file
        self.notes: List[Note] = []

        self._ensure_storage()
        self.load()

    # ------------------------------------------------------
    # STORAGE
    # ------------------------------------------------------

    def _ensure_storage(self):
        directory = os.path.dirname(self.notes_file)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.notes_file):
            self._write_file([])

    def _write_file(self, data: List[Dict[str, Any]]) -> bool:
        try:
            directory = os.path.dirname(self.notes_file)

            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            temp_file = self.notes_file + ".tmp"

            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            os.replace(temp_file, self.notes_file)

            return True

        except Exception:
            return False

    def _save(self) -> bool:
        return self._write_file(
            [note.to_dict() for note in self.notes]
        )

    def load(self) -> NoteResult:
        try:
            with open(
                self.notes_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                data = []

            self.notes = []

            for item in data:
                if not isinstance(item, dict):
                    continue

                try:
                    note = Note.from_dict(item)

                    if note.title.strip():
                        self.notes.append(note)

                except Exception:
                    continue

            return NoteResult(
                success=True,
                action="load",
                message="Notes loaded successfully.",
                count=len(self.notes)
            )

        except Exception as error:
            self.notes = []

            return NoteResult(
                success=False,
                action="load",
                error=str(error),
                error_type="load_error"
            )

    # ------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        if not isinstance(text, str):
            return ""

        text = text.strip().lower()
        text = re.sub(r"\s+", " ", text)

        return text

    @staticmethod
    def clean_title(title: str) -> str:
        if not isinstance(title, str):
            return ""

        title = title.strip()
        title = re.sub(r"\s+", " ", title)

        return title

    @staticmethod
    def clean_content(content: str) -> str:
        if not isinstance(content, str):
            return ""

        return content.strip()

    @staticmethod
    def normalize_tags(tags) -> List[str]:
        if tags is None:
            return []

        if isinstance(tags, str):
            tags = re.split(r"[,;]", tags)

        if not isinstance(tags, (list, tuple, set)):
            return []

        result = []

        for tag in tags:
            tag = str(tag).strip().lower()

            if tag and tag not in result:
                result.append(tag)

        return result

    # ------------------------------------------------------
    # ID GENERATION
    # ------------------------------------------------------

    def _generate_id(self) -> str:

        numbers = []

        for note in self.notes:
            match = re.search(
                r"(\d+)$",
                note.note_id
            )

            if match:
                numbers.append(
                    int(match.group(1))
                )

        next_number = max(
            numbers,
            default=0
        ) + 1

        return f"note_{next_number:04d}"

    # ------------------------------------------------------
    # ADD NOTE
    # ------------------------------------------------------

    def add(
        self,
        title: str,
        content: str,
        category: str = "general",
        tags=None
    ) -> NoteResult:

        title = self.clean_title(title)
        content = self.clean_content(content)

        if not title:
            return NoteResult(
                success=False,
                action="add",
                error="Note title cannot be empty.",
                error_type="invalid_title"
            )

        if not content:
            return NoteResult(
                success=False,
                action="add",
                error="Note content cannot be empty.",
                error_type="invalid_content"
            )

        category = (
            self.clean_title(category)
            or "general"
        )

        tags = self.normalize_tags(tags)

        normalized_title = self.normalize(title)

        # Prevent duplicate titles.
        for note in self.notes:
            if self.normalize(note.title) == normalized_title:
                return NoteResult(
                    success=False,
                    action="add",
                    message="A note with this title already exists.",
                    note=note.to_dict(),
                    error="Duplicate note title.",
                    error_type="duplicate"
                )

        note = Note(
            note_id=self._generate_id(),
            title=title,
            content=content,
            category=category,
            tags=tags
        )

        self.notes.append(note)

        if not self._save():
            self.notes.pop()

            return NoteResult(
                success=False,
                action="add",
                error="Could not save note.",
                error_type="save_error"
            )

        return NoteResult(
            success=True,
            action="add",
            message="Note added successfully.",
            note=note.to_dict(),
            count=1
        )

    # ------------------------------------------------------
    # GET NOTE
    # ------------------------------------------------------

    def get(self, note_id: str) -> NoteResult:

        note_id = str(note_id).strip()

        for note in self.notes:
            if note.note_id == note_id:
                return NoteResult(
                    success=True,
                    action="get",
                    note=note.to_dict(),
                    count=1
                )

        return NoteResult(
            success=False,
            action="get",
            error="Note not found.",
            error_type="not_found"
        )

    # ------------------------------------------------------
    # SEARCH NOTES
    # ------------------------------------------------------

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 10
    ) -> NoteResult:

        query = self.normalize(query)

        category = (
            self.normalize(category)
            if category
            else None
        )

        tag = (
            self.normalize(tag)
            if tag
            else None
        )

        if not query and not category and not tag:
            return NoteResult(
                success=False,
                action="search",
                error="Search query cannot be empty.",
                error_type="invalid_query"
            )

        try:
            limit = max(1, int(limit))
        except Exception:
            limit = 10

        query_words = set(query.split())

        scored = []

        for note in self.notes:

            if category:
                if self.normalize(
                    note.category
                ) != category:
                    continue

            note_tags = self.normalize_tags(
                note.tags
            )

            if tag and tag not in note_tags:
                continue

            title = self.normalize(note.title)
            content = self.normalize(note.content)

            score = 0

            if query:

                if query == title:
                    score += 100

                if query in title:
                    score += 60

                if query in content:
                    score += 30

                title_words = set(title.split())
                content_words = set(content.split())

                score += len(
                    query_words & title_words
                ) * 15

                score += len(
                    query_words & content_words
                ) * 5

                for note_tag in note_tags:
                    if note_tag in query_words:
                        score += 8

            else:
                score = 1

            if score > 0:
                scored.append(
                    (score, note)
                )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1].updated_at
            ),
            reverse=True
        )

        results = [
            note.to_dict()
            for _, note in scored[:limit]
        ]

        return NoteResult(
            success=True,
            action="search",
            message=f"Found {len(results)} note(s).",
            notes=results,
            count=len(results)
        )

    # ------------------------------------------------------
    # UPDATE NOTE
    # ------------------------------------------------------

    def update(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags=None
    ) -> NoteResult:

        note_id = str(note_id).strip()

        target = None

        for note in self.notes:
            if note.note_id == note_id:
                target = note
                break

        if target is None:
            return NoteResult(
                success=False,
                action="update",
                error="Note not found.",
                error_type="not_found"
            )

        old_data = target.to_dict()

        if title is not None:
            title = self.clean_title(title)

            if not title:
                return NoteResult(
                    success=False,
                    action="update",
                    error="Note title cannot be empty.",
                    error_type="invalid_title"
                )

            target.title = title

        if content is not None:
            content = self.clean_content(content)

            if not content:
                return NoteResult(
                    success=False,
                    action="update",
                    error="Note content cannot be empty.",
                    error_type="invalid_content"
                )

            target.content = content

        if category is not None:
            category = self.clean_title(category)

            target.category = (
                category or "general"
            )

        if tags is not None:
            target.tags = self.normalize_tags(tags)

        target.updated_at = datetime.now().isoformat(
            timespec="seconds"
        )

        if not self._save():

            target.title = old_data["title"]
            target.content = old_data["content"]
            target.category = old_data["category"]
            target.tags = old_data["tags"]
            target.updated_at = old_data["updated_at"]

            return NoteResult(
                success=False,
                action="update",
                error="Could not save updated note.",
                error_type="save_error"
            )

        return NoteResult(
            success=True,
            action="update",
            message="Note updated successfully.",
            note=target.to_dict(),
            count=1
        )

    # ------------------------------------------------------
    # DELETE NOTE
    # ------------------------------------------------------

    def delete(self, note_id: str) -> NoteResult:

        note_id = str(note_id).strip()

        for index, note in enumerate(self.notes):

            if note.note_id == note_id:

                removed = self.notes.pop(index)

                if not self._save():

                    self.notes.insert(
                        index,
                        removed
                    )

                    return NoteResult(
                        success=False,
                        action="delete",
                        error="Could not save deletion.",
                        error_type="save_error"
                    )

                return NoteResult(
                    success=True,
                    action="delete",
                    message="Note deleted successfully.",
                    note=removed.to_dict(),
                    count=1
                )

        return NoteResult(
            success=False,
            action="delete",
            error="Note not found.",
            error_type="not_found"
        )

    # ------------------------------------------------------
    # CLEAR NOTES
    # ------------------------------------------------------

    def clear(self) -> NoteResult:

        old_notes = self.notes.copy()

        self.notes = []

        if not self._save():

            self.notes = old_notes

            return NoteResult(
                success=False,
                action="clear",
                error="Could not clear notes.",
                error_type="save_error"
            )

        return NoteResult(
            success=True,
            action="clear",
            message="All notes cleared.",
            count=len(old_notes)
        )

    # ------------------------------------------------------
    # LIST NOTES
    # ------------------------------------------------------

    def list_notes(
        self,
        category: Optional[str] = None
    ) -> NoteResult:

        category = (
            self.normalize(category)
            if category
            else None
        )

        results = []

        for note in self.notes:

            if category:
                if self.normalize(
                    note.category
                ) != category:
                    continue

            results.append(
                note.to_dict()
            )

        results.sort(
            key=lambda item: item["updated_at"],
            reverse=True
        )

        return NoteResult(
            success=True,
            action="list",
            notes=results,
            count=len(results)
        )

    # ------------------------------------------------------
    # CATEGORIES
    # ------------------------------------------------------

    def categories(self) -> List[str]:

        result = []

        for note in self.notes:

            if note.category not in result:
                result.append(note.category)

        return sorted(result)

    # ------------------------------------------------------
    # TAGS
    # ------------------------------------------------------

    def tags(self) -> List[str]:

        result = []

        for note in self.notes:

            for tag in note.tags:

                if tag not in result:
                    result.append(tag)

        return sorted(result)

    # ------------------------------------------------------
    # COUNT
    # ------------------------------------------------------

    def count(self) -> int:
        return len(self.notes)

    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    def status(self) -> Dict[str, Any]:

        category_counts = {}

        for note in self.notes:

            category = note.category

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "notes_file": self.notes_file,
            "note_count": len(self.notes),
            "categories": len(category_counts),
            "category_counts": category_counts,
            "tags": len(self.tags()),
            "storage_exists": os.path.exists(
                self.notes_file
            )
        }


# ==========================================================
# DEFAULT ENGINE
# ==========================================================

_default_engine = NotesEngine()


# ==========================================================
# PUBLIC FUNCTIONS
# ==========================================================

def add_note(
    title: str,
    content: str,
    category: str = "general",
    tags=None
) -> NoteResult:

    return _default_engine.add(
        title,
        content,
        category,
        tags
    )


def get_note(note_id: str) -> NoteResult:
    return _default_engine.get(note_id)


def search_notes(
    query: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 10
) -> NoteResult:

    return _default_engine.search(
        query,
        category,
        tag,
        limit
    )


def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    tags=None
) -> NoteResult:

    return _default_engine.update(
        note_id,
        title,
        content,
        category,
        tags
    )


def delete_note(note_id: str) -> NoteResult:
    return _default_engine.delete(note_id)


def clear_notes() -> NoteResult:
    return _default_engine.clear()


def list_notes(
    category: Optional[str] = None
) -> NoteResult:

    return _default_engine.list_notes(
        category
    )


def note_categories() -> List[str]:
    return _default_engine.categories()


def note_tags() -> List[str]:
    return _default_engine.tags()


def note_count() -> int:
    return _default_engine.count()


def notes_status() -> Dict[str, Any]:
    return _default_engine.status()


# ==========================================================
# SELF TEST
# ==========================================================

def run_notes_engine_test() -> bool:

    print("=" * 58)
    print("AkshAI Notes Engine v1.0")
    print("=" * 58)

    test_file = os.path.join(
        NOTES_DIR,
        "notes_test.json"
    )

    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except Exception:
            pass

    engine = NotesEngine(test_file)

    passed = 0
    total = 0

    def check(name, condition):
        nonlocal passed, total

        total += 1

        if condition:
            print(f"{name} passed")
            passed += 1
        else:
            print(f"FAILED {name}")

    # 1
    check(
        "Normalization test",
        engine.normalize(
            "  Hello   AkshAI  "
        ) == "hello akshai"
    )

    # 2
    check(
        "Tag normalization test",
        engine.normalize_tags(
            "JEE, Study, JEE"
        ) == ["jee", "study"]
    )

    # 3
    result = engine.add(
        "Physics Revision",
        "Revise kinematics formulas.",
        category="study",
        tags=["physics", "jee"]
    )

    check(
        "Add note test",
        result.success
        and result.note["note_id"] == "note_0001"
    )

    # 4
    result2 = engine.add(
        "Python Project",
        "Build the next AkshAI module.",
        category="coding",
        tags=["python", "akshai"]
    )

    check(
        "Second note test",
        result2.success
    )

    # 5
    duplicate = engine.add(
        "Physics Revision",
        "Another version."
    )

    check(
        "Duplicate detection test",
        not duplicate.success
        and duplicate.error_type == "duplicate"
    )

    # 6
    found = engine.search("kinematics")

    check(
        "Search test",
        found.success
        and found.count == 1
        and found.notes[0]["note_id"] == "note_0001"
    )

    # 7
    category_search = engine.search(
        "",
        category="coding"
    )

    check(
        "Category search test",
        category_search.success
        and category_search.count == 1
    )

    # 8
    tag_search = engine.search(
        "",
        tag="python"
    )

    check(
        "Tag search test",
        tag_search.success
        and tag_search.count == 1
    )

    # 9
    got = engine.get("note_0001")

    check(
        "Get note test",
        got.success
        and got.note["title"]
        == "Physics Revision"
    )

    # 10
    updated = engine.update(
        "note_0001",
        title="Physics JEE Revision",
        content="Revise motion and kinematics.",
        tags=["physics", "jee", "revision"]
    )

    check(
        "Update note test",
        updated.success
        and updated.note["title"]
        == "Physics JEE Revision"
        and "revision"
        in updated.note["tags"]
    )

    # 11
    found_updated = engine.search(
        "Physics JEE"
    )

    check(
        "Updated search test",
        found_updated.success
        and found_updated.count == 1
    )

    # 12
    categories = engine.categories()

    check(
        "Categories test",
        categories == ["coding", "study"]
    )

    # 13
    tags = engine.tags()

    check(
        "Tags test",
        "jee" in tags
        and "python" in tags
        and "revision" in tags
    )

    # 14
    listed = engine.list_notes()

    check(
        "List notes test",
        listed.success
        and listed.count == 2
    )

    # 15
    status = engine.status()

    check(
        "Status test",
        status["note_count"] == 2
        and status["storage_exists"]
    )

    # 16
    deleted = engine.delete("note_0002")

    check(
        "Delete note test",
        deleted.success
        and engine.count() == 1
    )

    # 17
    missing = engine.get("note_9999")

    check(
        "Missing note test",
        not missing.success
        and missing.error_type == "not_found"
    )

    # 18
    engine2 = NotesEngine(test_file)

    check(
        "Persistence test",
        engine2.count() == 1
        and engine2.notes[0].note_id
        == "note_0001"
    )

    # 19
    cleared = engine2.clear()

    check(
        "Clear notes test",
        cleared.success
        and engine2.count() == 0
    )

    # 20
    empty_search = engine2.search(
        "nothing"
    )

    check(
        "Empty search result test",
        empty_search.success
        and empty_search.count == 0
    )

    # Cleanup
    try:
        if os.path.exists(test_file):
            os.remove(test_file)
    except Exception:
        pass

    print("-" * 58)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("NOTES ENGINE TEST PASSED ✅")
        return True

    print("NOTES ENGINE TEST FAILED ❌")
    return False


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    run_notes_engine_test()