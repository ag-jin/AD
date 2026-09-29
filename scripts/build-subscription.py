#!/usr/bin/env python3
"""构建订阅文件：上游规则 + 自有规则注入。

上游 sr_top500_whitelist_ad.conf 每次更新会重写整个文件，
手写规则会被冲掉。此脚本把自有规则以标记块形式注入，
并把 update-url 指向本仓库，使订阅更新后仍保留自有规则。
"""
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UPSTREAM = (
    "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/"
    "sr_top500_whitelist_ad.conf"
)
PAGES = "https://ag-jin.github.io/AD/sr_top500_whitelist_ad.conf"
OUT = ROOT / "sr_top500_whitelist_ad.conf"
RULES = ROOT / "adblock-rules.conf"

START = "# >>> AD-CUSTOM-START 自有规则（由 GitHub Actions 注入，勿手改）"
END = "# <<< AD-CUSTOM-END"


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "build-bot"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            print(f"  第 {i + 1} 次下载失败: {exc}", file=sys.stderr)
    raise SystemExit("上游下载失败，保留原文件不动")


def strip_block(text):
    """移除已有注入块，保证重复执行幂等。"""
    pattern = re.escape(START) + r".*?" + re.escape(END) + r"\n?"
    return re.sub(pattern, "", text, flags=re.S)


def main():
    upstream = fetch(UPSTREAM)
    if "[Rule]" not in upstream or "FINAL" not in upstream:
        raise SystemExit("上游内容校验失败（缺 [Rule] 或 FINAL），中止")

    text = strip_block(upstream)

    # update-url 指回本仓库，避免订阅更新冲掉自有规则
    if re.search(r"^update-url\s*=", text, flags=re.M):
        text = re.sub(r"^update-url\s*=.*$", f"update-url = {PAGES}", text, flags=re.M)
    else:
        text = re.sub(r"^\[Rule\]", f"update-url = {PAGES}\n\n[Rule]", text, count=1, flags=re.M)

    rules = RULES.read_text(encoding="utf-8").strip()
    rule_lines = [ln for ln in rules.splitlines() if ln.strip().startswith(("DOMAIN", "#"))]
    block = "\n".join([START, *rule_lines, END]) + "\n"

    m = re.search(r"^\[Rule\][ \t]*$", text, flags=re.M)
    if not m:
        raise SystemExit("未找到 [Rule] 段，中止")
    text = text[: m.end()] + "\n" + block + text[m.end():]

    OUT.write_text(text, encoding="utf-8")

    n = sum(1 for ln in rule_lines if ln.startswith("DOMAIN"))
    print(f"已生成 {OUT.name}：自有规则 {n} 条，总 {len(text.splitlines())} 行")


if __name__ == "__main__":
    main()
