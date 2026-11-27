"""'.env' 점검: 키 이름과 형식만 보여주고 값은 가린다. (python scripts/check_env.py)"""
import re
from pathlib import Path

raw = Path(".env").read_bytes()
print(f"크기: {len(raw)} bytes")
if raw.startswith(b"\xef\xbb\xbf"):
    print("경고: UTF-8 BOM 있음 -> 'UTF-8(BOM 없음)'으로 다시 저장 권장")
if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
    print("오류: UTF-16 으로 저장됨 -> 'UTF-8'로 다시 저장해야 함")
    raise SystemExit(1)

text = raw.decode("utf-8-sig", errors="replace")
for i, line in enumerate(text.splitlines(), 1):
    s = line.strip()
    if not s:
        continue
    if s.startswith("#"):
        print(f"{i:>3}: (주석)")
    elif re.match(r"^(export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=", s):
        key, _, val = s.partition("=")
        note = "  <- 값 비어 있음" if not val.strip() else ""
        print(f"{i:>3}: {key.strip()}=****{note}")
    else:
        print(f"{i:>3}: !! KEY=VALUE 형식이 아님 -> 이 줄이 parse 경고의 원인 (내용은 숨김)")