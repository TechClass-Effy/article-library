#!/usr/bin/env python3
"""build_glossary.py — regenerate the Broad Glossary from verses.json alone.

python3 scripts/build_glossary.py            # writes glossary.md next to versions
Sections, statuses, rulings and adjudications all live in verses.json (meta.sections /
meta.section_order / per-use adjudication), so this never needs the article again.
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = json.load(open(os.path.join(HERE, "verses.json"), encoding="utf-8"))
META, VERSES = src["meta"], src["verses"]
V = {v["id"]: v for v in VERSES}
SEC_ORDER = META.get("section_order") or sorted({u["section"] for v in VERSES for u in v["uses"]})
SECD = {s["key"]: s for s in META.get("sections", [])}

STATUS_DISP = {"confirmed": "CONFIRMED", "confirmed-excerpt": "CONFIRMED (EXCERPT)",
               "differs-minor": "DIFFERS", "paraphrase": "PARAPHRASE",
               "anchor": "ANCHOR", "commentary": "COMMENTARY"}
VERNAME = {"brenton": "Brenton LXX", "gnv": "Geneva 1599", "kjv": "KJV", "jps": "JPS 1917"}

def short(s, n=420):
    return "\u201c" + (s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …") + "\u201d"

L = []
L += ["# BROAD GLOSSARY OF VERIFIED SCRIPTURES", "",
      "## *HALLOWED BE THY NAME* — every referenced verse, fetched and checked word-for-word", "",
      "**2 November 2026** · Divided by the seventeen Seeker questions, exactly as the book is divided. "
      "Once a verse is banked here, future writing can copy it straight from this page — no fresh online check needed.", ""]
counts = {}
for v in VERSES:
    for u in v["uses"]:
        counts[u["status"]] = counts.get(u["status"], 0) + 1
L += [f"**{len(VERSES)} verses banked**, {sum(counts.values())} checks. Statuses: **CONFIRMED** = word-for-word · "
      "**EXCERPT** = word-for-word, partial · **DIFFERS** = few words off · **PARAPHRASE** = reworded · "
      "ANCHOR = referenced, not quoted.", "",
      "| Status | Count |", "|---|---|"]
for k in ("confirmed", "confirmed-excerpt", "differs-minor", "paraphrase", "anchor", "commentary"):
    L.append(f"| {STATUS_DISP[k]} | {counts.get(k, 0)} |")
L += ["", "**The rulings below are final per the standing rule** (exact text of the specified versions: "
      "LXX Brenton for this article's Old Testament, Geneva 1599 for its New Testament; KJV where the "
      "article's own blockquote voice is KJV). Nothing was changed in the manuscript; each ruling awaits the word `apply`.", "", "---"]

for key in SEC_ORDER:
    s = SECD.get(key, {})
    label = (s.get("label", key) + (" — " + s["sub"] if s.get("sub") else ""))
    L += ["", "## " + label]
    if s.get("seeker_text") and key.startswith("P1"):
        L += ["", "> *The Seeker asked:* \u201c" + s["seeker_text"].replace("The Seeker asked: ", "").strip().strip('"') + "\u201d"]
    hits = [(u.get("article_line") or 0, v, u) for v in VERSES for u in v["uses"] if u["section"] == key]
    if not hits:
        L += ["", "*No scripture referenced here — this stretch is letters, history, and the breath itself.*"]
        continue
    byvid = {}
    for ln, v, u in hits:
        if v["id"] in byvid:
            byvid[v["id"]][1].append((ln, u))
        else:
            byvid[v["id"]] = (v, [(ln, u)])
    for vid, (v, uselist) in sorted(byvid.items(), key=lambda kv: min(x[0] for x in kv[1][1])):
        uselist.sort(key=lambda x: x[0])
        pick = next((u for _, u in uselist if u["status"] != "anchor"), uselist[0][1])
        L += ["", f"### {v['ref']} — {STATUS_DISP[pick['status']]}"]
        if v.get("lxx_note"):
            L.append(f"*Cited as {pick['cited_as']}; Brenton prints it as {v['lxx_note']}.*")
        elif pick["cited_as"] != "no translation cited":
            L.append(f"*cited as: {pick['cited_as']}*")
        for ed in ("brenton", "gnv", "kjv", "jps"):
            if ed in v["translations"]:
                body = v["translations"][ed]["text"]
                L.append(f"- **{VERNAME[ed]}:** {short(body)}")
        adj = pick.get("adjudication")
        if adj:
            rn = {"brenton": "Brenton LXX", "gnv": "Geneva 1599", "kjv": "KJV", "jps": "JPS 1917"}[adj["version"]]
            L += [f"- **Ruling — apply {rn} exact:** {short(adj['text'])}",
                  f"  ({adj['reason']})"]
        elif pick["status"] in ("differs-minor", "paraphrase"):
            q0 = (pick.get("quotes") or [""])[0]
            lq = "\u201c"
            rq = "\u201d"
            L.append(f"- **Flag:** {pick.get('note') or ('article reads: ' + lq + q0 + rq)}")
        elif pick.get("note"):
            L.append(f"- *Note:* {pick['note']}")
        L.append(f"- *Checked 2 Nov 2026 · editions fetched: {', '.join(sorted(v['translations'].keys()))}*")
        sc = v.get("second_check") or {}
        if sc:
            marks = []
            for ed, rec in sc.items():
                if rec["result"] == "agree":
                    marks.append(f"{VERNAME[ed]} \u2713")
                elif rec["result"] == "agree-minor":
                    marks.append(f"{VERNAME[ed]} \u2713 (minor: {rec.get('loc') or rec.get('sim')})")
                else:
                    marks.append(f"{VERNAME[ed]} \u2014 {rec['result']}")
            L.append(f"- *Double-checked (2 Nov 2026, second online source): {' · '.join(marks)}*")

L += ["", "---", "", "## Master index (by book)", "", "| Verse | Mentions in sections | Status |", "|---|---|---|"]
for v in VERSES:
    secs = ", ".join(sorted({u["section"] for u in v["uses"]}, key=SEC_ORDER.index))
    sts = sorted({STATUS_DISP[u["status"]].lower() for u in v["uses"]})
    L.append(f"| {v['ref']} | {secs} | {', '.join(sts)} |")
L += ["", "## The online editions used", "",
      "- Brenton Septuagint (1851 English translation), eBible.org — id eng-Brenton; chapter pages like https://ebible.org/eng-Brenton/EXO20.htm",
      "- Geneva Bible 1599, eBible.org — id enggnv; like https://ebible.org/enggnv/JHN03.htm",
      "- King James Version (1769 standard text), eBible.org — id eng-kjv2006; like https://ebible.org/eng-kjv2006/PRO18.htm", "",
      "Each verse stores its exact source page address in *verses.json*. See *README.md* for the standing rules and the one-line method for banking a new verse."]

out = os.path.join(HERE, "glossary.md")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("glossary.md regenerated:", os.path.getsize(out), "bytes,", len(VERSES), "verses")