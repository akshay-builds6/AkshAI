"""
AkshAI Web Engine v1.0
======================

Purpose:
    Web browsing and web research support for AkshAI.

Features:
    - URL normalization
    - URL validation
    - Web page fetching
    - HTML to readable text
    - Title extraction
    - Link extraction
    - Search engine query support
    - Multiple search results
    - Safe request handling
    - Structured WebResult
    - No third-party packages required

Depends on:
    internet_engine.py

Author:
    Akshay Yadav
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import unescape
from typing import Any, Dict, List, Optional
from urllib.parse import (
    quote_plus,
    unquote,
    urljoin,
    urlparse,
)
from urllib.request import (
    Request,
    urlopen,
)
from urllib.error import (
    HTTPError,
    URLError,
)
import json
import re
import ssl


# ============================================================
# CONSTANTS
# ============================================================

ENGINE_NAME = "AkshAI Web Engine"
ENGINE_VERSION = "1.0"

DEFAULT_TIMEOUT = 10

SEARCH_URL = "https://www.google.com/search?q={query}"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 11) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Mobile Safari/537.36"
)


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class WebResult:
    """
    Standard result returned by Web Engine.
    """

    success: bool = False

    query: str = ""
    url: str = ""

    title: str = ""
    text: str = ""

    status_code: Optional[int] = None
    content_type: str = ""

    links: List[Dict[str, str]] = field(default_factory=list)
    results: List[Dict[str, str]] = field(default_factory=list)

    source: str = "web"

    error: str = ""
    error_type: str = ""

    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "query": self.query,
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "links": self.links,
            "results": self.results,
            "source": self.source,
            "error": self.error,
            "error_type": self.error_type,
            "data": self.data,
        }


# ============================================================
# WEB ENGINE
# ============================================================

class WebEngine:
    """
    Main Web Engine for AkshAI.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
    ):
        self.timeout = max(1, int(timeout))
        self.user_agent = user_agent

        self._ssl_context = ssl.create_default_context()

    # ========================================================
    # TEXT CLEANING
    # ========================================================

    def clean_text(self, text: Any) -> str:
        """
        Clean extracted web text.
        """

        if text is None:
            return ""

        text = unescape(str(text))

        # Remove scripts/styles leftovers.
        text = re.sub(
            r"<script\b[^>]*>.*?</script>",
            " ",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        text = re.sub(
            r"<style\b[^>]*>.*?</style>",
            " ",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Normalize whitespace.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)

        # Remove excessive blank lines.
        lines = []

        for line in text.split("\n"):
            line = line.strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()

    # ========================================================
# URL NORMALIZATION
# ========================================================

    def normalize_url(self, url: Any) -> str:
        """
        Normalize a web URL.
        """

        if not isinstance(url, str):
            return ""

        url = url.strip()

        if not url:
            return ""

        # Common user input:
        # example.com -> https://example.com
        if not re.match(
            r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
            url
        ):
            url = "https://" + url

        parsed = urlparse(url)

        if not parsed.scheme:
            return ""

        if parsed.scheme.lower() not in {"http", "https"}:
            return ""

        if not parsed.netloc:
            return ""

        # Reject spaces inside hostname/domain.
        if any(
            char.isspace()
            for char in parsed.netloc
        ):
            return ""

        return url

    # ========================================================
    # URL VALIDATION
    # ========================================================

    def is_valid_url(self, url: Any) -> bool:
        """
        Check whether URL is valid HTTP/HTTPS.
        """

        normalized = self.normalize_url(url)

        if not normalized:
            return False

        parsed = urlparse(normalized)

        if parsed.scheme not in {"http", "https"}:
            return False

        if not parsed.netloc:
            return False

        return True

    # ========================================================
    # URL INFORMATION
    # ========================================================

    def get_url_info(self, url: Any) -> Dict[str, Any]:
        """
        Return useful information about a URL.
        """

        normalized = self.normalize_url(url)

        if not normalized:
            return {
                "valid": False,
                "url": "",
                "scheme": "",
                "domain": "",
                "path": "",
            }

        parsed = urlparse(normalized)

        return {
            "valid": True,
            "url": normalized,
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
            "fragment": parsed.fragment,
        }

    # ========================================================
    # HTML TAG REMOVAL
    # ========================================================

    def strip_html(self, html: Any) -> str:
        """
        Convert HTML into readable text.
        """

        if html is None:
            return ""

        html = str(html)

        # Remove comments.
        html = re.sub(
            r"<!--.*?-->",
            " ",
            html,
            flags=re.DOTALL,
        )

        # Remove scripts.
        html = re.sub(
            r"<script\b[^>]*>.*?</script>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove styles.
        html = re.sub(
            r"<style\b[^>]*>.*?</style>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Add line breaks for useful block tags.
        html = re.sub(
            r"</?(p|div|section|article|main|header|footer|"
            r"h1|h2|h3|h4|h5|h6|li|br|tr)\b[^>]*>",
            "\n",
            html,
            flags=re.IGNORECASE,
        )

        # Remove remaining tags.
        html = re.sub(
            r"<[^>]+>",
            " ",
            html,
        )

        # Decode HTML entities.
        html = unescape(html)

        return self.clean_text(html)

    # ========================================================
    # TITLE EXTRACTION
    # ========================================================

    def extract_title(self, html: Any) -> str:
        """
        Extract <title> from HTML.
        """

        if html is None:
            return ""

        match = re.search(
            r"<title\b[^>]*>(.*?)</title>",
            str(html),
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not match:
            return ""

        title = unescape(match.group(1))

        return self.clean_text(title)

    # ========================================================
    # LINK EXTRACTION
    # ========================================================

    def extract_links(
        self,
        html: Any,
        base_url: str = "",
        limit: int = 50,
    ) -> List[Dict[str, str]]:
        """
        Extract links from HTML.
        """

        if html is None:
            return []

        html = str(html)

        links: List[Dict[str, str]] = []

        pattern = re.compile(
            r'<a\b([^>]*)>(.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        for match in pattern.finditer(html):

            attributes = match.group(1)
            label = match.group(2)

            href_match = re.search(
                r'href\s*=\s*["\']([^"\']+)["\']',
                attributes,
                flags=re.IGNORECASE,
            )

            if not href_match:
                continue

            href = unescape(href_match.group(1)).strip()

            if not href:
                continue

            if base_url:
                href = urljoin(base_url, href)

            label = self.strip_html(label)

            links.append(
                {
                    "text": label,
                    "url": href,
                }
            )

            if len(links) >= limit:
                break

        return links

    # ========================================================
    # HTTP REQUEST
    # ========================================================

    def fetch(
        self,
        url: Any,
        timeout: Optional[int] = None,
    ) -> WebResult:
        """
        Fetch a webpage.
        """

        normalized = self.normalize_url(url)

        if not normalized:
            return WebResult(
                success=False,
                url="",
                source="web",
                error="Invalid URL.",
                error_type="invalid_url",
            )

        request_timeout = (
            self.timeout
            if timeout is None
            else max(1, int(timeout))
        )

        request = Request(
            normalized,
            headers={
                "User-Agent": self.user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/json;q=0.9,*/*;q=0.8"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=request_timeout,
                context=self._ssl_context,
            ) as response:

                raw_data = response.read()

                status_code = getattr(
                    response,
                    "status",
                    None,
                )

                content_type = response.headers.get(
                    "Content-Type",
                    "",
                )

                charset_match = re.search(
                    r"charset=([^\s;]+)",
                    content_type,
                    flags=re.IGNORECASE,
                )

                encoding = (
                    charset_match.group(1)
                    if charset_match
                    else "utf-8"
                )

                try:
                    content = raw_data.decode(
                        encoding,
                        errors="replace",
                    )
                except LookupError:
                    content = raw_data.decode(
                        "utf-8",
                        errors="replace",
                    )

                title = self.extract_title(content)

                text = self.strip_html(content)

                links = self.extract_links(
                    content,
                    base_url=normalized,
                )

                return WebResult(
                    success=True,
                    url=normalized,
                    title=title,
                    text=text,
                    status_code=status_code,
                    content_type=content_type,
                    links=links,
                    source="web",
                    data={
                        "content_length": len(raw_data),
                    },
                )

        except HTTPError as exc:

            return WebResult(
                success=False,
                url=normalized,
                status_code=getattr(
                    exc,
                    "code",
                    None,
                ),
                source="web",
                error=f"HTTP error: {exc}",
                error_type="http_error",
            )

        except URLError as exc:

            return WebResult(
                success=False,
                url=normalized,
                source="web",
                error=f"URL error: {exc.reason}",
                error_type="url_error",
            )

        except TimeoutError:

            return WebResult(
                success=False,
                url=normalized,
                source="web",
                error="Web request timed out.",
                error_type="timeout",
            )

        except Exception as exc:

            return WebResult(
                success=False,
                url=normalized,
                source="web",
                error=f"Web request failed: {exc}",
                error_type="request_error",
            )

    # ========================================================
    # JSON FETCH
    # ========================================================

    def fetch_json(
        self,
        url: Any,
        timeout: Optional[int] = None,
    ) -> WebResult:
        """
        Fetch JSON from a URL.
        """

        result = self.fetch(
            url,
            timeout=timeout,
        )

        if not result.success:
            return result

        try:
            data = json.loads(result.text)

            result.data = data

            return result

        except json.JSONDecodeError:

            return WebResult(
                success=False,
                query=result.query,
                url=result.url,
                title=result.title,
                text=result.text,
                status_code=result.status_code,
                content_type=result.content_type,
                links=result.links,
                source="web",
                error="Response is not valid JSON.",
                error_type="invalid_json",
            )

    # ========================================================
    # SEARCH URL
    # ========================================================

    def build_search_url(self, query: Any) -> str:
        """
        Build Google search URL.
        """

        if not isinstance(query, str):
            return ""

        query = query.strip()

        if not query:
            return ""

        return SEARCH_URL.format(
            query=quote_plus(query)
        )

    # ========================================================
    # SEARCH RESULT EXTRACTION
    # ========================================================

    def extract_search_results(
        self,
        html: Any,
        limit: int = 10,
    ) -> List[Dict[str, str]]:
        """
        Extract basic search results from a search page.

        Note:
            Search engine HTML can change at any time.
            This parser is intentionally defensive.
        """

        if html is None:
            return []

        html = str(html)

        results: List[Dict[str, str]] = []

        # Generic anchor-based extraction.
        pattern = re.compile(
            r'<a\b([^>]*)>(.*?)</a>',
            flags=re.IGNORECASE | re.DOTALL,
        )

        seen_urls = set()

        for match in pattern.finditer(html):

            attributes = match.group(1)
            content = match.group(2)

            href_match = re.search(
                r'href\s*=\s*["\']([^"\']+)["\']',
                attributes,
                flags=re.IGNORECASE,
            )

            if not href_match:
                continue

            href = unescape(
                href_match.group(1)
            ).strip()

            title = self.strip_html(content)

            if not href or not title:
                continue

            # Google redirect links.
            if href.startswith("/url?q="):
                parsed = urlparse(href)

                query_value = parsed.query

                match_url = re.search(
                    r"(?:^|&)q=([^&]+)",
                    query_value,
                )

                if match_url:
                    href = unquote(
                        match_url.group(1)
                    )

            # Skip internal/search links.
            lowered = href.lower()

            if (
                lowered.startswith("#")
                or lowered.startswith("javascript:")
                or lowered.startswith("mailto:")
            ):
                continue

            if href.startswith("/"):
                continue

            if href in seen_urls:
                continue

            seen_urls.add(href)

            results.append(
                {
                    "title": title,
                    "url": href,
                }
            )

            if len(results) >= limit:
                break

        return results

    # ========================================================
    # WEB SEARCH
    # ========================================================

    def search(
        self,
        query: Any,
        limit: int = 10,
        timeout: Optional[int] = None,
    ) -> WebResult:
        """
        Search the web.
        """

        if not isinstance(query, str):
            return WebResult(
                success=False,
                query="",
                source="web_search",
                error="Query must be text.",
                error_type="invalid_query",
            )

        query = query.strip()

        if not query:
            return WebResult(
                success=False,
                query="",
                source="web_search",
                error="Search query is empty.",
                error_type="empty_query",
            )

        limit = max(1, min(int(limit), 20))

        search_url = self.build_search_url(query)

        if not search_url:
            return WebResult(
                success=False,
                query=query,
                source="web_search",
                error="Could not build search URL.",
                error_type="search_url_error",
            )

        result = self.fetch(
            search_url,
            timeout=timeout,
        )

        result.query = query
        result.source = "web_search"

        if not result.success:
            return result

        search_results = self.extract_search_results(
            result.text,
            limit=limit,
        )

        result.results = search_results

        result.data = {
            "query": query,
            "result_count": len(search_results),
        }

        return result

    # ========================================================
    # SEARCH TEXT
    # ========================================================

    def search_text(
        self,
        query: Any,
        limit: int = 10,
    ) -> str:
        """
        Return a simple text representation of search results.
        """

        result = self.search(
            query,
            limit=limit,
        )

        if not result.success:
            return result.error

        if not result.results:
            return "No web results found."

        lines = []

        for index, item in enumerate(
            result.results,
            start=1,
        ):
            title = item.get("title", "")
            url = item.get("url", "")

            lines.append(
                f"{index}. {title}\n   {url}"
            )

        return "\n".join(lines)

    # ========================================================
    # READ PAGE
    # ========================================================

    def read_page(
        self,
        url: Any,
        max_chars: int = 12000,
    ) -> WebResult:
        """
        Fetch a webpage and return readable text.
        """

        result = self.fetch(url)

        if not result.success:
            return result

        max_chars = max(
            500,
            int(max_chars),
        )

        if len(result.text) > max_chars:
            result.text = (
                result.text[:max_chars]
                + "\n\n[Content truncated by AkshAI.]"
            )

        return result

    # ========================================================
    # PAGE SUMMARY INPUT
    # ========================================================

    def get_page_data(
        self,
        url: Any,
    ) -> Dict[str, Any]:
        """
        Return useful page information.
        """

        result = self.fetch(url)

        return {
            "success": result.success,
            "url": result.url,
            "title": result.title,
            "text": result.text,
            "links": result.links,
            "status_code": result.status_code,
            "content_type": result.content_type,
            "error": result.error,
        }
        # ============================================================
# NATURAL QUERY
# ============================================================

    def answer_query(
        self,
        query: Any,
        default_location: str = "Delhi",
    ) -> WebResult:
        """
        Handle natural-language web requests.

        Examples:
            search latest JEE news
            search Python tutorials
            open https://example.com
            read https://example.com
        """

        if not isinstance(query, str):
            return WebResult(
                success=False,
                query="",
                source="web_query",
                error="Query must be text.",
                error_type="invalid_query",
            )

        original_query = query.strip()

        if not original_query:
            return WebResult(
                success=False,
                query="",
                source="web_query",
                error="Query is empty.",
                error_type="empty_query",
            )

        lowered = original_query.lower().strip()

        # ----------------------------------------------------
        # Direct URL
        # ----------------------------------------------------

        if self.is_valid_url(original_query):
            result = self.read_page(original_query)

            result.query = original_query
            result.source = "web_query"

            return result

        # ----------------------------------------------------
        # Explicit search phrases
        # ----------------------------------------------------

        search_prefixes = [
            "search ",
            "search for ",
            "google ",
            "look up ",
            "find ",
            "web search ",
            "search the web for ",
        ]

        search_query = ""

        for prefix in search_prefixes:
            if lowered.startswith(prefix):
                search_query = original_query[
                    len(prefix):
                ].strip()
                break

        # ----------------------------------------------------
        # Question-style web request
        # ----------------------------------------------------

        if not search_query:

            web_keywords = [
                "latest",
                "recent",
                "today",
                "current",
                "news",
                "update",
                "updates",
                "online",
                "internet",
                "website",
                "web",
                "who is",
                "what is",
                "when is",
                "where is",
                "how much",
                "price",
            ]

            if any(
                keyword in lowered
                for keyword in web_keywords
            ):
                search_query = original_query

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        if search_query:

            result = self.search(
                search_query
            )

            result.query = original_query

            return result

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        result = self.search(
            original_query
        )

        result.query = original_query

        return result

    # ========================================================
    # FORMAT SEARCH RESULT
    # ========================================================

    def format_search_results(
        self,
        result: WebResult,
    ) -> str:
        """
        Convert search results into AkshAI-friendly text.
        """

        if not isinstance(result, WebResult):
            return "Invalid web result."

        if not result.success:
            return (
                f"❌ Web search failed.\n"
                f"Reason: {result.error}"
            )

        if not result.results:
            return (
                f"🔎 No useful results found "
                f"for: {result.query}"
            )

        lines = [
            f"🔎 Web Results for: "
            f"{result.query}",
            "",
        ]

        for index, item in enumerate(
            result.results,
            start=1,
        ):
            title = item.get(
                "title",
                "Untitled",
            )

            url = item.get(
                "url",
                "",
            )

            lines.append(
                f"{index}. {title}"
            )

            if url:
                lines.append(
                    f"   🔗 {url}"
                )

            lines.append("")

        return "\n".join(lines).strip()

    # ========================================================
    # FORMAT PAGE
    # ========================================================

    def format_page(
        self,
        result: WebResult,
        max_chars: int = 6000,
    ) -> str:
        """
        Convert webpage result into readable output.
        """

        if not isinstance(result, WebResult):
            return "Invalid web result."

        if not result.success:
            return (
                f"❌ Unable to open webpage.\n"
                f"Reason: {result.error}"
            )

        text = result.text.strip()

        if len(text) > max_chars:
            text = (
                text[:max_chars]
                + "\n\n"
                "[Content shortened by AkshAI.]"
            )

        lines = []

        lines.append(
            f"🌐 {result.title or 'Web Page'}"
        )

        if result.url:
            lines.append(
                f"🔗 {result.url}"
            )

        lines.append("")

        if text:
            lines.append(text)
        else:
            lines.append(
                "No readable text was found "
                "on this page."
            )

        return "\n".join(lines).strip()

    # ========================================================
    # SMART FORMAT
    # ========================================================

    def format_result(
        self,
        result: WebResult,
    ) -> str:
        """
        Automatically format any WebResult.
        """

        if not isinstance(result, WebResult):
            return "Invalid web result."

        if result.source == "web_search":
            return self.format_search_results(
                result
            )

        if result.source == "web_query":
            if result.results:
                return self.format_search_results(
                    result
                )

            return self.format_page(
                result
            )

        return self.format_page(
            result
        )

    # ========================================================
    # SIMPLE SEARCH API
    # ========================================================

    def quick_search(
        self,
        query: str,
        limit: int = 5,
    ) -> str:
        """
        Search and directly return formatted text.
        """

        result = self.search(
            query,
            limit=limit,
        )

        return self.format_result(
            result
        )

    # ========================================================
    # SIMPLE PAGE API
    # ========================================================

    def quick_read(
        self,
        url: str,
        max_chars: int = 6000,
    ) -> str:
        """
        Open a webpage and directly return
        formatted readable content.
        """

        result = self.read_page(
            url,
            max_chars=max_chars,
        )

        return self.format_page(
            result,
            max_chars=max_chars,
        )

    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> Dict[str, Any]:
        """
        Return Web Engine status.
        """

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "status": "ready",
            "timeout": self.timeout,
            "features": [
                "url_normalization",
                "url_validation",
                "web_fetch",
                "html_parsing",
                "title_extraction",
                "link_extraction",
                "web_search",
                "search_result_parsing",
                "page_reader",
                "natural_query",
                "result_formatting",
            ],
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

_web_engine = WebEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def fetch_url(
    url: str,
    timeout: Optional[int] = None,
) -> WebResult:
    """
    Fetch a webpage.
    """

    return _web_engine.fetch(
        url,
        timeout=timeout,
    )


def fetch_json(
    url: str,
    timeout: Optional[int] = None,
) -> WebResult:
    """
    Fetch JSON from a URL.
    """

    return _web_engine.fetch_json(
        url,
        timeout=timeout,
    )


def search_web(
    query: str,
    limit: int = 10,
) -> WebResult:
    """
    Search the web.
    """

    return _web_engine.search(
        query,
        limit=limit,
    )


def read_webpage(
    url: str,
    max_chars: int = 12000,
) -> WebResult:
    """
    Read webpage content.
    """

    return _web_engine.read_page(
        url,
        max_chars=max_chars,
    )


def answer_web_query(
    query: str,
) -> WebResult:
    """
    Handle natural web query.
    """

    return _web_engine.answer_query(
        query
    )


def quick_web_search(
    query: str,
    limit: int = 5,
) -> str:
    """
    Search web and return formatted text.
    """

    return _web_engine.quick_search(
        query,
        limit=limit,
    )


def quick_web_read(
    url: str,
    max_chars: int = 6000,
) -> str:
    """
    Read webpage and return formatted text.
    """

    return _web_engine.quick_read(
        url,
        max_chars=max_chars,
    )


def get_web_status() -> Dict[str, Any]:
    """
    Return engine status.
    """

    return _web_engine.status()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> bool:
    """
    Run Web Engine self-tests.
    """

    engine = WebEngine()

    passed = 0
    total = 0

    def test(
        name: str,
        condition: bool,
    ) -> None:
        nonlocal passed, total

        total += 1

        if condition:
            passed += 1
            print(
                f"{name} test passed"
            )
        else:
            print(
                f"{name} test FAILED"
            )

    print(
        f"{ENGINE_NAME} v{ENGINE_VERSION}"
    )
    print("=" * 55)

    # --------------------------------------------------------
    # 1. Text cleaning
    # --------------------------------------------------------

    cleaned = engine.clean_text(
        "  Hello   AkshAI  \n\n  World  "
    )

    test(
        "Text cleaning",
        cleaned == "Hello AkshAI\nWorld",
    )

    # --------------------------------------------------------
    # 2. URL normalization
    # --------------------------------------------------------

    normalized = engine.normalize_url(
        "example.com"
    )

    test(
        "URL normalization",
        normalized == "https://example.com",
    )

    # --------------------------------------------------------
    # 3. HTTPS validation
    # --------------------------------------------------------

    test(
        "HTTPS validation",
        engine.is_valid_url(
            "https://example.com"
        ),
    )

    # --------------------------------------------------------
    # 4. HTTP validation
    # --------------------------------------------------------

    test(
        "HTTP validation",
        engine.is_valid_url(
            "http://example.com"
        ),
    )

    # --------------------------------------------------------
    # 5. Invalid URL
    # --------------------------------------------------------

    test(
        "Invalid URL detection",
        not engine.is_valid_url(
            "not a url"
        ),
    )

    # --------------------------------------------------------
    # 6. URL info
    # --------------------------------------------------------

    info = engine.get_url_info(
        "https://example.com/test"
    )

    test(
        "URL info",
        (
            info["valid"]
            and info["scheme"] == "https"
            and info["domain"] == "example.com"
            and info["path"] == "/test"
        ),
    )

    # --------------------------------------------------------
    # 7. HTML stripping
    # --------------------------------------------------------

    html = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Hello</h1>
            <p>AkshAI Web Engine</p>
        </body>
    </html>
    """

    text = engine.strip_html(
        html
    )

    test(
        "HTML stripping",
        (
            "Hello" in text
            and "AkshAI Web Engine" in text
            and "<h1>" not in text
        ),
    )

    # --------------------------------------------------------
    # 8. Title extraction
    # --------------------------------------------------------

    title = engine.extract_title(
        html
    )

    test(
        "Title extraction",
        title == "Test Page",
    )

    # --------------------------------------------------------
    # 9. Link extraction
    # --------------------------------------------------------

    link_html = """
    <a href="https://example.com">
        Example
    </a>
    """

    links = engine.extract_links(
        link_html
    )

    test(
        "Link extraction",
        (
            len(links) == 1
            and links[0]["url"]
            == "https://example.com"
            and links[0]["text"]
            == "Example"
        ),
    )

    # --------------------------------------------------------
    # 10. Search URL
    # --------------------------------------------------------

    search_url = engine.build_search_url(
        "JEE Main 2027"
    )

    test(
        "Search URL generation",
        (
            search_url.startswith(
                "https://www.google.com/search?q="
            )
            and "JEE+Main+2027" in search_url
        ),
    )

    # --------------------------------------------------------
    # 11. Search result extraction
    # --------------------------------------------------------

    search_html = """
    <html>
        <body>
            <a href="https://example.com/one">
                Example One
            </a>

            <a href="https://example.com/two">
                Example Two
            </a>
        </body>
    </html>
    """

    search_results = (
        engine.extract_search_results(
            search_html,
            limit=5,
        )
    )

    test(
        "Search result extraction",
        (
            len(search_results) == 2
            and search_results[0]["title"]
            == "Example One"
            and search_results[1]["title"]
            == "Example Two"
        ),
    )

    # --------------------------------------------------------
    # 12. Search result limit
    # --------------------------------------------------------

    limited = engine.extract_search_results(
        search_html,
        limit=1,
    )

    test(
        "Search result limit",
        len(limited) == 1,
    )

    # --------------------------------------------------------
    # 13. Empty search
    # --------------------------------------------------------

    empty_search = engine.search(
        ""
    )

    test(
        "Empty search handling",
        (
            not empty_search.success
            and empty_search.error_type
            == "empty_query"
        ),
    )

    # --------------------------------------------------------
    # 14. Invalid query
    # --------------------------------------------------------

    invalid_query = engine.answer_query(
        None
    )

    test(
        "Invalid query handling",
        (
            not invalid_query.success
            and invalid_query.error_type
            == "invalid_query"
        ),
    )

    # --------------------------------------------------------
    # 15. Empty natural query
    # --------------------------------------------------------

    empty_query = engine.answer_query(
        "   "
    )

    test(
        "Empty natural query handling",
        (
            not empty_query.success
            and empty_query.error_type
            == "empty_query"
        ),
    )

    # --------------------------------------------------------
    # 16. Search phrase detection
    # --------------------------------------------------------

    result = engine.answer_query(
        "search Python programming"
    )

    test(
        "Natural search detection",
        result.query
        == "search Python programming",
    )

    # --------------------------------------------------------
    # 17. Direct URL detection
    # --------------------------------------------------------

    url_result = engine.answer_query(
        "https://example.com"
    )

    test(
        "Direct URL detection",
        url_result.query
        == "https://example.com",
    )

    # --------------------------------------------------------
    # 18. Search formatting
    # --------------------------------------------------------

    fake_result = WebResult(
        success=True,
        query="Python",
        source="web_search",
        results=[
            {
                "title": "Python",
                "url": "https://python.org",
            }
        ],
    )

    formatted_search = (
        engine.format_search_results(
            fake_result
        )
    )

    test(
        "Search formatting",
        (
            "Web Results" in formatted_search
            and "Python" in formatted_search
            and "https://python.org"
            in formatted_search
        ),
    )

    # --------------------------------------------------------
    # 19. Page formatting
    # --------------------------------------------------------

    fake_page = WebResult(
        success=True,
        url="https://example.com",
        title="Example",
        text="This is a test webpage.",
        source="web",
    )

    formatted_page = (
        engine.format_page(
            fake_page
        )
    )

    test(
        "Page formatting",
        (
            "Example" in formatted_page
            and "test webpage"
            in formatted_page
        ),
    )

    # --------------------------------------------------------
    # 20. Status
    # --------------------------------------------------------

    status = engine.status()

    test(
        "Status",
        (
            status["engine"]
            == ENGINE_NAME
            and status["version"]
            == ENGINE_VERSION
            and status["status"]
            == "ready"
        ),
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("-" * 55)
    print(
        f"Tests passed: {passed}/{total}"
    )

    if passed == total:
        print(
            "WEB ENGINE TEST PASSED ✅"
        )
        return True

    print(
        "WEB ENGINE TEST FAILED ❌"
    )
    return False


# ============================================================
# MODULE ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_self_test()