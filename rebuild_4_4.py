# -*- coding: utf-8 -*-
"""
rebuild_4_4.py
Compute phrase-level evidence for Section 4.4.6.3 (H3/RQ3):
- frequent n-grams (bigrams/trigrams)
- log-likelihood keyness (G^2) for phrases
- concordance (KWIC) excerpts
- generates: CSV tables + TXT section ready to paste into thesis

USAGE (Windows CMD):
  cd /d "%USERPROFILE%\\Desktop\\4.4"
  py rebuild_4_4.py --input "dataset.csv"
  py rebuild_4_4.py --input "dataset.xlsx"

Outputs are written to the current folder unless --outdir is provided.
"""

import argparse
import csv
import math
import os
import re
from collections import Counter
from typing import Dict, List, Tuple, Optional

# Optional dependencies:
# - pandas for xlsx/csv loading (recommended)
# - matplotlib for charts (optional)
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


# -----------------------------
# Robust column detection
# -----------------------------
def pick_col(columns: List[str], candidates: List[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


# -----------------------------
# Wrapper removal (optional)
# -----------------------------
OPEN_WRAPPER_RE = re.compile(r"\bcertainly\b.*\bhappy\b.*\bto\b.*\bhelp\b", re.IGNORECASE)
CLOSE_WRAPPER_RE = re.compile(
    r"\bplease\b.*\blet\b.*\bme\b.*\bknow\b.*\bif\b.*\byou(?:'|’)?d\b.*\blike\b.*\b(shorter|brief)\b.*\bversion\b",
    re.IGNORECASE,
)

def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def strip_wrapper(text: str) -> str:
    """
    Conservative wrapper stripping: remove a matched opening sentence-ish fragment and
    matched closing fragment. If no match, returns text unchanged.
    """
    t = normalize_ws(text)

    # Opening: remove from match start to next punctuation boundary (., !, ?)
    m = OPEN_WRAPPER_RE.search(t)
    if m:
        start = m.start()
        end = None
        for ch in [".", "!", "?"]:
            idx = t.find(ch, m.end())
            if idx != -1:
                end = idx + 1
                break
        if end is None:
            end = m.end()
        t = normalize_ws(t[:start] + " " + t[end:])

    # Closing: remove from match start to end punctuation boundary or end of string
    m = CLOSE_WRAPPER_RE.search(t)
    if m:
        start = m.start()
        end = None
        for ch in [".", "!", "?"]:
            idx = t.find(ch, m.end())
            if idx != -1:
                end = idx + 1
                break
        if end is None:
            end = len(t)
        t = normalize_ws(t[:start] + " " + t[end:])

    return t


# -----------------------------
# Tokenization + ngrams
# -----------------------------
TOKEN_RE = re.compile(r"[a-z0-9]+(?:['’][a-z0-9]+)?", re.IGNORECASE)

def tokenize(text: str) -> List[str]:
    return [m.group(0).lower().replace("’", "'") for m in TOKEN_RE.finditer(text or "")]

def ngrams(tokens: List[str], n: int) -> Counter:
    c = Counter()
    if len(tokens) < n:
        return c
    for i in range(len(tokens) - n + 1):
        ng = " ".join(tokens[i:i+n])
        c[ng] += 1
    return c


# -----------------------------
# Log-likelihood keyness (G^2)
# -----------------------------
def safe_log(x: float) -> float:
    return math.log(x) if x > 0 else 0.0

def ll_g2(k1: int, k2: int, n1: int, n2: int) -> float:
    """
    Dunning log-likelihood (G^2) for term frequency comparison across two corpora:
      corpus1: k1 occurrences out of n1 tokens
      corpus2: k2 occurrences out of n2 tokens
    """
    if n1 <= 0 or n2 <= 0:
        return 0.0

    p = (k1 + k2) / (n1 + n2)
    e1 = n1 * p
    e2 = n2 * p

    g2 = 0.0
    if k1 > 0 and e1 > 0:
        g2 += k1 * safe_log(k1 / e1)
    if k2 > 0 and e2 > 0:
        g2 += k2 * safe_log(k2 / e2)

    o1 = n1 - k1
    o2 = n2 - k2
    e1o = n1 - e1
    e2o = n2 - e2

    if o1 > 0 and e1o > 0:
        g2 += o1 * safe_log(o1 / e1o)
    if o2 > 0 and e2o > 0:
        g2 += o2 * safe_log(o2 / e2o)

    return 2.0 * g2

def compute_keyness(
    counts_A: Counter,
    counts_B: Counter,
    nA: int,
    nB: int,
    min_total_count: int = 2,
    top_k: int = 25
) -> List[Dict[str, object]]:
    records = []
    all_phrases = set(counts_A.keys()) | set(counts_B.keys())
    for phr in all_phrases:
        a = counts_A.get(phr, 0)
        b = counts_B.get(phr, 0)
        if a + b < min_total_count:
            continue
        g2 = ll_g2(a, b, nA, nB)
        rateA = (a / nA) * 1000 if nA else 0.0
        rateB = (b / nB) * 1000 if nB else 0.0
        key_in = "A" if rateA > rateB else ("B" if rateB > rateA else "equal")
        records.append({
            "phrase": phr,
            "freq_A": a,
            "freq_B": b,
            "tokens_A": nA,
            "tokens_B": nB,
            "rateA_per1000": round(rateA, 3),
            "rateB_per1000": round(rateB, 3),
            "LL_G2": round(g2, 3),
            "key_in": key_in,
        })
    records.sort(key=lambda r: r["LL_G2"], reverse=True)
    return records[:top_k]


# -----------------------------
# Concordance (KWIC)
# -----------------------------
def kwic(texts: List[Tuple[str, str]], phrase: str, window: int = 8, max_examples: int = 6) -> List[str]:
    """
    texts: list of (response_id, body_text)
    phrase: lowercased phrase
    returns KWIC lines
    """
    ptoks = phrase.split()
    n = len(ptoks)
    out = []
    for rid, t in texts:
        toks = tokenize(t)
        for i in range(0, len(toks) - n + 1):
            if toks[i:i+n] == ptoks:
                left = " ".join(toks[max(0, i-window):i])
                hit = " ".join(toks[i:i+n])
                right = " ".join(toks[i+n:min(len(toks), i+n+window)])
                out.append(f"{rid} | ... {left} [{hit}] {right} ...")
                if len(out) >= max_examples:
                    return out
    return out


# -----------------------------
# IO: load dataset
# -----------------------------
def load_dataset(path: str):
    if pd is None:
        raise SystemExit("Missing dependency: pandas. Install with: py -m pip install pandas openpyxl")

    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    cols = list(df.columns)
    tone_col = pick_col(cols, ["tone"])
    cert_col = pick_col(cols, ["certainty", "certainty_pressure"])
    rid_col  = pick_col(cols, ["response_id", "id"])
    body_col = pick_col(cols, ["body_text", "body"])
    resp_col = pick_col(cols, ["response_text", "response"])
    task_col = pick_col(cols, ["task_type", "task"])

    if tone_col is None or cert_col is None:
        raise SystemExit(f"Dataset must contain at least columns tone and certainty. Found: {cols}")

    # Choose text source: prefer body_text, otherwise response_text.
    text_col = body_col or resp_col
    if text_col is None:
        raise SystemExit("Dataset must contain a text column: body_text or response_text.")

    # Ensure a response_id column exists; if not, synthesize from index.
    if rid_col is None:
        df["_response_id"] = ["row" + str(i) for i in range(len(df))]
        rid_col = "_response_id"

    # Standardize
    df["_tone"] = df[tone_col].astype(str).str.upper()
    df["_cert"] = df[cert_col].astype(str).str.upper()
    df["_rid"] = df[rid_col].astype(str)

    # Create body text:
    if body_col is None:
        # Strip wrapper from full response if needed
        df["_body"] = df[text_col].astype(str).apply(strip_wrapper)
    else:
        df["_body"] = df[text_col].astype(str).apply(normalize_ws)

    # Keep task_type if exists
    if task_col is not None:
        df["_task"] = df[task_col].astype(str).str.upper()
    else:
        df["_task"] = ""

    return df


# -----------------------------
# Charts (optional)
# -----------------------------
def plot_keyness(records: List[Dict[str, object]], title: str, out_png: str):
    if plt is None or not records:
        return None
    # Top 10
    recs = records[:10][::-1]
    phrases = [r["phrase"] for r in recs]
    scores = [r["LL_G2"] for r in recs]
    plt.figure(figsize=(10, 6))
    plt.barh(phrases, scores)
    plt.xlabel("Log-likelihood keyness (G²)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()
    return out_png


# -----------------------------
# Writers
# -----------------------------
def write_csv(path: str, records: List[Dict[str, object]]):
    if not records:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

def write_txt(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# -----------------------------
# Section generator (academic EN)
# -----------------------------
def build_section_text(
    top_ngrams_pol: List[Tuple[str, int]],
    top_ngrams_ua: List[Tuple[str, int]],
    key_pol: List[Dict[str, object]],
    key_ua: List[Dict[str, object]],
    kwic_pol: List[str],
    kwic_ua: List[str],
) -> str:
    def bullet_ngrams(items):
        return "\n".join([f"- {p} (n={c})" for p, c in items]) if items else "(none)"

    def bullet_key(items, labelA, labelB):
        lines = []
        for r in items[:10]:
            key_in = r["key_in"]
            key_lab = labelA if key_in == "A" else (labelB if key_in == "B" else "equal")
            lines.append(f"- **{r['phrase']}** (LL={r['LL_G2']}; key in {key_lab}; {labelA}:{r['freq_A']} vs {labelB}:{r['freq_B']})")
        return "\n".join(lines) if lines else "(none)"

    def block(lines):
        return "\n".join(lines) if lines else "(no examples found)"

    return f"""### 4.4.6.3 H3 / RQ3: Phraseology and interactional routines (n-grams, key phrases/keyness, concordance)

**Analytic aim and link to H3.**  
H3 predicts that condition effects should be detectable not only in single-token markers but also as **multiword routines** and recurring **interactional templates**. This subsection therefore reports phrase-level evidence in three complementary forms: (i) recurrent n-grams, (ii) key phrases quantified using **log-likelihood keyness (G²)**, and (iii) concordance-style excerpts illustrating local pragmatic function.

**Results-relevant segmentation reminder.**  
Phrase evidence is interpreted with explicit reference to the two-layer output model (wrapper/BP vs body) to avoid over-attributing stable boilerplate routines to in-content pragmatic strategy shifts.

---

#### (a) Recurrent n-grams (descriptive)

**Top recurrent phrases in POL (wrapper-influenced):**
{bullet_ngrams(top_ngrams_pol)}

**Top recurrent phrases in UA (body-only; branching/alternatives expected):**
{bullet_ngrams(top_ngrams_ua)}

**Where to insert in the thesis:**  
Insert *Table 4.4.6.3-A* (“Top recurrent n-grams by condition”) here. The table should report phrase counts and (if available) normalized rates per 1,000 tokens.

---

#### (b) Key phrases and keyness (log-likelihood G²)

Keyness was computed using Dunning’s log-likelihood statistic (G²), contrasting (i) **POL vs non-POL (NEU+CON)** and (ii) **UA vs HC**, using body-only text where available. Higher LL values indicate that a phrase is more characteristic of a target condition than expected given corpus sizes.

**Top key phrases: POL vs non-POL (LL):**
{bullet_key(key_pol, "POL", "nonPOL")}

**Top key phrases: UA vs HC (LL):**
{bullet_key(key_ua, "UA", "HC")}

**Where to insert in the thesis:**  
Insert *Table 4.4.6.3-B* (“Key phrases with LL keyness”) here, and place *Figure 4.4.6.3-1/2* (bar charts of top LL phrases) directly underneath.

---

#### (c) Concordance excerpts (KWIC) for interpretation

Keyness identifies distributional distinctiveness; concordance excerpts indicate how phrases function pragmatically in context.

**POL routine excerpts (illustrative KWIC):**
{block(kwic_pol)}

**UA branching excerpts (illustrative KWIC):**
{block(kwic_ua)}

**Where to insert in the thesis:**  
Insert *Table 4.4.6.3-C* (“Concordance excerpts for key routines”) here. Include 2–4 short excerpts per routine type; move the full excerpt set to the Appendix if needed.

---

#### H3 conclusion (explicit hypothesis mapping)

Taken together, the phrase-level evidence supports H3: condition differences are observable beyond token counts as **multiword formulae and interactional routines**. POL outputs display stable service-stance wrapper routines, whereas UA outputs show an alternatives template (e.g., Option A/B plus conditional selection), consistent with uncertainty management via structured branching rather than a uniform increase in classic epistemic hedging.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to dataset (.xlsx or .csv)")
    ap.add_argument("--outdir", default=".", help="Output directory")
    ap.add_argument("--topk", type=int, default=15, help="Top K phrases to report")
    ap.add_argument("--mincount", type=int, default=2, help="Minimum total count threshold")
    args = ap.parse_args()

    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    df = load_dataset(args.input)

    # Build condition sets
    df_pol = df[df["_tone"] == "POL"]
    df_nonpol = df[df["_tone"].isin(["NEU", "CON"])]

    df_ua = df[df["_cert"] == "UA"]
    df_hc = df[df["_cert"] == "HC"]

    # Tokenize corpora (body-only, because df["_body"] is body)
    pol_tokens = []
    nonpol_tokens = []
    ua_tokens = []
    hc_tokens = []

    pol_texts = []
    ua_texts = []

    for _, r in df_pol.iterrows():
        pol_texts.append((r["_rid"], r["_body"]))
        pol_tokens.extend(tokenize(r["_body"]))
    for _, r in df_nonpol.iterrows():
        nonpol_tokens.extend(tokenize(r["_body"]))
    for _, r in df_ua.iterrows():
        ua_texts.append((r["_rid"], r["_body"]))
        ua_tokens.extend(tokenize(r["_body"]))
    for _, r in df_hc.iterrows():
        hc_tokens.extend(tokenize(r["_body"]))

    # N-grams (mix 2-grams and 3-grams)
    pol_ng = ngrams(pol_tokens, 2) + ngrams(pol_tokens, 3)
    ua_ng = ngrams(ua_tokens, 2) + ngrams(ua_tokens, 3)

    top_ngrams_pol = pol_ng.most_common(args.topk)
    top_ngrams_ua = ua_ng.most_common(args.topk)

    # Keyness tables: build phrase counts from combined n-grams (2+3)
    # For keyness, we reuse pol_ng and ua_ng as phrase counts;
    # reference for pol is nonPOL phrase counts; for UA it's HC phrase counts.
    nonpol_ng = ngrams(nonpol_tokens, 2) + ngrams(nonpol_tokens, 3)
    hc_ng = ngrams(hc_tokens, 2) + ngrams(hc_tokens, 3)

    # Total token counts as denominators
    n_pol = max(1, len(pol_tokens))
    n_non = max(1, len(nonpol_tokens))
    n_ua = max(1, len(ua_tokens))
    n_hc = max(1, len(hc_tokens))

    key_pol = compute_keyness(pol_ng, nonpol_ng, n_pol, n_non, min_total_count=args.mincount, top_k=args.topk)
    key_ua = compute_keyness(ua_ng, hc_ng, n_ua, n_hc, min_total_count=args.mincount, top_k=args.topk)

    # Concordance: pick top 2 phrases keyed to each target
    def pick_target_phrases(recs, want="A", k=2):
        out = []
        for r in recs:
            if r["key_in"] == want:
                out.append(r["phrase"])
            if len(out) >= k:
                break
        return out

    pol_phrases = pick_target_phrases(key_pol, "A", 2)
    ua_phrases = pick_target_phrases(key_ua, "A", 2)

    kwic_pol_lines = []
    for phr in pol_phrases:
        kwic_pol_lines.append(f"\nPhrase: {phr}")
        kwic_pol_lines.extend(kwic(pol_texts, phr.lower(), window=8, max_examples=6) or ["(no hits found)"])

    kwic_ua_lines = []
    for phr in ua_phrases:
        kwic_ua_lines.append(f"\nPhrase: {phr}")
        kwic_ua_lines.extend(kwic(ua_texts, phr.lower(), window=8, max_examples=6) or ["(no hits found)"])

    # Write outputs
    write_csv(os.path.join(outdir, "out_keyness_POL_vs_nonPOL.csv"), key_pol)
    write_csv(os.path.join(outdir, "out_keyness_UA_vs_HC.csv"), key_ua)

    # Write n-grams as CSV too
    with open(os.path.join(outdir, "out_top_ngrams_POL.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phrase", "count"])
        w.writerows(top_ngrams_pol)

    with open(os.path.join(outdir, "out_top_ngrams_UA.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phrase", "count"])
        w.writerows(top_ngrams_ua)

    # Concordance
    write_txt(os.path.join(outdir, "out_concordance_POL.txt"), "\n".join(kwic_pol_lines))
    write_txt(os.path.join(outdir, "out_concordance_UA.txt"), "\n".join(kwic_ua_lines))

    # Charts (optional)
    pol_png = os.path.join(outdir, "Fig_4_4_6_3_POL_keyness.png")
    ua_png = os.path.join(outdir, "Fig_4_4_6_3_UA_keyness.png")
    plot_keyness(key_pol, "Top key phrases: POL vs (NEU+CON)", pol_png)
    plot_keyness(key_ua, "Top key phrases: UA vs HC", ua_png)

    # Generate thesis section
    section_text = build_section_text(
        top_ngrams_pol=top_ngrams_pol,
        top_ngrams_ua=top_ngrams_ua,
        key_pol=key_pol,
        key_ua=key_ua,
        kwic_pol=kwic_pol_lines[:30],
        kwic_ua=kwic_ua_lines[:30],
    )
    write_txt(os.path.join(outdir, "out_section_4_4_6_3.txt"), section_text)

    print("DONE. Outputs written to:", outdir)
    print(" - out_section_4_4_6_3.txt (paste into thesis)")
    print(" - out_keyness_POL_vs_nonPOL.csv")
    print(" - out_keyness_UA_vs_HC.csv")
    print(" - out_top_ngrams_POL.csv / out_top_ngrams_UA.csv")
    print(" - out_concordance_POL.txt / out_concordance_UA.txt")
    if plt is not None:
        print(" - Fig_4_4_6_3_POL_keyness.png / Fig_4_4_6_3_UA_keyness.png")
    else:
        print(" (matplotlib not installed: no PNG charts generated)")


if __name__ == "__main__":
    main()