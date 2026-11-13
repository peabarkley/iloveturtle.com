#!/usr/bin/env python3
"""Patrol checks: language links resolve, species listing, logo, favicon."""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {"article-template.html", "zh/article-template.html"}
LABELS = {"English", "中文", "中文版", "EN"}


def fail(msg):
    print("FAIL:", msg)
    return 1


def is_stub(path: pathlib.Path) -> bool:
    head = path.read_text(encoding="utf-8", errors="replace")[:2500]
    return 'http-equiv="refresh"' in head or "http-equiv='refresh'" in head


def resolve(url_path: str):
    url_path = url_path.split("#")[0].split("?")[0]
    if url_path in ("", "/"):
        return ROOT / "index.html"
    if url_path.endswith("/"):
        cand = ROOT / url_path.strip("/") / "index.html"
        return cand if cand.exists() else None
    cand = ROOT / url_path.lstrip("/")
    if cand.exists():
        return cand
    idx = ROOT / url_path.lstrip("/") / "index.html"
    return idx if idx.exists() else None


def main():
    errors = 0
    if not (ROOT / "images" / "logo.png").is_file():
        errors += fail("images/logo.png is missing")
    for name in ("favicon.ico", "favicon.png"):
        if not (ROOT / name).is_file():
            errors += fail(f"missing {name}")

    a_re = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S | re.I)
    switch_re = re.compile(r'<div class="lang-switch">(.*?)</div>', re.S)
    hreflang_re = re.compile(r'hreflang="([^"]+)"\s+href="([^"]+)"')

    for html in ROOT.rglob("*.html"):
        rel = html.relative_to(ROOT).as_posix()
        text = html.read_text(encoding="utf-8")
        if "fa-turtle" in text:
            errors += fail(f"{rel} still uses fa-turtle")
        if rel not in SKIP and 'rel="icon"' not in text:
            errors += fail(f"{rel} has no favicon link")
        if rel in SKIP:
            continue
        for block in switch_re.findall(text):
            for href, inner in a_re.findall(block):
                target = resolve(href)
                if target is None:
                    errors += fail(f"{rel} language switch {href} does not exist")
                elif is_stub(target):
                    errors += fail(f"{rel} language switch {href} is a redirect stub")
        for href, inner in a_re.findall(text):
            label = re.sub(r"<[^>]+>", "", inner)
            label = re.sub(r"\s+", " ", label).strip()
            if label not in LABELS or not href.startswith("/"):
                continue
            target = resolve(href)
            if target is None:
                errors += fail(f"{rel} {label!r} link {href} does not exist")
            elif is_stub(target):
                errors += fail(f"{rel} {label!r} link {href} is a redirect stub")
        for lang, href in hreflang_re.findall(text):
            if "{{" in href:
                continue
            path = re.sub(r"https?://[^/]+", "", href)
            target = resolve(path)
            if target is None:
                errors += fail(f"{rel} hreflang {lang} -> {path} does not exist")

    footer_re = re.compile(r'<footer class="footer">.*?</footer>', re.S)
    for html in ROOT.rglob("*.html"):
        rel = html.relative_to(ROOT).as_posix()
        if rel in SKIP:
            continue
        text = html.read_text(encoding="utf-8")
        switches = switch_re.findall(text)
        if not switches:
            continue
        header_hrefs = [href for href, _inner in a_re.findall(switches[0])]
        if len(header_hrefs) != 1:
            errors += fail(f"{rel} header language switch should have one link")
            continue
        footer = footer_re.search(text)
        if not footer:
            continue
        footer_hrefs = []
        for href, inner in a_re.findall(footer.group(0)):
            label = re.sub(r"<[^>]+>", "", inner)
            label = re.sub(r"\s+", " ", label).strip()
            if label in LABELS:
                footer_hrefs.append(href)
        # Standard footers include the sitemap and a language link. Legacy
        # category footers have neither; leave those on the header switch only.
        requires_footer_link = "sitemap.xml" in footer.group(0)
        if requires_footer_link and len(footer_hrefs) != 1:
            errors += fail(f"{rel} footer should have one language link, found {footer_hrefs}")
            continue
        if len(footer_hrefs) > 1:
            errors += fail(f"{rel} footer has multiple language links: {footer_hrefs}")
            continue
        if footer_hrefs and footer_hrefs[0] != header_hrefs[0]:
            errors += fail(
                f"{rel} footer language link {footer_hrefs[0]} "
                f"does not match header {header_hrefs[0]}"
            )

    expected_switches = {
        "about.html": "/zh/about.html",
        "contact.html": "/zh/contact.html",
        "privacy.html": "/zh/privacy.html",
        "terms.html": "/zh/terms.html",
        "disclaimer.html": "/zh/disclaimer.html",
    }
    for rel, href in expected_switches.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        if f'<div class="lang-switch"><a href="{href}">中文</a></div>' not in text:
            errors += fail(f"{rel} is missing the header language switch to {href}")

    species = (ROOT / "category" / "species.html").read_text(encoding="utf-8")
    if "/article/red-footed-tortoise-care.html" not in species:
        errors += fail("species listing omits red-footed-tortoise-care")

    zh = (ROOT / "zh" / "article" / "tortoise2.html").read_text(encoding="utf-8")
    if 'href="/article/red-footed-tortoise-care.html"' not in zh:
        errors += fail("Chinese red-footed article does not link to the English article")

    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
