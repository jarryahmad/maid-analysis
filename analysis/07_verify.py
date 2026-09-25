"""
Verification pass. Fails loudly if anything on the page has drifted from source.

The transcribed Quebec prognosis table is the only file in this repo typed by
hand rather than parsed, so it gets the strictest check: every count must appear
in the extracted text of the PDF it claims to come from, inside that report's
"Pronostic vital" block, and every row must sum to its published total.
"""
import csv, json, re, sys

FAILS, CHECKS = [], 0

def check(label, cond, detail=""):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(f"{label}  {detail}")

def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))

# ---------------------------------------------------------------- Quebec
QC_KEYS = ["le_1wk", "le_2wk", "le_1mo", "le_3mo", "le_6mo", "le_1yr", "le_2yr",
           "eol_unspecified", "gt_1yr_not_eol", "gt_1yr_eol_judged"]

def prognosis_block(text):
    """The report's prognosis table: from the 'Pronostic vital' heading to 'Total'."""
    m = re.search(r"Pronostic[^\n]{0,40}?Nombre\s+%(.{0,900}?)Total\s+([\d\s\u00a0\u202f]+)",
                  text, re.S)
    return m


for r in load("data/source/quebec_prognosis_by_year.csv"):
    period, fn = r["period"], r["source_file"]
    txt_path = f"data/raw/lit/{fn[:-4]}.txt"
    try:
        text = open(txt_path, encoding="utf-8").read()
    except FileNotFoundError:
        FAILS.append(f"[qc {period}] missing extracted text {txt_path}"); CHECKS += 1
        continue

    m = prognosis_block(text)
    check(f"[qc {period}] prognosis table located in {fn}", m is not None)
    if not m:
        continue
    block, total_in_pdf = m.group(1), m.group(2)
    norm = lambda s: re.sub(r"[\s ]", "", s)

    # Every transcribed count must appear as a number in that block.
    for k in QC_KEYS:
        if not r[k]:
            continue
        v = int(r[k])
        pat = re.compile(r"(?<!\d)" + r"[\s ]?".join(f"{v:,}".replace(",", " ").split())
                         .replace(" ", r"[\s ]?") + r"(?!\d)")
        found = re.search(pat, block) or re.search(rf"(?<!\d){v}(?!\d)", norm(block))
        check(f"[qc {period}] {k}={v} present in source block", found is not None,
              f"(not found in {fn})")

    # Published total must match the transcribed total and the row sum.
    row_sum = sum(int(r[k]) for k in QC_KEYS if r[k])
    check(f"[qc {period}] row sums to published total",
          row_sum == int(r["total"]),
          f"(sum={row_sum}, stated={r['total']})")
    check(f"[qc {period}] stated total appears in PDF",
          norm(str(r["total"])) in norm(total_in_pdf) or str(r["total"]) in norm(block),
          f"(pdf tail={total_in_pdf.strip()[:20]!r})")

# --------------------------------------------------- Health Canada figures
vol = load("data/clean/maid_by_year.csv")
fig22a = {r[0]: r for r in csv.reader(open("data/clean/tables/2024__figure-2-2a.csv"))}
for r in vol:
    y = r["year"]
    if y in fig22a:
        src = fig22a[y]
        check(f"[hc {y}] total matches Figure 2.2a",
              src[3].replace(",", "") == r["total_provisions"],
              f"({src[3]} vs {r['total_provisions']})")

k = json.load(open("data/clean/key_numbers.json"))
check("[hc] 2024 tracks sum to total", k["t1"] + k["t2"] == k["tot24"])
check("[hc] Health Canada's published 5.1% share is quoted verbatim",
      k["hc_published_share_24"] == 5.1)
check("[hc] computed share is within 0.1pt of Health Canada's published figure",
      abs(k["maid_share_24"] - k["hc_published_share_24"]) <= 0.1,
      f"(computed {k['maid_share_24']}, published {k['hc_published_share_24']})")

# ------------------------------------- narrative claims quoted on the page
QUOTES = [
    ("data/raw/hc-annual-2024.txt",
     "Self-perceived burden was cited as a sole source of suffering in fewer than five "
     "MAID cases and alongside only one other type of suffering in 18 cases."),
    ("data/raw/hc-annual-2024.txt",
     "Isolation or loneliness was not reported as a sole source of suffering for any "
     "MAID cases in 2024."),
    ("data/raw/hc-annual-2024.txt",
     "In 2024, 5.1% of people in Canada who died received MAID"),
    ("data/raw/hc-annual-2023.txt",
     "data collected in 2023 are not fully comparable with the data collected in "
     "previous years"),
    ("data/raw/lit/pbo-c7-2020.txt",
     "14% will see their life shortened by 2 weeks, 25% by one month"),
    ("data/raw/lit/pbo-c7-2020.txt",
     "we assumed all these patients would see their life shortened by a"),
    ("data/raw/lit/pbo-c7-2020.txt",
     "except for the estimated life remaining"),
    ("data/raw/lit/csfv_rapport_2018-2023.txt", "75,7 % (n = 979) en 2018-2019"),
    # The Commission's own statement of the trend, paraphrased on the page.
    ("data/raw/lit/csfv_rapport_2018-2023.txt",
     "la proportion des personnes avec un pronostic plus long a augmenté"),
    # Figures quoted in the Track 1 vs Track 2 profile paragraph.
    ("data/raw/hc-annual-2024.txt",
     "the percentage of people living alone (41.7%) was higher than the percentage of "
     "people living with family (30.6%)"),
    ("data/raw/hc-annual-2024.txt",
     "of Track 1 respondents self-identified as having a disability"),
]
for path, quote in QUOTES:
    body = re.sub(r"\s+", " ", open(path, encoding="utf-8").read())
    check(f"[quote] {quote[:52]}…", re.sub(r"\s+", " ", quote) in body, f"({path})")

# ----------------------------------------------------------------- report
print(f"{CHECKS - len(FAILS)}/{CHECKS} checks passed")
if FAILS:
    print("\nFAILED:")
    for f_ in FAILS:
        print("  " + f_)
    sys.exit(1)
print("all source checks passed")
