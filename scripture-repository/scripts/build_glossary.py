#!/usr/bin/env python3
"""build_glossary.py — regenerate the Broad Glossary from verses.json alone.

python3 scripts/build_glossary.py            # writes glossary.md next to verses.json
Multi-work: groups entries by the work each use belongs to (hallowed sections vs the
Biblical Sabbath's SAB sections). Sections, statuses, rulings and flags all live in
verses.json, so this never needs the article files.
"""
import json, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = json.load(open(os.path.join(HERE, "verses.json"), encoding="utf-8"))
META, VERSES = src["meta"], src["verses"]
SECD = {s["key"]: s for s in META.get("sections", []) if isinstance(s, dict)}
SEC_ORDER = META.get("section_order") or sorted({u["section"] for v in VERSES for u in v["uses"]})

def label_of(key):
    s = SECD.get(key)
    if s:
        return s.get("label", key) + (f" — {s['sub']}" if s.get("sub") else "")
    labels = [u.get("section_label") for v in VERSES for u in v["uses"]
              if u.get("section") == key and u.get("section_label")]
    return labels[0] if labels else key

def work_of(v):
    secs = {u.get("section", "") for u in v["uses"]}
    if any(s.startswith("SAB") or s == "SAB-INTRO" for s in secs):
        return "sabbath"
    return "hallowed"

STATUS_DISP = {"confirmed": "CONFIRMED", "confirmed-excerpt": "CONFIRMED (EXCERPT)",
               "confirmed-joined": "CONFIRMED (JOINED VERSES)", "differs-minor": "DIFFERS (MINOR)",
               "differs": "DIFFERS", "paraphrase": "PARAPHRASE", "anchor": "ANCHOR",
               "commentary": "COMMENTARY", "recap-use": "RECAP CROSS-REFERENCE",
               "unverified-vs-codex": "PENDING CODEX 2ND PASS", "composite-quote": "COMPOSITE QUOTE"}
VERNAME = {"brenton": "Brenton LXX", "gnv": "Geneva 1599", "kjv": "KJV", "jps": "JPS 1917",
           "nets": "NETS (Septuagint, modern)", "sinaiticus": "Codex Sinaiticus",
           "standard-greek": "Standard critical Greek"}

def short(s, n=420):
    return "“" + (s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …") + "”"

WORKS = {
 "hallowed": ("*HALLOWED BE THY NAME*",
              "Old Testament: LXX Brenton exact (KJV only where the article's own voice is KJV). "
              "New Testament: 1599 Geneva.",
              "Divided by the seventeen Seeker questions, exactly as the book is divided. "
              "Verified and double-checked 2 Nov 2026."),
 "sabbath": ("*THE BIBLICAL SABBATH*",
             "Old Testament: NETS exact (LES where meaningfully different). "
             "New Testament: ancient codexes, codex named per quote (Sinaiticus dominant).",
             "Verified 3–4 Nov 2026. Proposed corrections (the article's OT blockquotes are "
             "smoothed NETS rather than NETS-exact) await the word `apply`. Codex-mismatch and "
             "second-pass items are marked in place."),
}

def flag_lines(pick):
    L = []
    for key in ("flag", "flag_pending", "flag_proposed_kjv"):
        fl = pick.get(key)
        if not fl: continue
        kind = fl.get("kind", "flag")
        if kind == "proposed-correction":
            L += [f"- **Ruling — proposed (awaiting apply):** {fl.get('detail', '')}"]
        elif kind == "needs-authorization":
            L += [f"- **Needs Gideon's ruling:** {fl.get('detail', '')}"]
        elif kind == "needs-verification":
            L += [f"- **Second pass pending:** {fl.get('detail', '')}"]
    return L

L = ["# BROAD GLOSSARY OF VERIFIED SCRIPTURES", ""]
for wkey in ("hallowed", "sabbath"):
    wver = [v for v in VERSES if work_of(v) == wkey]
    if not wver: continue
    title, rule, note = WORKS[wkey]
    L += [f"## {title} — every referenced verse, fetched and checked word-for-word", "",
          f"**{len(wver)} verses banked for this work.** Versions: {rule}", note, ""]

L += [f"**{len(VERSES)} verses banked in total.** Statuses: **CONFIRMED** = word-for-word · "
      "**EXCERPT** = word-for-word, partial · **DIFFERS** = wording differs (exact text of the "
      "specified version banked, proposal ready) · **PARAPHRASE** = reworded · ANCHOR = referenced, "
      "not quoted · RECAP = re-cited in prose. Nothing was changed in any manuscript; every "
      "ruling awaits the word `apply`.", "", "---"]

for wkey in ("hallowed", "sabbath"):
    wver = [v for v in VERSES if work_of(v) == wkey]
    if not wver: continue
    L += ["", f"# {WORKS[wkey][0].strip('*')}"]
    seen_keys = []
    for key in SEC_ORDER:
        if any(u["section"] == key and work_of(v) == wkey for v in wver for u in v["uses"]):
            seen_keys.append(key)
    for key in seen_keys:
        L += ["", "## " + label_of(key)]
        s = SECD.get(key) or {}
        if s.get("seeker_text") and key.startswith("P1"):
            L += ["", "> *The Seeker asked:* “" + s["seeker_text"].replace("The Seeker asked: ", "").strip().strip('"') + "”"]
        hits = [(u.get("article_line") or 0, v, u) for v in wver for u in v["uses"] if u["section"] == key]
        if not hits:
            continue
        byvid = {}
        for ln, v, u in hits:
            byvid.setdefault(v["id"], (v, []))[1].append((ln, u))
        for vid, (v, uselist) in sorted(byvid.items(), key=lambda kv: min(x[0] for x in kv[1][1])):
            uselist.sort(key=lambda x: x[0])
            pick = next((u for _, u in uselist if u["status"] not in ("anchor", "recap-use")), uselist[0][1])
            L += ["", f"### {v['ref']} — {STATUS_DISP.get(pick['status'], pick['status'].upper())}"]
            if pick.get("cited_as") not in (None, "no translation cited", "narrative reference"):
                L.append(f"*cited as: {pick['cited_as']}*")
            for ed in ("nets", "sinaiticus", "standard-greek", "brenton", "gnv", "kjv", "jps"):
                if ed in v["translations"]:
                    L.append(f"- **{VERNAME[ed]}:** {short(v['translations'][ed]['text'])}")
            L += flag_lines(pick)
            adj = pick.get("adjudication")
            if adj:
                if not adj.get("text"):
                    L += [f"- **Ruling — {str(adj.get('ruling', 'APPLIED')).upper()}:** {adj.get('reason') or adj.get('detail', '')}"]
                else:
                    L += [f"- **Ruling — apply {VERNAME.get(adj.get('version', '?'), '?')} exact:** {short(adj['text'])}",
                          f"  ({adj.get('reason', '')})"]
            elif pick["status"] in ("differs-minor", "differs", "paraphrase"):
                q0 = (pick.get("quotes") or [""])[0]
                lq, rq = "“", "”"
                L.append(f"- **Flag:** {pick.get('note') or ('article reads: ' + lq + q0 + rq)}")
            elif pick.get("note"):
                L.append(f"- *Note:* {pick['note']}")
            L.append(f"- *Checked {v.get('verified', '?')} · editions fetched: {', '.join(sorted(v['translations'].keys()))}*")
            sc = v.get("second_check") or {}
            if sc:
                marks = []
                for ed, rec in sc.items():
                    rn = {"sinaiticus": "Codex Sinaiticus"}.get(ed, ed)
                    if rec.get("result", "").startswith("agree"):
                        marks.append(f"{rn} ✓")
                    else:
                        marks.append(f"{rn} — {rec['result']}")
                L.append(f"- *Double-checked (second source): {' · '.join(marks)}*")

L += ["", "---", "", "## Master index (by book)", "", "| Verse | Mentions in sections | Status |", "|---|---|---|"]
def sec_rank(u):
    s = u if isinstance(u, str) else u.get("section", "")
    if s in SEC_ORDER:
        return SEC_ORDER.index(s)
    return 999
for v in VERSES:
    secs = ", ".join(sorted({u["section"] for u in v["uses"]}, key=sec_rank))
    sts = sorted({STATUS_DISP.get(u["status"], u["status"]).lower() for u in v["uses"]})
    L.append(f"| {v['ref']} | {secs} | {', '.join(sts)} |")
L += ["", "## The editions used", "",
      "- NETS (New English Translation of the Septuagint), Oxford master PDFs per book — https://ccat.sas.upenn.edu/nets/edition/ (the book's OT standard for THE BIBLICAL SABBATH)",
      "- Codex Sinaiticus Greek readings + critical apparatus — https://greeknewtestament.net (per verse, aleph line + apparatus)",
      "- Brenton Septuagint (1851 English), eBible.org — id eng-Brenton; like https://ebible.org/eng-Brenton/EXO20.htm",
      "- Geneva Bible 1599, eBible.org — id enggnv; like https://ebible.org/enggnv/JHN03.htm",
      "- King James Version (1769 standard text), eBible.org — id eng-kjv2006; like https://ebible.org/eng-kjv2006/PRO18.htm", "",
      "Each verse stores its exact source page address in *verses.json*. See *README.md* for the standing rules and the one-line method for banking a new verse."]

out = os.path.join(HERE, "glossary.md")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("glossary.md regenerated:", os.path.getsize(out), "bytes,", len(VERSES), "verses")
