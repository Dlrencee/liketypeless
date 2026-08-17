from __future__ import annotations

import re


PROVIDER_NAME = "local-conservative-rules"
TERMINAL_PUNCTUATION = "。！？；.!?;"

FILLER_PATTERNS = (
    r"(?<![\u4e00-\u9fff])嗯+[，,、\s]*",
    r"(?<![\u4e00-\u9fff])呃+[，,、\s]*",
    r"(?<![\u4e00-\u9fff])额+[，,、\s]*",
    r"[，,、\s]+嗯+[，,、\s]*",
    r"[，,、\s]+呃+[，,、\s]*",
    r"[，,、\s]+额+[，,、\s]*",
    r"[，,、\s]+啊+[，,、\s]*",
    r"啊+(?=[，,。！？；;\s]|$)",
    r"就是说[，,、\s]*",
    r"怎么说呢[，,、\s]*",
    r"这个[，,、\s]*(?=第一|第二|第三|第四|第五|第六|第七|第八|第九|第十|我们|我|要|可以|需要)",
    r"那个[，,、\s]*(?=第一|第二|第三|第四|第五|第六|第七|第八|第九|第十|我们|我|要|可以|需要)",
)

ORDINAL_PATTERN = re.compile(r"(第[一二三四五六七八九十]+[，,、\s]*(?:个|点|是|就是)?)")


def structure_text_conservatively(text: str) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""

    items = _split_ordinal_items(cleaned)
    if len(items) <= 1:
        return _ensure_terminal_punctuation(cleaned)

    return "\n".join(
        f"{index + 1}. {_ensure_terminal_punctuation(item)}" for index, item in enumerate(items)
    )


def ensure_terminal_punctuation(text: str) -> str:
    """Add conservative sentence-ending punctuation without changing words."""
    return "\n".join(
        _ensure_terminal_punctuation(line) if line.strip() else line
        for line in text.splitlines()
    ).strip()


def _clean_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("然后然后", "然后")
    cleaned = cleaned.replace("然后，然后", "然后")

    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, _preserve_separator, cleaned)

    cleaned = re.sub(r"([，,。！？；;])\1+", r"\1", cleaned)
    cleaned = re.sub(r"\s*([，,。！？；;])\s*", r"\1", cleaned)
    cleaned = re.sub(r"^[，,、。！？；;\s]+", "", cleaned)
    cleaned = re.sub(r"[，,、；;\s]+$", "", cleaned)
    return cleaned.strip()


def _preserve_separator(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith(("，", ",", "、", " ")):
        return "，"
    return ""


def _ensure_terminal_punctuation(text: str) -> str:
    value = text.strip()
    if not value or value.endswith(tuple(TERMINAL_PUNCTUATION)):
        return value
    return f"{value}。"


def _split_ordinal_items(text: str) -> list[str]:
    matches = list(ORDINAL_PATTERN.finditer(text))
    if len(matches) < 2:
        return [text]

    items: list[str] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        item = text[start:end]
        item = re.sub(r"^[，,、。；;\s]+", "", item)
        item = re.sub(r"^(就是|是)[，,、\s]*", "", item)
        item = re.sub(r"(然后|那么|所以)[，,、\s]*$", "", item)
        item = re.sub(r"[，,、；;\s]+$", "", item)
        item = item.strip()
        if item:
            items.append(item)

    return items or [text]
