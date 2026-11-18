#!/usr/bin/env python3
"""Parse and normalize r/Wetshaving SOTD (Shave of the Day) comment entries.

Input: a JSON file with a list of comments, each like:
    {"author": "...", "body": "...", "created_utc": 1234567890, "id": "..."}

Output: normalized entries, one dict per comment:
    {
      "author": ..., "comment_id": ..., "created_utc": ...,
      "razor": "...", "blade": "...", "blade_uses": 3, "brush": "...",
      "soap": "...", "preshave": "...", "aftershave": "...",
      "fragrance": "...", "bowl": "...", "rating": "...",
      "notes": "...",   # free text that wasn't a labeled field
      "other": {...},   # labeled fields we didn't recognize
    }

Usage:
    python sotd_parser.py raw_comments.json [-o normalized.json] [--csv out.csv]
"""

import argparse
import csv
import json
import re
import sys

# ---------------------------------------------------------------------------
# Field normalization: canonical name -> set of label spellings seen in SOTD
# comments. Labels are normalized (lowercased, non-alphanumerics removed)
# before lookup, so "Pre-Shave", "pre shave", "preshave" all match.
# ---------------------------------------------------------------------------
FIELD_ALIASES = {
    "razor": {
        "razor", "razors", "safetyrazor", "straightrazor", "shaver",
        "razorblade",  # rare, but seen: "razor/blade" lines handled below
    },
    "blade": {"blade", "blades"},
    "brush": {"brush", "brushes", "shavebrush", "shavingbrush", "brushedit"},
    "soap": {
        "soap", "soaps", "shavesoap", "shavingsoap", "cream", "creams",
        "shavecream", "shavingcream", "lather", "croap", "soapcream",
    },
    "preshave": {"preshave", "pre", "prep", "preshaveoil", "facewash",
                 "preshavesoap"},
    "aftershave": {
        "aftershave", "as", "splash", "balm", "postshave", "post",
        "aftershavesplash", "aftershavebalm", "postpostshave",
    },
    "fragrance": {"fragrance", "frag", "fragrances", "edt", "edp", "parfum",
                  "cologne", "scent", "perfume"},
    "bowl": {"bowl", "scuttle", "mug", "latherbowl", "latheringbowl", "cup"},
    "rating": {"rating", "rate", "score", "shaverating"},
}

CANONICAL_FIELDS = ["razor", "blade", "brush", "soap", "preshave",
                    "aftershave", "fragrance", "bowl", "rating"]


def normalize_label(label: str) -> str:
    """Lowercase and strip non-alphanumerics: 'Pre-Shave' -> 'preshave'."""
    return re.sub(r"[^a-z0-9]", "", label.lower())


LABEL_TO_FIELD = {}
for field, aliases in FIELD_ALIASES.items():
    for alias in aliases:
        LABEL_TO_FIELD.setdefault(alias, field)

# ---------------------------------------------------------------------------
# Line patterns found in SOTD comments.
# ---------------------------------------------------------------------------
# "**Razor:** Blackland Blackbird" / "**Razor**: value" / "* **Razor:** v"
# The colon may sit inside the closing bold markers (Reddit convention:
# "**Brush:**") or after them ("**Brush**:"), so accept both orders.
BOLD_FIELD_RE = re.compile(
    r"^\s*(?:[*\-+]\s*)?\*{1,2}\s*([^*:\n]{1,40}?)\s*:?\s*\*{1,2}\s*:?\s*(.+?)\s*$")
# "Razor: Blackland Blackbird" (plain, no bold) -- label must be short
PLAIN_FIELD_RE = re.compile(
    r"^\s*(?:[*\-+]\s*)?([A-Za-z][A-Za-z /&\-(),]{1,24}?)\s*:\s*(.+?)\s*$")
# "Razor. Shavely DG TTO razor" (period instead of colon) -- known labels only
DOT_FIELD_RE = re.compile(
    r"^\s*(?:[*\-+]\s*)?([A-Za-z][A-Za-z /&\-(),]{1,24}?)\s*\.\s+(.+?)\s*$")
# Markdown table row: "| Razor | Blackland Blackbird |"
TABLE_ROW_RE = re.compile(r"^\s*\|\s*([^|]{1,40}?)\s*\|\s*([^|]+?)\s*\|?\s*$")
# Bullet/numbered list marker stripper
LIST_MARKER_RE = re.compile(r"^\s*(?:[*\-+]\s+|\d+[.)]\s+)")
# Blade use count: "Astra SP (3)", "Nacet [2]", "SharpEdge (1).",
# "Feather (3nd use)", "Schick Yellow, 4th use"
USE_COUNT_RE = re.compile(
    r"[\(\[]\s*(\d{1,2})\s*(?:st|nd|rd|th)?\s*\??\s*(?:[x×]\s*)?(?:use)?\s*[\)\]]"
    r"[.,;:]?\s*$")
USE_COUNT_WORD_RE = re.compile(
    r",?\s*(\d{1,2})(?:st|nd|rd|th)\s+use\.?\s*$", re.IGNORECASE)
# Rating: "8/10", "9", "4.5/5"
RATING_RE = re.compile(r"(\d+(?:\.\d+)?)\s*/\s*(\d+)")


def clean_value(value: str) -> str:
    value = value.strip()
    # strip surrounding bold/italic markers left over
    value = re.sub(r"^\*{1,2}\s*", "", value)
    value = re.sub(r"\s*\*{1,2}$", "", value)
    # strip a stray leading bullet: "Prep: - Hot Shower"
    value = re.sub(r"^[\-\*\+]\s+", "", value)
    return value.strip()


def extract_use_count(value: str):
    """Split trailing use count: 'Astra SP (3)' -> ('Astra SP', 3).

    Handles '(3)', '[2]', '(3).', '(3nd use)', and '4th use' spellings.
    """
    m = USE_COUNT_RE.search(value)
    if m:
        return value[:m.start()].strip(), int(m.group(1))
    m = USE_COUNT_WORD_RE.search(value)
    if m:
        return value[:m.start()].strip().rstrip(","), int(m.group(1))
    return value, None


def _looks_like_field(seg: str) -> bool:
    """True if a text segment looks like a 'Label: value' field line."""
    if BOLD_FIELD_RE.match(seg):
        return True
    if "|" in seg and TABLE_ROW_RE.match(seg):
        return True
    m = PLAIN_FIELD_RE.match(seg)
    return bool(m and normalize_label(m.group(1)) in LABEL_TO_FIELD)


# A known field label appearing mid-line, e.g.
# "- Post: Sea Spice Lime toner Frag: Sea Spice Lime"
# splits into ["- Post: Sea Spice Lime toner", "Frag: Sea Spice Lime"].
# Deliberately excludes ultra-generic labels ('as', 'pre', 'post') to avoid
# splitting prose; those are still caught at line start by _parse_line.
INLINE_LABEL_RE = re.compile(
    r"\s(?=(?:razors?|blades?|brush(?:es)?|soaps?|creams?|lather|croap|"
    r"pre[\s-]?shave|preshave|prep|post[\s-]?shave|splash|balm|"
    r"aftershave|fragrance|frag|edt|edp|bowl|scuttle|rating|tags)\s*:)",
    re.IGNORECASE)


def _split_segments(line: str):
    """Split a line on ';' only when a later segment is a labeled field.

    Keeps 'Post: A; B' as one value, but splits 'Brush: X; Razor: Y'
    into two fields. Unlabeled trailing segments stay glued to the
    field they follow.
    """
    if ";" not in line:
        return [line]
    parts = [p.strip() for p in line.split(";")]
    if not any(_looks_like_field(p) for p in parts[1:]):
        return [line]
    segments, current = [], ""
    for p in parts:
        if _looks_like_field(p) and current:
            segments.append(current)
            current = p
        else:
            current = f"{current}; {p}" if current else p
    if current:
        segments.append(current)
    return segments


def _parse_line(line: str, entry: dict):
    """Parse one line (or semicolon-separated segment) into entry."""
    # Skip markdown table separator rows: |---|---|
    if re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$", line):
        return
    # Skip headings
    if line.startswith("#"):
        return

    field = value = None
    m = BOLD_FIELD_RE.match(line)
    if m:
        field, value = m.group(1), m.group(2)
    else:
        m = TABLE_ROW_RE.match(line)
        if m and ("|" in line):
            field, value = m.group(1), m.group(2)
        else:
            # plain "Label: value" -- only accept if the label looks like
            # a known field, to avoid swallowing prose with colons
            m = PLAIN_FIELD_RE.match(line)
            if m:
                label_norm = normalize_label(m.group(1))
                if label_norm in LABEL_TO_FIELD:
                    field, value = m.group(1), m.group(2)
            if field is None:
                # "Label. value" variant, same known-label gate
                m = DOT_FIELD_RE.match(line)
                if m:
                    label_norm = normalize_label(m.group(1))
                    if label_norm in LABEL_TO_FIELD:
                        field, value = m.group(1), m.group(2)

    if field is None:
        entry["notes"].append(LIST_MARKER_RE.sub("", line).strip())
        return

    canon = LABEL_TO_FIELD.get(normalize_label(field))
    value = clean_value(value)
    # strip a duplicated label: "- Brush: Brush: X" -> "X"
    value = re.sub(r"^" + re.escape(field.strip()) + r"\s*:\s*",
                   "", value, flags=re.IGNORECASE).strip()
    if not value:
        return
    if canon:
        # repeated fields (e.g. two "Post Shave" lines: splash + balm)
        # are joined rather than dropped
        if canon in entry:
            entry[canon] += " | " + value
        else:
            entry[canon] = value
    else:
        entry["other"].setdefault(field.strip(), []).append(value)


def _clean_invisible(text: str) -> str:
    """Normalize archive quirks before parsing.

    Arctic Shift returns comment bodies verbatim, including U+2060 WORD JOINER
    etc. that break line-label matching, so normalize them away first.
    Some comments also use backslash-escaped markdown ("\\*\\*Brush:\\*\\*");
    unescape those so the bold-field regex can match.
    """
    text = re.sub(r"[\u2060\u200b\u200c\u200d\ufeff\u00ad\u034f]", "", text)
    return text.replace("\\*", "*")


def parse_comment_body(body: str) -> dict:
    """Parse one SOTD comment body into normalized fields."""
    entry = {"notes": [], "other": {}}

    for raw_line in _clean_invisible(body).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # normalize unicode bullets ("• Brush: ...") and runs of bullets
        # ("•••Razor. ...") to a single "- " marker
        line = re.sub(r"^[•·▪‣∙]+\s*", "- ", line)
        line = re.sub(r"^([*\-+]){2,}\s*", "- ", line)
        # split combined lines: "- Post: X toner Frag: Y"
        pieces = [p for p in INLINE_LABEL_RE.split(line) if p.strip()]
        for piece in pieces:
            # Some comments put the whole gear list on one line separated by
            # semicolons: "Brush: X; Razor: Y; Lather: Z". Split those, but
            # keep "Post: A; B" style single-field values intact.
            for seg in _split_segments(piece):
                if seg:
                    _parse_line(seg, entry)

    entry["notes"] = "\n".join(n for n in entry["notes"] if n).strip()
    return entry


def normalize_comment(comment: dict) -> dict:
    """Normalize one raw comment dict into a structured entry."""
    body = comment.get("body", "")
    parsed = parse_comment_body(body)

    out = {
        "author": comment.get("author"),
        "comment_id": comment.get("id"),
        "created_utc": comment.get("created_utc"),
        "thread_id": comment.get("thread_id"),
        "thread_title": comment.get("thread_title"),
        "thread_date": comment.get("thread_date"),
        "razor": parsed.get("razor"),
        "blade": None,
        "blade_uses": None,
        "brush": parsed.get("brush"),
        "soap": parsed.get("soap"),
        "preshave": parsed.get("preshave"),
        "aftershave": parsed.get("aftershave"),
        "fragrance": parsed.get("fragrance"),
        "bowl": parsed.get("bowl"),
        "rating": parsed.get("rating"),
        "notes": parsed.get("notes") or None,
        "other": parsed.get("other") or None,
    }

    if parsed.get("blade"):
        blade, uses = extract_use_count(parsed["blade"])
        out["blade"] = blade or None
        out["blade_uses"] = uses

    if out["rating"]:
        m = RATING_RE.search(out["rating"])
        if m:
            try:
                num, den = float(m.group(1)), float(m.group(2))
                if den:
                    out["rating"] = round(num / den * 10, 1)  # normalize to /10
            except (ValueError, ZeroDivisionError):
                pass

    return out


def normalize_all(comments: list) -> list:
    return [normalize_comment(c) for c in comments]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Parse r/Wetshaving SOTD comments")
    ap.add_argument("input", help="JSON file: list of {author, body, ...} comments")
    ap.add_argument("-o", "--output", default=None, help="JSON output path")
    ap.add_argument("--csv", default=None, help="also write a CSV")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "comments" in data:
        # {"thread": {"id","title","date"}, "comments": [...]}
        thread = data.get("thread", {}) or {}
        comments = data["comments"]
        for c in comments:
            c.setdefault("thread_id", thread.get("id"))
            c.setdefault("thread_title", thread.get("title"))
            c.setdefault("thread_date", thread.get("date"))
    elif isinstance(data, dict):
        comments = data.get("comments", [])
    else:
        comments = data

    entries = normalize_all(comments)

    out_path = args.output or "normalized.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    if args.csv:
        cols = ["thread_date", "thread_title", "author", "created_utc",
                "razor", "blade", "blade_uses",
                "brush", "soap", "preshave", "aftershave", "fragrance",
                "bowl", "rating", "notes"]
        with open(args.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(entries)

    n_fields = sum(1 for e in entries for k in CANONICAL_FIELDS if e.get(k))
    print(f"Parsed {len(entries)} comments -> {out_path}"
          + (f", {args.csv}" if args.csv else ""))
    print(f"Total recognized field values: {n_fields} "
          f"(avg {n_fields / max(len(entries), 1):.1f} per entry)")


if __name__ == "__main__":
    main()
