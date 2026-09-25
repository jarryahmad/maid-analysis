"""
Compute every derived number quoted in the prose, so nothing on the page is
typed by hand. Prints a JSON blob consumed by the site builder.
"""
import csv, json, sys
sys.path.insert(0, "analysis")

def load(name):
    with open(name if name.startswith("data/") else f"data/clean/{name}", encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))

qc  = load("data/source/quebec_prognosis_by_year.csv")
vol = load("maid_by_year.csv")
prof = {r["metric"]: r for r in load("track_profile_2024.csv")}

g = lambda r, k: int(r[k]) if r[k] else 0
first, last = qc[0], qc[-1]

def bands(r):
    tot = int(r["total"])
    le6 = sum(g(r, k) for k in ["le_1wk","le_2wk","le_1mo","le_3mo","le_6mo","eol_unspecified"])
    le12 = le6 + g(r, "le_1yr")
    return tot, le6, le12

# --- Quebec, all MAID ------------------------------------------------------
tot_l, le6_l, le12_l = bands(last)
tot_f, le6_f, le12_f = bands(first)

# --- Quebec, excluding the "not at end of life" bucket (Track-1 analogue) --
ne = g(last, "gt_1yr_not_eol")
base_eol = tot_l - ne
le6_eol  = le6_l
le12_eol = le12_l

K = {
  "qc_last_period": last["period"], "qc_first_period": first["period"],
  "qc_last_n": tot_l, "qc_first_n": tot_f,
  "qc_gt6_last_pct": round(100*(tot_l-le6_l)/tot_l, 1),
  "qc_gt6_first_pct": round(100*(tot_f-le6_f)/tot_f, 1),
  "qc_gt12_last_pct": round(100*(tot_l-le12_l)/tot_l, 1),
  "qc_gt12_first_pct": round(100*(tot_f-le12_f)/tot_f, 1),
  "qc_gt6_last_n": tot_l-le6_l, "qc_gt6_first_n": tot_f-le6_f,
  "qc_gt12_last_n": tot_l-le12_l, "qc_gt12_first_n": tot_f-le12_f,
  "qc_le3_last_pct": round(100*sum(g(last,k) for k in
      ["le_1wk","le_2wk","le_1mo","le_3mo"])/tot_l, 1),
  "qc_le1mo_last_pct": round(100*sum(g(last,k) for k in
      ["le_1wk","le_2wk","le_1mo"])/tot_l, 1),
  "qc_noteol_last_pct": round(100*ne/tot_l, 1), "qc_noteol_last_n": ne,
  # Track-1 analogue: exclude the not-at-end-of-life bucket entirely
  "eol_base": base_eol,
  # 2018-19 had no "not at end of life" category at all, so the whole cohort is
  # the end-of-life population and the two rates coincide.
  "eol_gt6_first_pct": round(100*(tot_f-le6_f)/tot_f, 1),
  "share_of_gt6_judged_eol": round(100*((tot_l-le6_l)-ne)/(tot_l-le6_l)),
  "eol_gt6_pct": round(100*(base_eol-le6_eol)/base_eol, 1),
  "eol_gt12_pct": round(100*(base_eol-le12_eol)/base_eol, 1),
}

# --- National projection ---------------------------------------------------
v24 = vol[-1]
t1, t2, tot24 = int(v24["track_1"]), int(v24["track_2"]), int(v24["total_provisions"])
K.update({
  "t1": t1, "t2": t2, "tot24": tot24,
  "all_deaths_24": int(v24["all_deaths_canada"]),
  "maid_share_24": float(v24["maid_pct_of_all_deaths"]),
  "proj_t1_gt6": round(t1 * K["eol_gt6_pct"]/100),
  "proj_t1_gt12": round(t1 * K["eol_gt12_pct"]/100),
})
K["proj_gt6_total"] = K["proj_t1_gt6"] + t2
K["proj_gt12_total"] = K["proj_t1_gt12"] + t2
K["proj_gt6_pct_of_maid"] = round(100*K["proj_gt6_total"]/tot24, 1)
K["proj_gt12_pct_of_maid"] = round(100*K["proj_gt12_total"]/tot24, 1)
K["proj_gt6_pct_of_deaths"] = round(100*K["proj_gt6_total"]/K["all_deaths_24"], 2)
K["proj_gt12_pct_of_deaths"] = round(100*K["proj_gt12_total"]/K["all_deaths_24"], 2)

# --- Health Canada's own published share of deaths -------------------------
# Read from the report text rather than recomputed, because Health Canada uses a
# provisional deaths denominator that Statistics Canada later revises.
_hc = open("data/raw/hc-annual-2024.txt", encoding="utf-8").read()
_m = __import__("re").search(r"In 2024, ([\d.]+)% of people in Canada who died received MAID", _hc)
assert _m, "Health Canada's published MAID share not found in the report text"
K["hc_published_share_24"] = float(_m.group(1))

# --- Requests that ended in natural death, by track (Table 2.1a) -----------
died = prof["requesters_died_of_another_cause"]
treq = prof["total_requests"]
K["t1_died_natural"] = int(float(died["track_1"]))
K["t2_died_natural"] = int(float(died["track_2"]))
K["t1_requests"] = int(float(treq["track_1"]))
K["t2_requests"] = int(float(treq["track_2"]))
K["t1_died_natural_pct"] = round(100*K["t1_died_natural"]/K["t1_requests"], 1)
K["t2_died_natural_pct"] = round(100*K["t2_died_natural"]/K["t2_requests"], 1)
K["t1_ineligible"] = int(float(prof["requests_deemed_ineligible"]["track_1"]))
K["t2_ineligible"] = int(float(prof["requests_deemed_ineligible"]["track_2"]))
K["t1_inelig_pct"] = round(100*K["t1_ineligible"]/K["t1_requests"], 1)
K["t2_inelig_pct"] = round(100*K["t2_ineligible"]/K["t2_requests"], 1)

# --- Track 1 vs Track 2 comparison table -----------------------------------
def _p(metric, col):
    return float(prof[metric][col])

K["t1_female"] = _p("sex::Female", "track_1")
K["t2_female"] = _p("sex::Female", "track_2")
# Lived with the condition for more than 10 years = the 10-20 and 20+ bands.
K["t1_cond_gt10"] = round(_p("condition_duration::10 years to less than 20 years", "track_1")
                          + _p("condition_duration::20 years or more", "track_1"), 1)
K["t2_cond_gt10"] = round(_p("condition_duration::10 years to less than 20 years", "track_2")
                          + _p("condition_duration::20 years or more", "track_2"), 1)
K["t1_cond_lt1"] = _p("condition_duration::Less than 1 year", "track_1")
K["t2_cond_lt1"] = _p("condition_duration::Less than 1 year", "track_2")
K["t1_adl"] = _p("decline::Unable to do most or all activities of daily living (ADLs) "
                 "and/or instrumental activities of daily living (IADLs) or marked "
                 "decrease in ability to do these activities", "track_1")

# --- Cumulative provisions since 2016 --------------------------------------
K["cumulative"] = sum(int(r["total_provisions"]) for r in vol)

if __name__ == "__main__":
    json.dump(K, open("data/clean/key_numbers.json", "w"), indent=2)
    for k, v in K.items():
        print(f"  {k:26} {v}")
