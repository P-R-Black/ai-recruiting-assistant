import re

from app.job_page.parsers.helpers.common import ParsedDescription

_SECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "responsibilities",
        re.compile(
            r"^(?:"
            r"responsibilities(?:\s+include)?"
            r"|duties(?:\s+include)?"
            r"|what\s+you(?:'ll|\s+will)\s+do"
            r"|what\s+you(?:'ll|\s+will)\s+be\s+doing"
            r"|job\s+responsibilities"
            r")$",
            re.IGNORECASE,
        ),
    ),
    (
        "required",
        re.compile(
            r"^(?:"
            r"required\s+qualifications"
            r"|minimum\s+qualifications"
            r"|requirements"
            r"|required\s+skills"
            r"|must\s+have"
            r"|what\s+you(?:'ll|\s+will)\s+need"
            r")$",
            re.IGNORECASE,
        ),
    ),
    (
        "preferred",
        re.compile(
            r"^(?:"
            r"preferred\s+qualifications"
            r"|preferred\s+skills"
            r"|desired\s+qualifications"
            r"|nice\s+to\s+have"
            r"|bonus\s+points"
            r")$",
            re.IGNORECASE,
        ),
    ),
)

_BULLET = re.compile(r"^\s*[-•*]\s*")


def _clean_line(line: str) -> str:
    """Remove surrounding whitespace and common bullet markers."""
    line = _BULLET.sub("", line)
    return line.strip()


def _classify_section_heading(heading: str) -> str:
    """Return the structured section associated with a recognized heading."""
    normalized = heading.strip().rstrip(":").strip()

    for section, pattern in _SECTION_PATTERNS:
        if pattern.fullmatch(normalized):
            return section

    return "other"


def _dedupe(items: list[str]) -> list[str]:
    """Remove duplicate items while preserving their original order."""
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        normalized = item.casefold()

        if normalized not in seen:
            seen.add(normalized)
            result.append(item)

    return result


def normalize_parsed_description(
    parsed: ParsedDescription,
) -> ParsedDescription:
    """
    Recover structured job-description sections when the parser
    did not extract any responsibilities or qualifications.
    """
    if not parsed.description:
        return parsed

    # Preserve existing data and only recover missing sections.
    recovered: dict[str, list[str]] = {
        "responsibilities": list(parsed.responsibilities),
        "required": list(parsed.required_qualifications),
        "preferred": list(parsed.preferred_qualifications),
    }

    # Identify which sections need recovery.
    missing_sections = {
        "responsibilities": not parsed.responsibilities,
        "required": not parsed.required_qualifications,
        "preferred": not parsed.preferred_qualifications,
    }

    # Nothing to recover.
    if not any(missing_sections.values()):
        return parsed

    current_section = "other"

    for raw_line in parsed.description.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Support inline headings, such as:
        # "Duties Include: Designing Marketing Materials"
        heading, separator, remainder = line.partition(":")

        section = _classify_section_heading(heading)

        if section != "other":
            current_section = section

            if (
                separator
                and remainder.strip()
                and missing_sections[current_section]
            ):
                item = _clean_line(remainder)

                if item:
                    recovered[current_section].append(item)

            continue

        # Unknown headings reset the current section.
        if separator and not remainder.strip():
            current_section = "other"
            continue

        if current_section == "other":
            continue

        # Never overwrite or supplement an already populated list.
        if not missing_sections[current_section]:
            continue

        item = _clean_line(line)

        if item:
            recovered[current_section].append(item)

    return ParsedDescription(
        description=parsed.description,
        responsibilities=_dedupe(recovered["responsibilities"]),
        required_qualifications=_dedupe(recovered["required"]),
        preferred_qualifications=_dedupe(recovered["preferred"]),
    )