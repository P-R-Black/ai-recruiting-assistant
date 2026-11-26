
import json
import re
from collections import defaultdict
from dataclasses import dataclass

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# --------------------------------------------------------------------------- #
# Shared helpers (board-agnostic; reusable for Indeed, LinkedIn, Dice, ...)
# --------------------------------------------------------------------------- #
 
_WS = re.compile(r"\s+")
_BULLET = re.compile(r"^\s*[•·▪●◦\-–*]\s+")
 
 
def clean_text(text: str) -> str:
    return _WS.sub(" ", text.replace("\xa0", " ")).strip()
 
 
# Order matters: first match wins.
_SECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("preferred", re.compile(
        r"preferred|nice[- ]to[- ]have|desired|bonus (points|skills|qualifications)|"
        r"(would be )?a plus", re.I)),
    ("required", re.compile(
        r"required|minimum|basic qualifications|requirements|"
        r"what you['’]?ll need|what you need|what you bring|must[- ]have|"
        r"qualifications|skills", re.I)),
    ("responsibilities", re.compile(
        r"responsibilit|what you['’]?ll do|what you will do|duties|"
        r"day[- ]to[- ]day|key accountabilit|your role|in this role", re.I)),
    ("company", re.compile(
        r"our company|about (us|the company)|who we are|company overview", re.I)),
    ("summary", re.compile(
        r"summary|overview|about the (role|job|position|opportunity)|"
        r"job description|the opportunity|description", re.I)),
]
 
 
def classify_heading(text: str) -> str:
    """Map heading text to a section key. Unknown headings -> 'other'
    (which also stops lists from leaking into the previous section)."""
    for key, pattern in _SECTION_PATTERNS:
        if pattern.search(text):
            return key
    return "other"
 
 
def is_heading(node: Tag) -> bool:
    """True for <h1-6>, or a short <p> that is entirely bold or ends with ':'."""
    if node.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return True
    if node.name not in {"p", "div", "strong", "b"}:
        return False
    text = clean_text(node.get_text(" "))
    if not text or len(text) > 100:
        return False
    if node.name in {"strong", "b"}:
        return True
    bold_text = clean_text(" ".join(t.get_text(" ") for t in node.find_all(["b", "strong"])))
    return (bold_text == text) or (text.endswith(":") and len(text) < 80)
 
 
def _top_level_blocks(soup: BeautifulSoup) -> list:
    """Unwrap single-child wrapper divs so we iterate the real content blocks."""
    container: Tag | BeautifulSoup = soup
    while True:
        tags = [c for c in container.children if isinstance(c, Tag)]
        has_text = any(
            isinstance(c, NavigableString) and not isinstance(c, Comment) and c.strip()
            for c in container.children
        )
        if (
                len(tags) == 1
                and not has_text
                and tags[0].name in {"div", "span"}
            ):
            container = tags[0]
        else:
            break
    return [c for c in container.children if not isinstance(c, Comment)]
 
 
@dataclass
class ParsedDescription:
    description: str | None
    responsibilities: list[str]
    required_qualifications: list[str]
    preferred_qualifications: list[str]
 
 
def _dedupe(items: list[str]) -> list[str]:
    seen, out = set(), []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out
 
 
def parse_description_html(description_html: str) -> ParsedDescription:
    """Split a job description into summary text + responsibilities / required / preferred lists."""
    if "<" not in description_html:  # plain text description
        description_html = "".join(
            f"<p>{line}</p>"
            for line in description_html.splitlines()
            if line.strip()
        )

    soup = BeautifulSoup(description_html, "html.parser")

    current = "intro"
    items: dict[str, list[str]] = defaultdict(list)
    all_description_parts: list[str] = []

    for node in _top_level_blocks(soup):
        if isinstance(node, NavigableString):
            if text := clean_text(str(node)):
                all_description_parts.append(text)
            continue

        if not isinstance(node, Tag):
            continue

        # Preserve list items in the full description and extract them
        # into the categorized lists when appropriate.
        if node.name in {"ul", "ol"}:
            for li in node.find_all("li", recursive=False):
                if item := clean_text(li.get_text(" ")):
                    items[current].append(item)
                    all_description_parts.append(f"• {item}")

        # Preserve section headings and use them to classify following content.
        elif is_heading(node):
            heading = clean_text(node.get_text(" "))

            if heading:
                all_description_parts.append(heading)

            current = classify_heading(heading)

        else:
            # Paragraphs may contain bullet lines separated by <br>.
            # Inline tags are kept together as one flowing line.
            for br in node.find_all("br"):
                br.replace_with("\x00")

            for line in node.get_text("").split("\x00"):
                line = clean_text(line)

                if not line:
                    continue

                if _BULLET.match(line):
                    item = _BULLET.sub("", line).strip()

                    if item:
                        items[current].append(item)
                        all_description_parts.append(f"• {item}")
                else:
                    all_description_parts.append(line)

    return ParsedDescription(
        description="\n\n".join(all_description_parts) or None,
        responsibilities=_dedupe(items["responsibilities"]),
        required_qualifications=_dedupe(items["required"]),
        preferred_qualifications=_dedupe(items["preferred"]),
    )
 
 
# --------------------------------------------------------------------------- #
# Plain-text strategy: for descriptions with no usable HTML structure
# (tags stripped, <li> boundaries lost, everything on one line).
# --------------------------------------------------------------------------- #
 
_PREFIX = (
    r"(?:Key|Primary|Core|Minimum|Basic|Required|Preferred|Additional|"
    r"Desired|Essential|Technical|Main)"
    )
_NOUN = r"(?:Responsibilities|Qualifications|Requirements|Experience|Skills|Duties|Competencies)"
_PREFIXED = rf"(?:{_PREFIX}\s+)+{_NOUN}(?:\s*&\s*Soft\s+Skills)?"
_PHRASES = (
    r"What You['’]?ll (?:Do|Need|Bring)|What You (?:Will Do|Need|Bring)|Nice[- ]to[- ]Have|"
    r"About (?:Us|The (?:Role|Job|Company))|Our Company|Who We Are|Position Summary|"
    r"Job Summary|Job Description|Work Environment|Benefits|Job Category|Job Type|Job Location"
)
# Bare words ("Qualifications") only count as headings at a sentence/line start
# and when followed by ":", end of line, or another heading.
_BARE = (
    r"(?:Responsibilities|Qualifications|Requirements|Skills|"
    r"Duties|Summary|Overview|Description|Experience)"
)
_TEXT_HEADING = re.compile(
    rf"(?<![\w&])(?P<a>{_PREFIXED}|{_PHRASES})(?![\w])"
    rf"|(?:^|(?<=[.!?;:)])\s+)(?P<b>{_BARE})(?=\s*:|[ \t]*$|\s+{_PREFIXED})",
    re.M,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+(?=[A-Z0-9])")
 
 
def _html_to_text(html: str) -> str:
    """HTML -> text with a newline at every block boundary / <br>, inline tags joined."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(
        ["br", "p", "li", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6"]):
        tag.insert_before("\n")
        tag.insert_after("\n")
    lines = (clean_text(line) for line in soup.get_text("").splitlines())
    return "\n".join(line for line in lines if line)
 
 
def _split_items(body: str, multiline: bool) -> list[str]:
    body = body.strip()
    if not body:
        return []
    if multiline:  # every source line is already one item
        parts = body.split("\n")
    else:
        # Items that lost their punctuation but share a first word
        # ("... controls Must be ... Must have ...") -> split before the repeats.
        first = body.split()[0]
        if (
            first[:1].isupper() 
            and len(re.findall(rf"(?<=[a-z,).]) {re.escape(first)}\b", body)) >= 2):
            body = re.sub(rf"(?<=[a-z,)]) ({re.escape(first)})\b", r". \1", body)
        parts = _SENTENCE_SPLIT.split(body)
    items = []
    for part in parts:
        part = _BULLET.sub("", clean_text(part)).rstrip(" .;")
        if len(part) >= 3:
            items.append(part)
    return items
 
 
def parse_description_text(text: str) -> ParsedDescription:
    """Section a plain-text description by heading phrases found anywhere in the text."""
    text = text.replace("\xa0", " ").replace("\r", "")
    multiline = len([line for line in text.split("\n") if line.strip()]) > 4

    sections: dict[str, list[str]] = defaultdict(list)
    current, pos = "intro", 0

    for m in _TEXT_HEADING.finditer(text):
        sections[current].append(text[pos:m.start()])
        current = classify_heading(m.group("a") or m.group("b"))
        pos = m.end()

    sections[current].append(text[pos:])

    def items(key: str) -> list[str]:
        # Split each block on its own so item boundaries never merge across headings.
        return _dedupe(
            [
                i
                for block in sections.get(key, [])
                for i in _split_items(block, multiline)
            ]
        )

    # Preserve the complete description, including section headings.
    if multiline:
        lines = [clean_text(line) for line in text.split("\n")]
        description = "\n\n".join(line for line in lines if line)
    else:
        description = clean_text(text)

    return ParsedDescription(
        description=description or None,
        responsibilities=items("responsibilities"),
        required_qualifications=items("required"),
        preferred_qualifications=items("preferred"),
    )
    # text = text.replace("\xa0", " ").replace("\r", "")
    # multiline = len([line for line in text.split("\n") if line.strip()]) > 4
 
    # sections: dict[str, list[str]] = defaultdict(list)  # one entry per heading occurrence
    # current, pos = "intro", 0
    # for m in _TEXT_HEADING.finditer(text):
    #     sections[current].append(text[pos:m.start()])
    #     current = classify_heading(m.group("a") or m.group("b"))
    #     pos = m.end()
    # sections[current].append(text[pos:])
 
    # def items(key: str) -> list[str]:
    #     # Split each block on its own so item boundaries never merge across headings.
    #     return _dedupe(
    #         [
    #             i for block in sections.get(key, []) for i in _split_items(block, multiline)
    #             ]
    #             )
 
    # summary_blocks = [
    #     b for b in (
    #         sections.get("summary") or sections.get("intro") or []) if b.strip()
    #         ]
    # if multiline:
    #     lines = [clean_text(line) for b in summary_blocks for line in b.split("\n")]
    #     description = "\n\n".join(line for line in lines if line)
    # else:
    #     description = clean_text(" ".join(summary_blocks))
 
    # return ParsedDescription(
    #     description=description or None,
    #     responsibilities=items("responsibilities"),
    #     required_qualifications=items("required"),
    #     preferred_qualifications=items("preferred"),
    # )
 
 
# --------------------------------------------------------------------------- #
# Scoring: run every strategy, keep the best-looking result
# --------------------------------------------------------------------------- #
 
def score_parsed(parsed: ParsedDescription) -> float:
    """Heuristic quality score; higher is better."""
    score = 0.0
    for items in (
        parsed.responsibilities, 
        parsed.required_qualifications, 
        parsed.preferred_qualifications):
        if not items:
            continue
        score += 3 + min(len(items), 10) * 0.02
        score -= min(sum(len(i) > 500 for i in items), 3)  # blobs: item boundaries were not found
    if parsed.description:
        score += 2
        # if len(parsed.description) > 3000:
        #     score -= 2
        # if re.search(_PREFIXED, parsed.description):  # section headings leaked into the summary
        #     score -= 3
    return score
 
 
@dataclass
class Candidate:
    method: str  # e.g. "json-ld+html", "dom+text"
    parsed: ParsedDescription
    score: float
 
 
def build_candidates(sources: list[tuple[str, str]]) -> list[Candidate]:
    """
    ``sources`` = [(label, raw_description), ...] in priority order. 
    Ties go to the earlier one.
    """
    out: list[Candidate] = []
    seen: set = set()
    for label, raw in sources:
        text = _html_to_text(raw) if "<" in raw else raw
        for name, parse, arg in (
            ("html", parse_description_html, raw), ("text", parse_description_text, text)
            ):
            try:
                parsed = parse(arg)
            except Exception:  # one broken strategy must not sink the others
                continue
            key = (parsed.description, tuple(parsed.responsibilities),
                   tuple(parsed.required_qualifications), tuple(parsed.preferred_qualifications))
            if key in seen:
                continue
            seen.add(key)
            score = score_parsed(parsed)
            if name == "html" and (parsed.responsibilities or parsed.required_qualifications
                                   or parsed.preferred_qualifications):
                score += 0.5  # real list markup is more precise than text heuristics; wins ties
            out.append(Candidate(f"{label}+{name}", parsed, score))
    return out

 
 
def find_job_posting(soup: BeautifulSoup) -> dict | None:
    """Return the schema.org JobPosting dict from any ld+json script, if present."""
    for script in soup.find_all(
        "script",
        type="application/ld+json",
    ):
        raw_json = script.string or script.get_text()

        try:
            data = json.loads(raw_json)
        except (json.JSONDecodeError, TypeError):
            continue

        for item in _iter_json_ld_objects(data):
            types = item.get("@type")

            if isinstance(types, str):
                types = [types]

            if not isinstance(types, list):
                continue

            if any(_is_job_posting_type(value) for value in types):
                return item

    return None
 
 
def _is_job_posting_type(value: object) -> bool:
    """Recognize JobPosting type names and schema.org URLs."""
    if not isinstance(value, str):
        return False

    normalized = value.rstrip("/").rsplit("/", 1)[-1]
    normalized = normalized.rsplit("#", 1)[-1]

    return normalized.casefold() == "jobposting"


def _iter_json_ld_objects(data: object):
    """Yield dictionaries from common JSON-LD structures."""
    if isinstance(data, dict):
        yield data

        # JSON-LD may contain nested graphs or embedded objects.
        for value in data.values():
            if isinstance(value, (dict, list)):
                yield from _iter_json_ld_objects(value)

    elif isinstance(data, list):
        for value in data:
            yield from _iter_json_ld_objects(value)
