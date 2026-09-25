"""Chart builders. Each returns (svg_html, table_html)."""
import csv, re, sys
sys.path.insert(0, "analysis")
from svgkit import Chart, table, fmt, ORDINAL, S1, S2, INK2, MUTED

CLEAN = "data/clean"


def load(name):
    path = name if name.startswith("data/") else f"{CLEAN}/{name}"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def n(v):
    return None if v in (None, "", "NA") else float(v)


def i(v):
    x = n(v)
    return None if x is None else int(x)


# ----------------------------------------------------------- 1. volume
def chart_volume():
    rows = load("maid_by_year.csv")
    vmax = 18000
    c = Chart(760, 380, pad=(24, 20, 44, 58))
    c.legend = [("Track 1, death reasonably foreseeable", S1),
                ("Track 2, death not reasonably foreseeable", S2)]
    c.grid_y([0, 4000, 8000, 12000, 16000], vmax, fmt_fn=lambda v: f"{v/1000:g}k",
             label="MAID provisions")
    for idx, r in enumerate(rows):
        x, bw = c.band(idx, len(rows))
        t1, t2, tot = i(r["track_1"]), i(r["track_2"]), i(r["total_provisions"])
        y_top = c.y(tot, vmax)
        if t2:
            h2 = (c.y(0, vmax) - c.y(t2, vmax))
            c.seg(x, y_top, bw, h2 - 1, ORDINAL[0] if False else S2,
                  f"{r['year']}: Track 2 = {fmt(t2)}")
            base = y_top + h2 + 1          # 2px surface gap between stacked fills
            h1 = c.y1 - base
            c.rect(x, base, bw, h1, S1, f"{r['year']}: Track 1 = {fmt(t1)}", flat_bottom=True)
        else:
            lab = ("all provisions (Track 2 did not exist)" if not t1
                   else "Track 1 (no Track 2 provisions)")
            c.rect(x, y_top, bw, c.y1 - y_top, S1, f"{r['year']}: {fmt(tot)} - {lab}")
        c.label(x + bw / 2, y_top - 7, fmt(tot))
    c.x_labels([r["year"] for r in rows])
    tbl = table(["Year", "Track 1", "Track 2", "Total", "All deaths in Canada", "MAID % of deaths"],
                [[r["year"], fmt(i(r["track_1"])), fmt(i(r["track_2"])),
                  fmt(i(r["total_provisions"])), fmt(i(r["all_deaths_canada"])),
                  fmt(n(r["maid_pct_of_all_deaths"]), 2, pct=True)] for r in rows])
    return c.render("MAID provisions in Canada by year and track, 2016 to 2024"), tbl


def chart_share():
    rows = load("maid_by_year.csv")
    vmax = 6
    c = Chart(760, 260, pad=(24, 24, 44, 58))
    c.grid_y([0, 1, 2, 3, 4, 5, 6], vmax, fmt_fn=lambda v: f"{v:g}%",
             label="% of all registered deaths")
    pts = []
    for idx, r in enumerate(rows):
        cx = c.x0 + (idx + 0.5) * c.iw / len(rows)
        v = n(r["maid_pct_of_all_deaths"])
        pts.append((cx, c.y(v, vmax)))
    c.line(pts, S1, 2)
    for idx, r in enumerate(rows):
        v = n(r["maid_pct_of_all_deaths"])
        c.dot(*pts[idx], S1, f"{r['year']}: {v:.2f}% of all deaths "
                             f"({fmt(i(r['total_provisions']))} of {fmt(i(r['all_deaths_canada']))})")
    c.label(pts[-1][0], pts[-1][1] - 14, f"{n(rows[-1]['maid_pct_of_all_deaths']):.1f}%", anchor="end")
    c.x_labels([r["year"] for r in rows])
    return c.render("MAID as a percentage of all deaths in Canada, 2016 to 2024"), ""


def chart_growth():
    years = ["2022", "2023", "2024"]
    total = [31.1, 16.9, 6.9]
    track2 = [109.4, 33.3, 17.1]
    vmax = 120
    c = Chart(560, 300, pad=(24, 20, 44, 52))
    c.legend = [("All MAID provisions", S1), ("Track 2 only", S2)]
    c.grid_y([0, 30, 60, 90, 120], vmax, fmt_fn=lambda v: f"{v:g}%",
             label="Year-over-year growth")
    for idx, y in enumerate(years):
        x, bw = c.band(idx, len(years), pad_frac=0.34)
        half = (bw - 2) / 2                     # 2px surface gap between adjacent bars
        for k, (vals, col) in enumerate([(total, S1), (track2, S2)]):
            v = vals[idx]
            yy = c.y(v, vmax)
            bx = x + k * (half + 2)
            c.rect(bx, yy, half, c.y1 - yy, col, f"{y}: {v:g}% growth")
            c.label(bx + half / 2, yy - 7, f"{v:g}%")
    c.x_labels(years)
    tbl = table(["Year", "All MAID growth", "Track 2 growth"],
                [[years[k], f"{total[k]:g}%", f"{track2[k]:g}%"] for k in range(3)],
                "Track 2 growth for 2022 is measured off a 224-case base (2021), its first "
                "full year; earlier rates are not meaningful.")
    return c.render("Year-over-year growth in MAID provisions, total and Track 2"), tbl


# -------------------------------------------------- 2. Quebec prognosis
QC_BANDS = [
    ("1 month or less", ["le_1wk", "le_2wk", "le_1mo"], ORDINAL[0]),
    ("1-3 months", ["le_3mo"], ORDINAL[1]),
    ("3-6 months*", ["le_6mo", "eol_unspecified"], ORDINAL[2]),
    ("6-12 months", ["le_1yr"], ORDINAL[3]),
    ("More than 12 months†", ["le_2yr", "gt_1yr_not_eol", "gt_1yr_eol_judged"], ORDINAL[4]),
]


def qc_banded():
    out = []
    for r in load("data/source/quebec_prognosis_by_year.csv"):
        tot = int(r["total"])
        vals = [sum(int(r[k]) if r[k] else 0 for k in keys) for _, keys, _ in QC_BANDS]
        out.append((r["period"], tot, vals))
    return out


def chart_qc_stack():
    data = qc_banded()
    c = Chart(760, 418, pad=(46, 20, 44, 46))
    c.legend = [(lab, col) for lab, _, col in QC_BANDS]
    c.grid_y([0, 25, 50, 75, 100], 100, fmt_fn=lambda v: f"{v:g}%")
    c.add(f'<text x="{c.x0}" y="{c.y0 - 30}" class="axis-label">'
          f'Share of all MAID deaths in Quebec &#183; label above each bar is the '
          f'share with more than 6 months</text>')
    for idx, (period, tot, vals) in enumerate(data):
        x, bw = c.band(idx, len(data), pad_frac=0.22)
        acc = 0.0
        for k, (lab, _, col) in enumerate(QC_BANDS):
            pct = 100 * vals[k] / tot
            ytop = c.y(acc + pct, 100)
            h = (c.y(acc, 100) - ytop) - (2 if k < len(QC_BANDS) - 1 else 0)
            c.seg(x, ytop, bw, h, col,
                  f"{period} · {lab}: {pct:.1f}% ({vals[k]:,} of {tot:,})")
            acc += pct
        gt6 = 100 * (vals[3] + vals[4]) / tot
        c.label(x + bw / 2, c.y(100, 100) - 9, f"{gt6:.0f}%", cls="datalabel strong")
    c.x_labels([p for p, _, _ in data], rotate=0)
    rows = []
    for period, tot, vals in data:
        rows.append([period, f"{tot:,}"] + [f"{v:,} ({100*v/tot:.1f}%)" for v in vals])
    tbl = table(["Quebec year", "MAID deaths"] + [b[0] for b in QC_BANDS], rows)
    return c.render("Composition of physician-estimated prognosis among Quebec MAID "
                    "recipients, 2018-19 to 2024-25"), tbl


def chart_qc_trend():
    rows = load("quebec_prognosis_derived.csv")
    vmax = 25
    c = Chart(760, 320, pad=(28, 30, 44, 52))
    c.legend = [("Prognosis longer than 6 months", S1),
                ("Prognosis longer than 12 months", S2)]
    c.grid_y([0, 5, 10, 15, 20, 25], vmax, fmt_fn=lambda v: f"{v:g}%",
             label="Share of Quebec MAID recipients")
    for key, col in [("pct_gt_6mo", S1), ("pct_gt_1yr", S2)]:
        pts = [(c.x0 + (k + 0.5) * c.iw / len(rows), c.y(float(r[key]), vmax))
               for k, r in enumerate(rows)]
        c.line(pts, col, 2)
        for k, r in enumerate(rows):
            c.dot(*pts[k], col, f"{r['period']}: {float(r[key]):.1f}% "
                                f"({'>6 months' if key=='pct_gt_6mo' else '>12 months'})")
        c.label(pts[-1][0] - 4, pts[-1][1] - 12, f"{float(rows[-1][key]):.1f}%", anchor="end")
    c.x_labels([r["period"] for r in rows])
    tbl = table(["Quebec year", "MAID deaths", "> 6 months", "> 12 months", "Not at end of life"],
                [[r["period"], f"{int(r['total']):,}", f"{float(r['pct_gt_6mo']):.1f}%",
                  f"{float(r['pct_gt_1yr']):.1f}%", f"{float(r['pct_not_end_of_life']):.1f}%"]
                 for r in rows])
    return c.render("Share of Quebec MAID recipients with an estimated prognosis longer "
                    "than 6 and 12 months, 2018-19 to 2024-25"), tbl


def chart_qc_cdf():
    """Cumulative share who, on the physician's estimate, had at most t left."""
    r = load("data/source/quebec_prognosis_by_year.csv")[-1]
    g = lambda k: int(r[k]) if r[k] else 0
    tot = int(r["total"])
    steps = [("1 week", g("le_1wk")), ("2 weeks", g("le_2wk")), ("1 month", g("le_1mo")),
             ("3 months", g("le_3mo") ), ("6 months", g("le_6mo") + g("eol_unspecified")),
             ("12 months", g("le_1yr")), ("2 years", g("le_2yr") + g("gt_1yr_eol_judged"))]
    c = Chart(760, 340, pad=(26, 26, 46, 52))
    c.grid_y([0, 25, 50, 75, 100], 100, fmt_fn=lambda v: f"{v:g}%",
             label="Cumulative share estimated to have died by this point anyway")
    acc, rows, pts = 0, [], []
    for k, (lab, v) in enumerate(steps):
        acc += v
        pct = 100 * acc / tot
        x, bw = c.band(k, len(steps), pad_frac=0.3)
        yy = c.y(pct, 100)
        c.rect(x, yy, bw, c.y1 - yy, S1,
               f"By {lab}: {pct:.1f}% ({acc:,} of {tot:,})")
        c.label(x + bw / 2, yy - 7, f"{pct:.0f}%")
        rows.append([lab, f"{v:,}", f"{acc:,}", f"{pct:.1f}%", f"{100-pct:.1f}%"])
        pts.append((x + bw / 2, yy))
    y6 = c.y(100 * sum(v for _, v in steps[:5]) / tot, 100)
    c.x_labels([s[0] for s in steps])
    tbl = table(["Within", "In this band", "Cumulative", "Cumulative %", "Still alive %"], rows,
                "Quebec, 1 April 2024 to 31 March 2025, n = 6,267. The residual 7.0% "
                "(n = 439) whose prognosis was over a year or who were judged not to be "
                "at end of life are excluded from every cumulative band above.")
    return c.render("Cumulative share of Quebec MAID recipients by estimated prognosis, "
                    "2024-25"), tbl


# ------------------------------------------------------- 3. track profile
def profile(prefix):
    rows = load("track_profile_2024.csv")
    return [(r["metric"].split("::", 1)[1], n(r["track_1"]), n(r["track_2"]))
            for r in rows if r["metric"].startswith(prefix + "::")]


def wrap_label(text, width=34, lines=2):
    """Greedy wrap onto at most `lines` lines. A "/" is a break opportunity, so
    slash-joined labels like "anxiety/fear/existential" can wrap. Ellipsis only
    if the label genuinely will not fit; the full text stays in the tooltip and
    in the table view."""
    words = re.findall(r"\S+?/|\S+", text)
    out, cur, used = [], "", 0
    for w in words:
        sep = "" if cur.endswith("/") else (" " if cur else "")
        trial = cur + sep + w
        if len(trial) <= width or not cur:
            cur = trial
            used += 1
        else:
            out.append(cur)
            if len(out) == lines:
                cur = ""
                break
            cur = w
            used += 1
    if cur and len(out) < lines:
        out.append(cur)
    if used < len(words):
        out[-1] = out[-1].rstrip(" ,/") + "\u2026"
    return out


def hbar(items, width=760, row_h=44, label_w=286, vmax=100, note=None, wrap=34):
    c = Chart(width, 34 + row_h * len(items), pad=(26, 46, 8, label_w))
    c.legend = [("Track 1", S1), ("Track 2", S2)]
    for t in [0, 25, 50, 75, 100]:
        x = c.x0 + t / vmax * c.iw
        c.add(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{c.y0}" y2="{c.y0 + row_h*len(items)}" '
              f'stroke="var(--grid)" stroke-width="1"/>')
        c.add(f'<text x="{x:.1f}" y="{c.y0 - 8}" text-anchor="middle" class="tick">{t}%</text>')
    for k, item in enumerate(items):
        lab, v1, v2 = item[0], item[1], item[2]
        full = item[3] if len(item) > 3 else lab
        y = c.y0 + k * row_h + 4
        bh = (row_h - 10) / 2
        ls = wrap_label(lab, wrap)
        top = y + row_h / 2 - 3 - (len(ls) - 1) * 7
        tspans = "".join(
            f'<tspan x="{c.pl - 12}" dy="{0 if k == 0 else 14}">{l}</tspan>'
            for k, l in enumerate(ls))
        c.add(f'<text y="{top:.1f}" text-anchor="end" class="rowlabel">'
              f'<title>{full}</title>{tspans}</text>')
        for j, (v, col) in enumerate([(v1, S1), (v2, S2)]):
            if v is None:
                continue
            w = v / vmax * c.iw
            yy = y + j * (bh + 2)
            c.add(f'<rect x="{c.x0}" y="{yy:.1f}" width="{max(w,0.8):.1f}" height="{bh:.1f}" '
                  f'rx="3" fill="{col}" class="mark" data-tip="{full} - '
                  f'Track {j+1}: {v:g}%"><title>{full} - Track {j+1}: {v:g}%</title></rect>')
            c.add(f'<text x="{c.x0 + w + 6:.1f}" y="{yy + bh - 1:.1f}" class="datalabel sm" '
                  f'text-anchor="start">{v:g}</text>')
    return c.render(note or "")


def chart_suffering():
    rows = load("suffering_by_year.csv")
    d = {r["measure"]: (n(r["track_1_or_all_pct"]), n(r["track_2_pct"]), r["published_label"])
         for r in rows if r["year"] == "2024"}
    order = ["meaningful_activities", "activities_daily_living", "independence", "dignity",
             "emotional_existential", "other_symptom_control", "pain_control",
             "perceived_burden", "bodily_functions", "isolation_loneliness", "other"]
    items = [(d[k][2], d[k][0], d[k][1]) for k in order if k in d]
    tbl = table(["Source of suffering", "Track 1", "Track 2", "Gap"],
                [[lab, f"{a:g}%", f"{b:g}%", f"{b-a:+.1f} pts"] for lab, a, b in items])
    return hbar(items, note="Reported sources of intolerable suffering by track, 2024"), tbl


# Health Canada's Figure 3.3a labels run to 165 characters. These are shortened
# for the chart axis only; the tooltip and the table view carry the published
# wording verbatim.
DECLINE_SHORT = {
    "Unable to do most or all activities of daily living (ADLs) and/or instrumental "
    "activities of daily living (IADLs) or marked decrease in ability to do these "
    "activities": "Unable to do most or all daily activities (ADLs/IADLs)",
    "Significant dependence on aid(s) for interaction and/or mobility, or advanced "
    "beyond use of these aids or marked increase in dependence":
        "Significant dependence on mobility or interaction aids",
    "Persistent significant fatigue/weakness or marked increase":
        "Persistent significant fatigue or weakness",
    "Significant shortness of breath or marked increase":
        "Significant shortness of breath",
}


def chart_decline():
    raw = profile("decline")
    items = [(DECLINE_SHORT.get(lab, lab), a, b, lab) for lab, a, b in raw]
    tbl = table(["Indicator of decline (as published)", "Track 1", "Track 2"],
                [[lab, f"{a:g}%", f"{b:g}%"] for lab, a, b in raw])
    return hbar(items, note="Reported indicators of advanced decline by track, 2024"), tbl


def chart_duration():
    items = profile("condition_duration")
    c = Chart(560, 300, pad=(26, 20, 48, 52))
    c.legend = [("Track 1", S1), ("Track 2", S2)]
    c.grid_y([0, 10, 20, 30, 40, 50], 50, fmt_fn=lambda v: f"{v:g}%",
             label="Share of recipients")
    for k, (lab, v1, v2) in enumerate(items):
        x, bw = c.band(k, len(items), pad_frac=0.3)
        half = (bw - 2) / 2
        for j, (v, col) in enumerate([(v1, S1), (v2, S2)]):
            yy = c.y(v, 50)
            c.rect(x + j * (half + 2), yy, half, c.y1 - yy, col, f"{lab} - Track {j+1}: {v:g}%")
    c.x_labels(["<1 yr", "1-5 yr", "5-10 yr", "10-20 yr", "20+ yr"])
    tbl = table(["Time living with the condition", "Track 1", "Track 2"],
                [[lab, f"{a:g}%", f"{b:g}%"] for lab, a, b in items])
    return c.render("How long recipients had lived with their condition, by track, 2024"), tbl


def chart_nsources():
    items = profile("n_suffering_sources")
    c = Chart(620, 300, pad=(26, 20, 48, 52))
    c.legend = [("Track 1", S1), ("Track 2", S2)]
    c.grid_y([0, 5, 10, 15, 20, 25], 25, fmt_fn=lambda v: f"{v:g}%",
             label="Share of recipients")
    for k, (lab, v1, v2) in enumerate(items):
        x, bw = c.band(k, len(items), pad_frac=0.3)
        half = (bw - 2) / 2
        for j, (v, col) in enumerate([(v1, S1), (v2, S2)]):
            if v is None:
                c.label(x + j * (half + 2) + half / 2, c.y1 - 6, "×", cls="tick")
                continue
            yy = c.y(v, 25)
            c.rect(x + j * (half + 2), yy, half, c.y1 - yy, col,
                   f"{lab} sources - Track {j+1}: {v:g}%")
    c.x_labels([lab for lab, _, _ in items])
    tbl = table(["Number of distinct sources cited", "Track 1", "Track 2"],
                [[lab, f"{a:g}%" if a is not None else "suppressed",
                  f"{b:g}%" if b is not None else "suppressed"] for lab, a, b in items],
                "x marks a value suppressed by Health Canada to meet confidentiality "
                "requirements (fewer than 5 cases).")
    return c.render("Number of distinct sources of suffering cited per recipient, by track, "
                    "2024"), tbl
