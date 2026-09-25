# MAID in Canada: the timeline question

A data analysis of Canada's Medical Assistance in Dying programme, built from primary
sources and published as a static page.

**The question.** Everyone dies eventually, so "MAID adds deaths" only means something
against a time window: how many recipients would still have been alive six months
later? Federal reporting records whether death was "reasonably foreseeable", which is a
legal test rather than a duration, so it cannot answer that. Quebec's can. A
physician-estimated prognosis is recorded for every MAID death, and the Commission sur
les soins de fin de vie publishes the distribution each year.

**What the series shows.** Assembling it for the first time, the share of Quebec MAID
recipients with an estimated prognosis longer than six months went from **3.8% in
2018-19 to 21.8% in 2024-25**. Longer than a year: 0.2% to 10.2%. 68% of that
beyond-six-months group were still judged to be at end of life, so the shift is not
only the Track 2 cohort created by Bill C-7. The Parliamentary Budget Officer's 2020
costing, still the source of the "weeks, not months" figure, was built on the 2018-19
version of this same Quebec data.

## What is in here

```
data/raw/        source documents exactly as downloaded (HTML, PDF, StatCan CSV)
data/source/     the one hand-transcribed table, provenance in the file header
data/clean/      every table parsed out of those documents, plus derived datasets
analysis/        the pipeline: scrape -> extract -> build -> render -> verify
notes/           the original brief, kept for provenance
site/            the generated page, the only thing published
```

## Running it

```sh
make all        # fetch sources, extract, build datasets, render, verify
make site       # re-render the page from the CSVs already present
make verify     # re-check every figure against its source document
make serve      # preview at localhost:8000
```

`make all` re-downloads from canada.ca, csfv.gouv.qc.ca, pbo-dpb.ca and statcan.gc.ca,
so it needs network access. Everything else runs offline from the committed raw files.

## How the numbers are guarded

No figure on the page is typed by hand. Prose and charts both generate from the CSVs in
`data/clean/`, which are parsed out of `data/raw/`.

The exception is `data/source/quebec_prognosis_by_year.csv`. Quebec publishes that table
inside PDFs whose layout does not parse reliably, so it was transcribed. `make verify`
checks it the hard way: every count must appear inside the "Pronostic vital" block of
the extracted text of the PDF it claims to come from, and every row must sum to its
published total. It also re-checks the Health Canada series against the scraped figure
tables and confirms each directly quoted sentence appears verbatim in its source. 97
checks in total, and the deploy workflow runs them, so a drifted figure fails the build
instead of shipping.

Two judgment calls are stated with their sensitivity rather than buried, on the page and
in the CSV headers:

1. Quebec's unspecified `"fin de vie"` bucket is allocated to 6 months or less, per the
   Commission's footnote describing it as "a few days to a few months". Excluding it
   instead moves the 2024-25 beyond-six-months share from 21.8% to 15.4%.
2. The `"more than a year / not at end of life"` bucket is allocated to over 2 years.

## Sources

| Source | Used for |
|---|---|
| [Health Canada, Sixth Annual Report on MAID (2024 data)](https://www.canada.ca/en/health-canada/services/publications/health-system-services/annual-report-medical-assistance-dying-2024.html) | Provisions by track, request outcomes, suffering, decline indicators, condition duration |
| Health Canada annual reports, 2019 to 2023 data years | Trend series |
| [Commission sur les soins de fin de vie (Quebec), annual reports 2018-19 to 2024-25](https://csfv.gouv.qc.ca/en/publications) | The prognosis series (French) |
| [Commission sur les soins de fin de vie, five-year report 2018-2023](https://csfv.gouv.qc.ca/fileadmin/docs/rapports_sfv/csfv_rapport_2018-2023.pdf) | Year-over-year prognosis narrative |
| [Statistics Canada, Table 13-10-0708-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310070801) | Total deaths in Canada by year |
| [Parliamentary Budget Officer, *Cost Estimate for Bill C-7* (2020)](https://www.pbo-dpb.ca/en/publications/RP-2021-025-M--cost-estimate-bill-c-7-medical-assistance-in-dying--estimation-couts-projet-loi-c-7-aide-medicale-mourir) | The official life-shortening assumptions |
| [Trachtenberg & Manns, CMAJ 2017;189:E101](https://www.cmaj.ca/content/189/3/E101) | Pre-legalization cost-model assumptions |
| [White et al., PLoS ONE 2016;11(8):e0161407](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0161407) | Accuracy of clinician survival predictions |

## Deploying

Push to `main`. `.github/workflows/pages.yml` rebuilds, verifies and publishes `site/`
to GitHub Pages. Enable Pages once under **Settings > Pages > Source: GitHub Actions**.

The repo URL the page links to lives in `analysis/06_build_site.py` (`REPO`). If the
repo is renamed or moved, update it there and re-run `make site`.

While the repo is private, Pages will not build on a free plan. Make it public to
publish.

## Nuances

This analysis cannot tell you whether any individual death was premature, whether burden
or loneliness caused a request, or what Track 2 recipients would actually have lived.
Those limits are stated on the page. The joint distribution of suffering sources would
need the microdata held in
[Statistics Canada Research Data Centres](https://crdcn.ca/data/medical-assistance-in-dying/).

Written by [@jahmad93](https://x.com/jahmad93). The extraction pipeline, calculations
and charts were built with Claude and are in the repo.

## Licence

Code and prose: MIT (see `LICENSE`). The underlying data belongs to Health Canada, the
Government of Quebec and Statistics Canada, and is reproduced here under their open-data
terms.
