"""
Extract every HTML table from the Health Canada MAID annual reports (data years
2019-2024) into CSVs, with a manifest recording provenance for each one.

Source pages (one per data year):
  https://www.canada.ca/en/health-canada/services/publications/health-system-services/
    annual-report-medical-assistance-dying-<YEAR>.html

Figures in these reports are images; each has an adjacent "Text description"
<details> block containing the underlying table. Those are the tables we want.
"""
import csv, json, os, re, sys
from bs4 import BeautifulSoup

YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
RAW = "data/raw"
OUT = "data/clean/tables"
URL = ("https://www.canada.ca/en/health-canada/services/publications/"
       "health-system-services/annual-report-medical-assistance-dying-{y}.html")

def slug(s):
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]

def table_label(t):
    cap = t.find("caption")
    if cap:
        return cap.get_text(" ", strip=True)
    prev = t.find_previous(["summary", "figcaption", "h2", "h3", "h4"])
    if prev:
        return prev.get_text(" ", strip=True)
    return "untitled"

def cell_text(td):
    # Strip footnote reference links (e.g. "Footnote 1") that Canada.ca appends.
    for sup in td.find_all("sup"):
        sup.decompose()
    txt = td.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", txt).strip()

def extract(t):
    rows = []
    for tr in t.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        row = []
        for c in cells:
            txt = cell_text(c)
            span = int(c.get("colspan", 1) or 1)
            row.append(txt)
            row.extend([""] * (span - 1))
        rows.append(row)
    if not rows:
        return []
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]

def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for y in YEARS:
        path = f"{RAW}/hc-annual-{y}.html"
        soup = BeautifulSoup(open(path, encoding="utf-8").read(), "lxml")
        seen = {}
        for t in soup.find_all("table"):
            label = table_label(t)
            rows = extract(t)
            if len(rows) < 2:
                continue
            base = slug(label.replace("- Text description", ""))
            seen[base] = seen.get(base, 0) + 1
            name = base if seen[base] == 1 else f"{base}-{seen[base]}"
            fn = f"{y}__{name}.csv"
            with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            manifest.append({
                "data_year": y,
                "label": label,
                "file": f"data/clean/tables/{fn}",
                "source_url": URL.format(y=y),
                "n_rows": len(rows) - 1,
                "n_cols": len(rows[0]),
            })
    with open("data/clean/tables_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"extracted {len(manifest)} tables across {len(YEARS)} reports")
    for y in YEARS:
        print(f"  {y}: {sum(1 for m in manifest if m['data_year']==y)}")

if __name__ == "__main__":
    main()
