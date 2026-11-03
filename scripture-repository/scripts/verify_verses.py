#!/usr/bin/env python3
"""verify_verses.py — fetch and look up scripture text from the bank's editions.

Usage:
  python3 verify_verses.py John 20:22 "Psalm 104:29-30" Genesis 1:1
  python3 verify_verses.py --download          # fetch the three editions into ./editions
  python3 verify_verses.py --only brenton "Exodus 20:7"

Prints, for each verse, the text as it stands in:
  brenton = Brenton Septuagint (1851 English; OT only; LXX psalm numbering)
  gnv     = Geneva Bible 1599
  kjv     = King James Version (1769 standard text)
Every text was fetched from eBible.org; the printed source line names the exact page.
No text is ever produced from memory.
"""
import os, re, html, sys, subprocess

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITIONS = os.path.join(HERE, "editions")
EDS = {
    "brenton": ("https://ebible.org/eng-Brenton/eng-Brenton_html.zip", "Old Testament (LXX)"),
    "gnv":     ("https://ebible.org/enggnv/enggnv_html.zip", "whole Bible"),
    "kjv":     ("https://ebible.org/eng-kjv2006/eng-kjv2006_html.zip", "whole Bible"),
}
CODES = {"genesis":"GEN","exodus":"EXO","leviticus":"LEV","numbers":"NUM","deuteronomy":"DEU",
 "joshua":"JOS","judges":"JDG","ruth":"RUT","1 samuel":"1SA","2 samuel":"2SA","1 kings":"1KI",
 "2 kings":"2KI","job":"JOB","psalm":"PSA","psalms":"PSA","proverbs":"PRO","ecclesiastes":"ECC",
 "isaiah":"ISA","jeremiah":"JER","lamentations":"LAM","ezekiel":"EZK","daniel":"DAG","hosea":"HOS",
 "joel":"JOL","amos":"AMO","obadiah":"OBA","jonah":"JON","micah":"MIC","nahum":"NAM","habakkuk":"HAB",
 "zephaniah":"ZEP","haggai":"HAG","zechariah":"ZEC","malachi":"MAL","1 chronicles":"1CH","2 chronicles":"2CH",
 "matthew":"MAT","mark":"MRK","luke":"LUK","john":"JHN","acts":"ACT","romans":"ROM",
 "1 corinthians":"1CO","2 corinthians":"2CO","galatians":"GAL","ephesians":"EPH","philippians":"PHP",
 "colossians":"COL","1 thessalonians":"1TH","2 thessalonians":"2TH","1 timothy":"1TI","2 timothy":"2TI",
 "titus":"TIT","philemon":"PHM","hebrews":"HEB","james":"JAS","1 peter":"1PE","2 peter":"2PE",
 "1 john":"1JN","2 john":"2JN","3 john":"3JN","jude":"JUD","revelation":"REV"}

def download():
    os.makedirs(EDITIONS, exist_ok=True)
    for tag, (url, _) in EDS.items():
        out = os.path.join(EDITIONS, tag)
        zipf = os.path.join(EDITIONS, tag + ".zip")
        if not os.path.isdir(out):
            print(f"downloading {tag} ...", flush=True)
            subprocess.run(["curl", "-sL", "-o", zipf, url], check=True)
            subprocess.run(["unzip", "-o", "-q", zipf, "-d", out], check=True)
    print("editions at", EDS)

def find_file(tag, book, chap):
    for pat in (f"{book}{chap:02d}", f"{book}{chap:03d}"):
        p = os.path.join(EDITIONS, tag, pat + ".htm")
        if os.path.isfile(p): return p
    return None

_cache = {}
def chapter(tag, book, chap):
    key = (tag, book, chap)
    if key in _cache: return _cache[key]
    p = find_file(tag, book, chap)
    if not p: _cache[key] = {}; return {}
    t = open(p, encoding="utf-8", errors="replace").read()
    body = t.split('<div class="main">', 1)[-1].split("<ul class='tnav'>")[0].split('<div class="footnote">')[0]
    body = re.sub(r'<a[^>]*class="notemark"[^>]*>.*?</a>', '', body, flags=re.S)
    verses = {}
    parts = re.split(r'<span class="verse" id="V(\d+)"[^>]*>\s*[0-9]+(?:&#160;|\u00a0)</span>', body)
    for i in range(1, len(parts)-1, 2):
        verses[int(parts[i])] = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', parts[i+1]))).strip()
    _cache[key] = verses
    return verses

def lookup(ref):
    ref = ref.strip()
    m = re.match(r'^([1-3][iI]?[. ]+)?([A-Za-z]+) ([0-9]{1,3})(?:[:.]\s*([0-9]{1,3})(?:[-\u2013]([0-9]{1,3}))?)?$', ref)
    if not m: return None, f"cannot parse reference: {ref}"
    bookname = ((m.group(1) or "").replace(".", "").strip() + " " + m.group(2)).strip().lower()
    code = CODES.get(bookname)
    if not code: return None, f"unknown book: {bookname}"
    c_, v1, v2 = int(m.group(3)), int(m.group(4) or 0), int(m.group(5) or 0)
    v1 = v1 or v2
    vs = list(range(v1, (v2 or v1) + 1)) if (v1 or v2) else None
    out = []
    disp = f"{bookname.title()} {c_}" + (f":{v1}\u2013{v2}" if v2 and v2 != v1 else (f":{v1}" if v1 else " (whole chapter)"))
    for tag in ("brenton", "gnv", "kjv"):
        if vs is None:
            ch = chapter(tag, code, c_)
            texts = [f"  {n}: {t}" for n, t in sorted(ch.items())]
            src = f"https://ebible.org/{'eng-Brenton' if tag=='brenton' else ('enggnv' if tag=='gnv' else 'eng-kjv2006')}/{code}{c_:02d}.htm"
            out.append(f"[{tag}] {src}\n" + "\n".join(texts)); continue
        got, note = [], ""
        if tag == "brenton" and code == "PSA" and v1:
            lines = ["  CAUTION: Brenton numbers the Psalms by the old LXX, which runs one behind the Hebrew across most of the book (and merges two psalms around 9-10). Both candidate chapters are printed below - read the opening words and pick the true match."]
            for chx in (c_ - 1, c_):
                ch = chapter(tag, code, chx)
                if not ch: continue
                opening = ch.get(1, "")[:60]
                lines.append(f"  [LXX Psalm {chx} opens: “{opening}...”]")
                for vn in vs:
                    t = ch.get(vn, "")
                    if t: lines.append(f"  LXX Psalm {chx}:{vn} → “{t}”")
            got = lines
        else:
            for vn in vs:
                t = chapter(tag, code, c_).get(vn, "")
                if not t and tag == "brenton" and code == "JOS" and c_ == 8:
                    note = "  (Brenton moves Joshua 8:30-32 into 9:2; text from there)"
                    t = chapter(tag, code, 9).get(2, "")
                got.append(t)
        if not any(got): continue
        src = f"https://ebible.org/{'eng-Brenton' if tag=='brenton' else ('enggnv' if tag=='gnv' else 'eng-kjv2006')}/{code}{c_:02d}.htm"
        out.append(f"[{tag}] {src}\n  " + " ¶ ".join(got) + (("\n" + note) if note else ""))
    return disp, ("\n\n".join(out) if out else "no text found in any edition")

if __name__ == "__main__":
    args = sys.argv[1:]
    only = None
    if "--download" in args:
        download(); sys.exit(0)
    if "--only" in args:
        i = args.index("--only"); only = args[i+1]; del args[i:i+2]
    if not args:
        print(__doc__); sys.exit(1)
    for ref in args:
        disp, text = lookup(ref)
        print("=" * 70)
        print(disp or text)
        if disp:
            for ed, t in [("brenton", text)] if False else []: pass
            parts = text.split("\n\n")
            for p in parts:
                if only and not p.startswith(f"[{only}]"): continue
                print(p)