# Scripture Repository — the Broad Glossary of Verified Verses

Built 2 November 2026 for **HALLOWED BE THY NAME**, and made to keep growing through
everything that comes after it — Ben Yachid, the Sabbath study, whatever the Lord leads to next.

## THE STANDING RULE (Gideon, 2 Nov 2026)

**ALWAYS use the exact text of the verse in the specified Version(s).** The specified
versions are named per work; quotes get corrected to them word-for-word. A different
Version stays only where the article's own wording is *already exact to it* — that is
the good-reason exception, and the reason is recorded on the verse's entry.

- **HALLOWED BE THY NAME specifies:** LXX **Brenton** (Old Testament) + **Geneva 1599**
  (New Testament). The KJV is the good-reason exception here (the article's uncited
  blockquotes speak KJV).
- **Ben Yachid specifies:** JPS **1917** (Tanakh) + **Geneva 1599** (NT).
- Every ruling carries its reason in `verses.json` (the entry's `adjudication.reason`).

## THE DOUBLE-CHECK (2 Nov 2026)

After the first verification pass, **every banked text was re-checked against a second,
independent online source** — result: **zero disagreements across 76 verse entries**.

| Edition banked | Second source used | Result |
|---|---|---|
| Brenton LXX (eBible) | BibleHub's "Brenton's Septuagint Translation" chapter pages + qbible.com Brenton pages | 39 exact agree + 10 agree-with-note (spelling/bracket noise in the second site's digital text) |
| Geneva 1599 (eBible) | TextusReceptusbibles.com verse tables | 76 agree |
| King James (eBible) | BibleHub King James chapter pages | 76 agree |

Per-entry verdicts with the second source's page address live in `verses.json`
(`second_check` on each entry). Two notes preserved for honesty: qbible.com is a
names-restored text (it numbers Joshua and Jeremiah by the Hebrew order), and eBible's
Brenton Jeremiah follows the LXX order — the New-Covenant verse sits at eBible's
Jeremiah 38:31-33 and at the Hebrew-numbered 31:31-33 elsewhere; the texts agree word
for word. During the double-check one bank error was caught and fixed: the Jeremiah
31:33 entry had stored the wrong Brenton verse (a direct-lookup artifact); it now
stores the true Brenton New-Covenant text, confirmed by both sources.

## What this is

Every scripture the article quotes or references was **fetched from a named online
digital edition and checked word-for-word**, then banked here. The point: once a verse
is in the bank, no future session ever has to go online to confirm it again. Copy the
text straight from *glossary.md* or *verses.json* and write.

| File | What it is |
|---|---|
| `glossary.md` | The human-readable Broad Glossary, divided by the article's 17 Seeker questions, with the canonical texts of each verse and a status flag. |
| `verses.json` | The machine bank — same verses, with exact source page addresses, article line numbers, and verify dates. |
| `scripts/verify_verses.py` | The little workhorse: fetches the three editions (once), and looks up any verse from the terminal. |

## The editions (all public domain, from eBible.org)

| Tag | Edition | Covers |
|---|---|---|
| `brenton` | **Brenton Septuagint** — Sir Lancelot C. L. Brenton's English Septuagint (1851), digital edition *eng-Brenton* | Old Testament only |
| `gnv` | **Geneva Bible 1599**, digital edition *enggnv* | whole Bible |
| `kjv` | **King James Version** (1769 standard text), digital edition *eng-kjv2006* | whole Bible |

Chapter pages spell out the addresses, e.g.:
- brenton → https://ebible.org/eng-Brenton/EXO20.htm
- gnv → https://ebible.org/enggnv/JHN03.htm
- kjv → https://ebible.org/eng-kjv2006/PRO18.htm

To re-download the editions (only needed if the bank must check a verse from a book not
yet parsed locally):

```bash
python3 scripts/verify_verses.py --download
```

That saves the three editions into `editions/` inside this folder and they never need
fetching again. (First build downloaded them to a scratch folder; the script puts them
in the repo so they survive.)

## How to verify a new verse

```bash
python3 scripts/verify_verses.py Genesis 22:8 Psalm 104:29-30 John 20:22
```

Each verse prints with its text from all three editions and the source page it came
from. Nothing is guessed; if an edition is missing the verse it says so. Then the
verified text can be entered into `verses.json` / `glossary.md` by hand (or ask Hermes
to do it) — with the date added.

## Statuses

- **confirmed** — the article's quote matches the cited edition word-for-word.
- **confirmed-excerpt** — word-for-word but partial (ellipsis, or the quote's lead-in).
- **differs-minor** — same verse, a few words changed (each note says exactly what).
- **paraphrase** — the article rewords the verse (note gives the article's text).
- **anchor** — a verse referenced narratively (a chapter named, not quoted).
- **commentary** — the article's own rendering (e.g. Ehyeh Asher Ehyeh); canonical texts banked for reference.

## Standing conventions (already in force)

- **For this article:** quotes cited *LXX, Brenton* are held to Brenton's English text;
  quotes cited *Geneva* to the 1599 Geneva. Uncited blockquotes were diagnosed against
  KJV (their usual voice) with GNV and Brenton banked alongside.
- **Psalms catch:** the article cites Hebrew-psalm numbers (Ps 22:16); Brenton prints the
  old LXX numbers (Ps 21:17) — both are recorded on each entry.
- **Two other Brenton numbering facts:** Brenton relocates the writing-on-the-stones
  verses of Joshua 8:30–32 into Joshua 9:2 (his footnote says so), and the LXX's
  Jeremiah runs eight chapters short of the Hebrew (the New-Covenant verse, Hebrew
  Jeremiah 31:33, is Brenton Jeremiah 38:31–33). Both are recorded in the bank.
- **Ben Yachid standard** for the next bank entries: *JPS 1917* (Tanakh) + *Geneva 1599*
  (NT). JPS was verified in the Ben Yachid work at mechon-mamre.org; add JPS texts here
  when those verses next need checking.
- Hebrew names in the body (Moshe, Yohoshua, Yerushalayim, Yeshua) are the author's
  intentional practice — never flagged as citation errors.

## What changed in the manuscript: nothing — yet

All DIFFERS/PARAPHRASE flags in the glossary are **proposals awaiting approval**. The
article HTML was not touched. After approval, the flagged quotes get corrected and the
PDF regenerates as usual.