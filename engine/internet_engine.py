"""
============================================================
AkshAI Internet Engine v1.0
============================================================

Purpose:
- Internet connectivity check
- Safe HTTP/HTTPS requests
- URL fetching
- Basic webpage text extraction
- JSON/API response handling
- Timeout and error handling
- URL validation
- Clean structured results
- Standard library only

No third-party packages required.
"""

from __future__ import annotations

import json
import re
import socket
import ssl
from dataclasses import dataclass, asdict
from html import unescape
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


# ============================================================
# ENGINE INFO
# ============================================================

ENGINE_NAME = "AkshAI Internet Engine"
ENGINE_VERSION = "1.0"
ENGINE_STATUS = "ready"


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = (
    "AkshAI/1.0 "
    "(Internet Engine; Python urllib)"
)


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class InternetResult:
    success: bool
    status_code: Optional[int] = None
    url: str = ""
    content: str = ""
    content_type: str = ""
    error: str = ""
    error_type: str = ""
    elapsed_hint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# URL VALIDATION
# ============================================================

def normalize_url(url: str) -> str:
    """
    Normalize a URL.

    Examples:
        google.com -> https://google.com
        https://google.com -> unchanged
    """

    if not isinstance(url, str):
        return ""

    url = url.strip()

    if not url:
        return ""

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url

    return url


def is_valid_url(url: str) -> bool:
    """
    Return True if URL is a valid HTTP/HTTPS URL.
    """

    try:
        url = normalize_url(url)
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        if "." not in parsed.netloc and parsed.netloc != "localhost":
            return False

        return True

    except Exception:
        return False


# ============================================================
# INTERNET CONNECTIVITY
# ============================================================

def check_internet(
    host: str = "example.com",
    port: int = 443,
    timeout: int = 5
) -> bool:
    """
    Check whether a network connection can be established.

    Returns:
        True  -> connection successful
        False -> connection failed
    """

    try:
        socket.setdefaulttimeout(timeout)

        connection = socket.create_connection(
            (host, port),
            timeout=timeout
        )

        connection.close()
        return True

    except (OSError, socket.timeout):
        return False

    finally:
        socket.setdefaulttimeout(None)


# ============================================================
# DNS CHECK
# ============================================================

def check_dns(
    hostname: str,
    timeout: int = 5
) -> bool:
    """
    Check whether a hostname can be resolved.
    """

    if not hostname:
        return False

    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

        socket.gethostbyname(hostname)

        return True

    except (socket.gaierror, OSError):
        return False

    finally:
        socket.setdefaulttimeout(old_timeout)


# ============================================================
# HTTP REQUEST
# ============================================================

def fetch_url(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    max_bytes: int = 2_000_000,
    user_agent: str = DEFAULT_USER_AGENT
) -> InternetResult:
    """
    Fetch a URL using HTTP/HTTPS.

    Returns an InternetResult object.
    """

    original_url = url
    url = normalize_url(url)

    if not is_valid_url(url):
        return InternetResult(
            success=False,
            url=original_url,
            error="Invalid URL.",
            error_type="invalid_url"
        )

    if timeout <= 0:
        timeout = DEFAULT_TIMEOUT

    if max_bytes <= 0:
        max_bytes = 2_000_000

    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": (
                "text/html,"
                "application/json,"
                "text/plain,"
                "*/*"
            )
        },
        method="GET"
    )

    try:
        with urlopen(
            request,
            timeout=timeout
        ) as response:

            status_code = getattr(
                response,
                "status",
                None
            )

            final_url = response.geturl()

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            data = response.read(max_bytes)

            charset = response.headers.get_content_charset()

            if charset:
                encoding = charset
            else:
                encoding = "utf-8"

            try:
                content = data.decode(
                    encoding,
                    errors="replace"
                )
            except LookupError:
                content = data.decode(
                    "utf-8",
                    errors="replace"
                )

            return InternetResult(
                success=True,
                status_code=status_code,
                url=final_url,
                content=content,
                content_type=content_type
            )

    except HTTPError as error:

        return InternetResult(
            success=False,
            status_code=error.code,
            url=url,
            error=f"HTTP error {error.code}: {error.reason}",
            error_type="http_error"
        )

    except URLError as error:

        reason = getattr(
            error,
            "reason",
            "Unknown URL error"
        )

        return InternetResult(
            success=False,
            url=url,
            error=f"URL error: {reason}",
            error_type="url_error"
        )

    except socket.timeout:

        return InternetResult(
            success=False,
            url=url,
            error="Request timed out.",
            error_type="timeout"
        )

    except TimeoutError:

        return InternetResult(
            success=False,
            url=url,
            error="Request timed out.",
            error_type="timeout"
        )

    except ssl.SSLError as error:

        return InternetResult(
            success=False,
            url=url,
            error=f"SSL error: {error}",
            error_type="ssl_error"
        )

    except OSError as error:

        return InternetResult(
            success=False,
            url=url,
            error=f"Network error: {error}",
            error_type="network_error"
        )

    except Exception as error:

        return InternetResult(
            success=False,
            url=url,
            error=f"Unexpected error: {error}",
            error_type="unknown_error"
        )


# ============================================================
# WEBPAGE TEXT EXTRACTION
# ============================================================

def strip_html(html: str) -> str:
    """
    Convert basic HTML into readable plain text.
    """

    if not isinstance(html, str):
        return ""

    text = html

    # Remove script blocks
    text = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove style blocks
    text = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Replace common block tags with line breaks
    text = re.sub(
        r"</?(?:p|div|br|li|h[1-6]|tr|section|article)"
        r"\b[^>]*>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # Remove remaining HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Decode HTML entities
    text = unescape(text)

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Normalize line breaks
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


# ============================================================
# JSON HANDLING
# ============================================================

def parse_json(
    content: str
) -> Optional[Any]:
    """
    Parse JSON text.

    Returns:
        Python object on success.
        None on failure.
    """

    if not isinstance(content, str):
        return None

    try:
        return json.loads(content)

    except (json.JSONDecodeError, TypeError):
        return None


def is_json_content(
    content_type: str
) -> bool:
    """
    Check whether Content-Type indicates JSON.
    """

    if not isinstance(content_type, str):
        return False

    content_type = content_type.lower()

    return (
        "application/json" in content_type
        or "application/ld+json" in content_type
        or "+json" in content_type
    )


# ============================================================
# WEBPAGE FETCH
# ============================================================

def fetch_webpage(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    max_bytes: int = 2_000_000
) -> InternetResult:
    """
    Fetch a webpage and convert HTML to readable text.
    """

    result = fetch_url(
        url=url,
        timeout=timeout,
        max_bytes=max_bytes
    )

    if not result.success:
        return result

    if is_json_content(result.content_type):
        parsed = parse_json(result.content)

        if parsed is not None:
            result.content = json.dumps(
                parsed,
                indent=2,
                ensure_ascii=False
            )

        return result

    result.content = strip_html(
        result.content
    )

    return result


# ============================================================
# API REQUEST
# ============================================================

def fetch_json(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    max_bytes: int = 2_000_000
) -> InternetResult:
    """
    Fetch an API endpoint and parse JSON.
    """

    result = fetch_url(
        url=url,
        timeout=timeout,
        max_bytes=max_bytes
    )

    if not result.success:
        return result

    parsed = parse_json(
        result.content
    )

    if parsed is None:
        result.success = False
        result.error = (
            "Response was not valid JSON."
        )
        result.error_type = "invalid_json"
        return result

    result.content = json.dumps(
        parsed,
        indent=2,
        ensure_ascii=False
    )

    return result


# ============================================================
# URL INFORMATION
# ============================================================

def get_url_info(
    url: str
) -> Dict[str, Any]:
    """
    Return useful information about a URL.
    """

    normalized = normalize_url(url)

    if not is_valid_url(normalized):
        return {
            "valid": False,
            "url": url,
            "scheme": "",
            "host": "",
            "port": None,
            "path": "",
            "query": ""
        }

    parsed = urlparse(normalized)

    return {
        "valid": True,
        "url": normalized,
        "scheme": parsed.scheme,
        "host": parsed.hostname or "",
        "port": parsed.port,
        "path": parsed.path,
        "query": parsed.query
    }


# ============================================================
# SIMPLE INTERNET STATUS
# ============================================================

def internet_status() -> Dict[str, Any]:
    """
    Return a simple internet status dictionary.
    """

    connected = check_internet()

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "internet_available": connected,
        "status": (
            "online"
            if connected
            else "offline"
        )
    }


# ============================================================
# QUICK HELPERS
# ============================================================

def quick_fetch(
    url: str
) -> str:
    """
    Quickly fetch readable webpage text.
    """

    result = fetch_webpage(url)

    if result.success:
        return result.content

    return ""


def quick_json(
    url: str
) -> Optional[Any]:
    """
    Quickly fetch JSON.
    """

    result = fetch_json(url)

    if not result.success:
        return None

    return parse_json(result.content)


# ============================================================
# ENGINE STATUS
# ============================================================

def get_engine_status() -> Dict[str, Any]:
    """
    Return engine information.
    """

    return {
        "name": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "status": ENGINE_STATUS,
        "standard_library_only": True,
        "features": [
            "internet_check",
            "dns_check",
            "url_validation",
            "http_fetch",
            "https_fetch",
            "html_text_extraction",
            "json_parsing",
            "api_fetch",
            "url_information",
            "error_handling"
        ]
    }


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> bool:
    """
    Run internal engine tests.
    """

    print("=" * 58)
    print("AkshAI Internet Engine v1.0")
    print("=" * 58)

    passed = 0
    total = 0

    def check(
        name: str,
        condition: bool
    ) -> None:
        nonlocal passed, total

        total += 1

        if condition:
            passed += 1
            print(f"{name} test passed")
        else:
            print(f"FAILED {name}")

    # --------------------------------------------------------
    # URL TESTS
    # --------------------------------------------------------

    check(
        "URL normalization",
        normalize_url(
            "example.com"
        ) == "https://example.com"
    )

    check(
        "HTTPS URL validation",
        is_valid_url(
            "https://example.com"
        )
    )

    check(
        "HTTP URL validation",
        is_valid_url(
            "http://example.com"
        )
    )

    check(
        "Invalid URL detection",
        not is_valid_url(
            "not a valid url"
        )
    )

    # --------------------------------------------------------
    # URL INFO
    # --------------------------------------------------------

    info = get_url_info(
        "https://example.com/test?a=1"
    )

    check(
        "URL info test",
        (
            info["valid"] is True
            and info["scheme"] == "https"
            and info["host"] == "example.com"
            and info["path"] == "/test"
            and info["query"] == "a=1"
        )
    )

    # --------------------------------------------------------
    # HTML TEST
    # --------------------------------------------------------

    html = """
    <html>
        <head>
            <title>Test</title>
            <style>
                body { color: red; }
            </style>
        </head>

        <body>
            <h1>Hello AkshAI</h1>

            <p>This is a test.</p>

            <script>
                console.log("ignore");
            </script>

            <div>Internet Engine</div>
        </body>
    </html>
    """

    text = strip_html(html)

    check(
        "HTML text extraction",
        (
            "Hello AkshAI" in text
            and "This is a test." in text
            and "Internet Engine" in text
            and "console.log" not in text
            and "color: red" not in text
        )
    )

    # --------------------------------------------------------
    # JSON TESTS
    # --------------------------------------------------------

    json_data = parse_json(
        '{"name": "AkshAI", "version": 1}'
    )

    check(
        "JSON parsing",
        (
            isinstance(json_data, dict)
            and json_data["name"] == "AkshAI"
            and json_data["version"] == 1
        )
    )

    check(
        "Invalid JSON detection",
        parse_json(
            "{invalid json}"
        ) is None
    )

    check(
        "JSON content detection",
        is_json_content(
            "application/json; charset=utf-8"
        )
    )

    # --------------------------------------------------------
    # ENGINE STATUS
    # --------------------------------------------------------

    status = get_engine_status()

    check(
        "Engine status test",
        (
            status["name"]
            == "AkshAI Internet Engine"
            and status["version"] == "1.0"
            and status["standard_library_only"] is True
        )
    )

    # --------------------------------------------------------
    # INTERNET CHECK
    # --------------------------------------------------------

    # We do not require internet to be available.
    # We only verify that the function returns a boolean.

    online = check_internet(
        host="example.com",
        port=443,
        timeout=3
    )

    check(
        "Internet check test",
        isinstance(online, bool)
    )

    # --------------------------------------------------------
    # DNS CHECK
    # --------------------------------------------------------

    dns = check_dns(
        "example.com",
        timeout=3
    )

    check(
        "DNS check test",
        isinstance(dns, bool)
    )

    # --------------------------------------------------------
    # RESULT MODEL
    # --------------------------------------------------------

    result = InternetResult(
        success=True,
        status_code=200,
        url="https://example.com",
        content="Hello"
    )

    result_dict = result.to_dict()

    check(
        "Result model test",
        (
            isinstance(result_dict, dict)
            and result_dict["success"] is True
            and result_dict["status_code"] == 200
            and result_dict["url"]
            == "https://example.com"
        )
    )

    # --------------------------------------------------------
    # INVALID FETCH TEST
    # --------------------------------------------------------

    invalid_result = fetch_url(
        "not a valid url"
    )

    check(
        "Invalid fetch handling",
        (
            invalid_result.success is False
            and invalid_result.error_type
            == "invalid_url"
        )
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("-" * 58)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print(
            "INTERNET ENGINE TEST PASSED ✅"
        )
        return True

    print(
        "INTERNET ENGINE TEST FAILED ❌"
    )
    return False


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_self_test()