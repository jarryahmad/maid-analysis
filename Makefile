# MAID analysis — full pipeline, from public sources to the published page.
#
#   make all      fetch sources, extract tables, build datasets, build the site
#   make site     rebuild only the page (uses the CSVs already in data/clean)
#   make fetch    re-download every source document
#   make verify   re-check derived figures against the published totals
#   make serve    preview at http://localhost:8000
#   make clean    remove generated files (raw downloads are kept)

PY := .venv/bin/python
YEARS := 2019 2020 2021 2022 2023 2024
HC_URL := https://www.canada.ca/en/health-canada/services/publications/health-system-services/annual-report-medical-assistance-dying
CSFV := https://csfv.gouv.qc.ca/fileadmin/docs/rapports_annuels
CSFV_5Y := https://csfv.gouv.qc.ca/fileadmin/docs/rapports_sfv/csfv_rapport_2018-2023.pdf
PBO := https://distribution-a617274656661637473.pbo-dpb.ca/241708b353e7782a9e5e713c2e281fc5ed932d3d07e9f5dd212e73604762bbc5
QC_REPORTS := csfv_rapport_activites_2024-2025 csfv_rapport_activites_2023-2024 \
              rapport_annuel_dactivites_2022-2023 csfv_rapport_activites_2021-2022 \
              csfv_rapport_activites_2020-2021 csfv_rapport_activites_2019-2020 \
              csfv_rapport_activites_2018-2019 csfv_rapport_activites_2017-2018 \
              csfv_rapport_activites_2016-2017 csfv_rapport_activites_2015-2016

.PHONY: all venv fetch extract data site verify serve clean

all: venv fetch extract data site verify

venv:
	@test -d .venv || python3 -m venv .venv
	@$(PY) -m pip install --quiet --disable-pip-version-check \
		beautifulsoup4 lxml pypdf cryptography

fetch:
	@mkdir -p data/raw/lit data/raw/statcan
	@echo "→ Health Canada annual reports"
	@for y in $(YEARS); do \
		curl -sSL --max-time 90 -o data/raw/hc-annual-$$y.html "$(HC_URL)-$$y.html"; done
	@echo "→ Quebec Commission sur les soins de fin de vie"
	@for f in $(QC_REPORTS); do \
		curl -sSL --max-time 120 -A "Mozilla/5.0" -o data/raw/lit/$$f.pdf "$(CSFV)/$$f.pdf"; done
	@curl -sSL --max-time 180 -A "Mozilla/5.0" -o data/raw/lit/csfv_rapport_2018-2023.pdf "$(CSFV_5Y)"
	@echo "→ Parliamentary Budget Officer, Bill C-7 cost estimate"
	@curl -sSL --max-time 120 -A "Mozilla/5.0" -o data/raw/lit/pbo-c7-2020.pdf "$(PBO)"
	@echo "→ Statistics Canada 13-10-0708-01 (deaths by year)"
	@curl -sSL --max-time 180 -A "Mozilla/5.0" -o data/raw/statcan/13100708.zip \
		"https://www150.statcan.gc.ca/n1/tbl/csv/13100708-eng.zip"
	@mkdir -p data/raw/statcan/13100708 && unzip -oq data/raw/statcan/13100708.zip \
		-d data/raw/statcan/13100708
	@echo "fetch complete"

extract:
	$(PY) analysis/01_extract_tables.py
	$(PY) analysis/02_extract_text.py

data:
	$(PY) analysis/03_build_datasets.py
	$(PY) analysis/05_key_numbers.py

site:
	$(PY) analysis/06_build_site.py

verify:
	$(PY) analysis/07_verify.py

serve: site
	@echo "http://localhost:8000"
	@cd site && python3 -m http.server 8000

clean:
	rm -rf data/clean/tables data/clean/*.csv data/clean/*.json site/index.html
	@echo "cleaned (raw downloads kept; run 'make fetch' to refresh them)"
