"""
Build the clean analytical datasets used by the site.

Every output CSV carries a `source` column or a header comment naming the exact
table and URL it came from. Nothing here is estimated or imputed unless the
column name says so.
"""
import csv, json, os, re

CLEAN = "data/clean"
HC = ("https://www.canada.ca/en/health-canada/services/publications/"
      "health-system-services/annual-report-medical-assistance-dying-{y}.html")

def read_table(path):
    with open(path, encoding="utf-8") as f:
        return [r for r in csv.reader(f)]

def num(s):
    s = (s or "").replace(",", "").replace(" ", "").strip()
    if s in ("", "NA", "X", "-", "-"):
        return None
    try:
        return float(s) if "." in s else int(s)
    except ValueError:
        return None

def write(name, header, rows, comment=None):
    path = os.path.join(CLEAN, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        if comment:
            for line in comment.strip().split("\n"):
                f.write("# " + line.strip() + "\n")
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {name} ({len(rows)} rows)")

# ---------------------------------------------------------------- 1. volume
def build_volume():
    # 2019-2024 from the 2024 report, Figure 2.2a (the latest revised series).
    fig = read_table(f"{CLEAN}/tables/2024__figure-2-2a.csv")[1:]
    series = {int(r[0]): (num(r[1]), num(r[2]), num(r[3])) for r in fig}
    # 2016-2018 from the 2019 report, Table 3.1 (no track split existed pre-2021).
    t31 = read_table(f"{CLEAN}/tables/2019__table-3-1-total-reported-maid-deaths-in-canada-"
                     "by-jurisdiction-2016-to-2019.csv")
    early = {int(r[0]): num(r[-1]) for r in t31[1:] if r[0].strip() in ("2016", "2017", "2018")}

    # Total deaths in Canada, StatCan 13-10-0708-01 (vital statistics, calendar year).
    deaths = {}
    with open("data/raw/statcan/13100708/13100708.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if (r["GEO"] == "Canada, place of residence"
                    and r["Month of death"] == "Total, month of death"
                    and r["Characteristics"] == "Number of deaths"):
                deaths[int(r["REF_DATE"])] = num(r["VALUE"])

    rows = []
    for y in range(2016, 2025):
        if y in early:
            t1 = t2 = None
            total = early[y]
            src = "HC 2019 annual report, Table 3.1"
        else:
            t1, t2, total = series[y]
            src = "HC 2024 annual report, Figure 2.2a"
        d = deaths.get(y)
        rows.append([y, t1, t2, total, d,
                     round(100 * total / d, 2) if d else None, src])
    write("maid_by_year.csv",
          ["year", "track_1", "track_2", "total_provisions",
           "all_deaths_canada", "maid_pct_of_all_deaths", "source"],
          rows,
          comment=f"""
          MAID provisions in Canada by calendar year and track, with total deaths.
          2016-2018 totals: {HC.format(y=2019)} (Table 3.1). No track split existed
            before Bill C-7 (2021); Quebec reported 18 Track-2-equivalent provisions in
            2020 under a court exemption.
          2019-2024: {HC.format(y=2024)} (Figure 2.2a). Health Canada notes
            "Previous years' reporting has been revised to include corrections and
            additional reports", so 2019 here (5,461) differs from the 5,631 published
            in the 2019 report.
          all_deaths_canada: Statistics Canada Table 13-10-0708-01, Canada (place of
            residence), total month of death, number of deaths.
            https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310070801
          """)
    return rows

# ------------------------------------------------ 2. sources of suffering
def build_suffering():
    """
    Marginal rates for each reported source of suffering, by year.

    IMPORTANT: the MAID monitoring regulations changed on 1 January 2023 and the
    reporting form's answer options changed with them. Health Canada states that
    "data collected in 2023 are not fully comparable with the data collected in
    previous years". The clearest artefacts: "loss of independence" and "emotional
    distress" were residual free-text categories before 2023 (1.7-5.6%) and became
    listed options afterwards (38-75%). Trends must not be read across 2022/2023.
    """
    pre = {  # single overall rate; no track split published before 2023
        2019: "2019__chart-6-1.csv",
        2020: "2020__this-bar-chart-indicates-the-different-reasons-that-prompted-"
              "patients-requests-f.csv",
        2021: "2021__chart-4-3-text-equivalent.csv",
        2022: "2022__chart-4-3-text-equivalent.csv",
    }
    post = {2023: "2023__figure-3-6a-text-description.csv",
            2024: "2024__figure-3-4a.csv"}

    # Map the differing labels onto one vocabulary.
    canon = [
        ("meaningful_activities", r"meaningful"),
        ("activities_daily_living", r"activities of daily living"),
        ("independence", r"independence|autonomy"),
        ("dignity", r"dignity"),
        ("emotional_existential", r"emotional distress|existential"),
        ("pain_control", r"pain control|control of pain"),
        ("other_symptom_control", r"other symptoms|symptoms other than pain"),
        ("perceived_burden", r"burden"),
        ("isolation_loneliness", r"isolation|loneliness"),
        ("bodily_functions", r"bodily functions"),
        ("quality_of_life", r"quality of life"),
        ("other", r"^other$"),
    ]
    def key_for(label):
        lab = label.strip().lower()
        for k, pat in canon:
            if re.search(pat, lab):
                return k
        return None

    rows = []
    for y, fn in sorted(pre.items()):
        for r in read_table(f"{CLEAN}/tables/{fn}")[1:]:
            k = key_for(r[0])
            if k:
                rows.append([y, k, r[0], num(r[1].rstrip("%")), None, "all",
                             "pre-2023 form", HC.format(y=y)])
    for y, fn in sorted(post.items()):
        for r in read_table(f"{CLEAN}/tables/{fn}")[1:]:
            k = key_for(r[0])
            if k:
                rows.append([y, k, r[0], num(r[1]), num(r[2]), "by_track",
                             "2023+ form", HC.format(y=y)])
    write("suffering_by_year.csv",
          ["year", "measure", "published_label", "track_1_or_all_pct", "track_2_pct",
           "breakdown", "form_version", "source"],
          rows, comment=build_suffering.__doc__)
    return rows

# ------------------------------------------------------- 3. Quebec prognosis
QC_ORDER = ["le_1wk", "le_2wk", "le_1mo", "le_3mo", "le_6mo", "le_1yr", "le_2yr",
            "eol_unspecified", "gt_1yr_not_eol", "gt_1yr_eol_judged"]
# Upper bound in days for each bounded bucket.
QC_UPPER = {"le_1wk": 7, "le_2wk": 14, "le_1mo": 30, "le_3mo": 91,
            "le_6mo": 182, "le_1yr": 365, "le_2yr": 730}

def build_quebec():
    """
    Derived cumulative shares from the Quebec prognosis series.

    The two unspecified buckets are handled explicitly rather than dropped:
      eol_unspecified  - the Commission's own footnote describes these as prognoses
                         given as "a few days to a few months", or qualitative
                         ("sombre", "reserve"). Allocated to <= 6 months.
      gt_1yr_not_eol   - ">1 year", ">18 months", ">=2 years", or unspecified where
                         the provider judged the person NOT to be at end of life.
                         Allocated to > 2 years.
      gt_1yr_eol_judged- 2018-19 and 2019-20 only. Reported as ">1 year" but
                         footnoted that the Commission judged the person WAS at end
                         of life. Allocated to > 1 year (n=3 and n=2; immaterial).
    Both allocations are stated on the page. The alternative (excluding them)
    changes the > 6 month share in 2024-25 from 21.8% to 15.4%.
    """
    src = [r for r in csv.DictReader(
        l for l in open(f"data/source/quebec_prognosis_by_year.csv") if not l.startswith("#"))]
    rows = []
    for r in src:
        g = lambda k: int(r[k]) if r[k] else 0
        total = int(r["total"])
        le6 = sum(g(k) for k in ["le_1wk", "le_2wk", "le_1mo", "le_3mo", "le_6mo"]) \
              + g("eol_unspecified")
        le12 = le6 + g("le_1yr")
        le24 = le12 + g("le_2yr") + g("gt_1yr_eol_judged")
        rows.append([
            r["period"], total,
            g("le_1wk") + g("le_2wk"), sum(g(k) for k in ["le_1wk", "le_2wk", "le_1mo"]),
            sum(g(k) for k in ["le_1wk", "le_2wk", "le_1mo", "le_3mo"]),
            le6, le12, le24,
            round(100 * (total - le6) / total, 2),
            round(100 * (total - le12) / total, 2),
            round(100 * (total - le24) / total, 2),
            round(100 * g("gt_1yr_not_eol") / total, 2),
        ])
    write("quebec_prognosis_derived.csv",
          ["period", "total", "n_le_2wk", "n_le_1mo", "n_le_3mo", "n_le_6mo",
           "n_le_1yr", "n_le_2yr", "pct_gt_6mo", "pct_gt_1yr", "pct_gt_2yr",
           "pct_not_end_of_life"],
          rows, comment=build_quebec.__doc__)
    return rows

# -------------------------------------------------------- 4. track profile
def build_track_profile():
    out = []
    def add(metric, t1, t2, unit, source):
        out.append([metric, t1, t2, unit, source])
    v = read_table(f"{CLEAN}/tables/2024__figure-2-2a.csv")[-1]
    add("provisions_2024", num(v[1]), num(v[2]), "count", "HC 2024 Fig 2.2a")
    o = {r[0]: r for r in read_table(
        f"{CLEAN}/tables/2024__table-2-1a-maid-requests-by-outcome-and-track.csv")}
    for label, key in [("requests_deemed_ineligible", "Requests where individual was deemed ineligible in 2024"),
                       ("requesters_died_of_another_cause", "Requests where individual died of another cause in 2024"),
                       ("requests_withdrawn", "Requests that were withdrawn in 2024"),
                       ("total_requests", "Total")]:
        r = o[key]
        add(label, num(r[2]), num(r[4]), "count", "HC 2024 Table 2.1a")
    for r in read_table(f"{CLEAN}/tables/2024__figure-3-2a.csv")[1:]:
        add(f"condition_duration::{r[0]}", num(r[1]), num(r[2]), "pct", "HC 2024 Fig 3.2a")
    for r in read_table(f"{CLEAN}/tables/2024__figure-3-3a.csv")[1:]:
        add(f"decline::{r[0]}", num(r[1]), num(r[2]), "pct", "HC 2024 Fig 3.3a")
    for r in read_table(f"{CLEAN}/tables/2024__figure-3-4b.csv")[1:]:
        add(f"n_suffering_sources::{r[0]}", num(r[1]), num(r[2]), "pct", "HC 2024 Fig 3.4b")
    for r in read_table(f"{CLEAN}/tables/2024__figure-2-2b.csv")[1:]:
        add(f"age_group::{r[0]}", num(r[1]), num(r[2]), "pct", "HC 2024 Fig 2.2b")
    s = read_table(f"{CLEAN}/tables/2024__figure-2-2c.csv")
    add("sex::Female", num(s[2][1]), num(s[2][2]), "pct", "HC 2024 Fig 2.2c")
    write("track_profile_2024.csv",
          ["metric", "track_1", "track_2", "unit", "source"], out,
          comment=f"Track 1 vs Track 2 profile, 2024 data. All rows from "
                  f"{HC.format(y=2024)}. '::' separates a metric family from its level.")
    return out

if __name__ == "__main__":
    print("building clean datasets:")
    build_volume(); build_suffering(); build_quebec(); build_track_profile()
