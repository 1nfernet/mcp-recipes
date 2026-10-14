"""Threads 글자 수 계산.

Threads API 문서: 글자 제한은 500자이고 "이모지는 UTF-8 바이트 수로 센다".
이모지만 정확히 가려내기 어려우므로 **보수적으로** 센다. 한글, 영문, 숫자, 일반 문장부호는 1로,
그 밖의 기호(이모지, 화살표, 변형 선택자, 제로폭 결합자 등)는 UTF-8 바이트 수로 센다.
화살표처럼 이모지가 아닌 기호는 실제보다 크게 셀 수 있다. 한도 검사에서는 안전한 쪽이다.
"""
from __future__ import annotations

LIMIT = 500

# 1로 세는 범위: 그 밖의 문자는 UTF-8 바이트 수로 센다
_ONE_RANGES = (
    (0x0000, 0x007F),   # ASCII
    (0x0080, 0x00FF),   # Latin-1 (· 등)
    (0x1100, 0x11FF),   # 한글 자모
    (0x2000, 0x206E),   # 일반 문장부호 (제로폭 결합자 U+200D 제외는 아래에서 처리)
    (0x3000, 0x303F),   # CJK 기호와 문장부호
    (0x3130, 0x318F),   # 한글 호환 자모
    (0xAC00, 0xD7A3),   # 한글 음절
    (0xFF00, 0xFFEF),   # 전각 문자
)
_EMOJI_PARTS = {0x200D, 0xFE0F, 0xFE0E}  # 이모지 조합에 쓰이는 문자는 바이트로 센다


def char_cost(ch: str) -> int:
    cp = ord(ch)
    if cp in _EMOJI_PARTS:
        return len(ch.encode("utf-8"))
    for lo, hi in _ONE_RANGES:
        if lo <= cp <= hi:
            return 1
    return len(ch.encode("utf-8"))


def threads_len(text: str) -> int:
    """Threads 한도 검사용 길이 (보수적)."""
    return sum(char_cost(ch) for ch in text.replace("\r", ""))
