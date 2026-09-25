> **This is the original handoff brief, kept for provenance.** It was written from a
> conversation summary, before the primary sources were pulled. Five things in it were
> corrected during verification, and the published page reflects the corrections, not
> this document:
>
> 1. **"4,017 requesters died of another cause."** Both numbers in the brief are real but
>    measure different things: 4,017 is the count of requesters (Table 2.1a); Table 2.3c
>    reports 3,973, the number for whom a *reason* was recorded.
> 2. **"April 2026: CAMH recommends an indefinite delay."** CAMH's statement is dated
>    **17 June 2026** and *supports* the Special Joint Committee's recommendation issued
>    the same day; it did not precede it.
> 3. **Sources-of-suffering trends.** The brief treats the annual series as comparable.
>    It is not: the monitoring regulations changed on 1 January 2023 and Health Canada
>    states that 2023 data "are not fully comparable with the data collected in previous
>    years." "Loss of independence" and "emotional distress" jump from residual
>    free-text categories (1.7–5.6%) to listed options (38–75%) across that break.
> 4. **The counterfactual.** The brief proposes modelling it from the CMAJ 2017 and
>    PBO 2020 assumptions. Quebec in fact *records* a physician-estimated prognosis for
>    every MAID death, which made the model largely unnecessary — and revealed that the
>    PBO's assumption was itself derived from the 2018-19 vintage of that same Quebec
>    source.
> 5. **Bill C-218.** Still at second reading as of 23 September 2026, not further along.

---

# MAID Analysis — Project Brief

Handoff brief for building a data analysis of Canada's Medical Assistance in Dying (MAID) data and publishing it as a static site on GitHub Pages.

## 1. Origin and motivation

A Twitter/X thread about a chart by @cremieuxrecueil, "Pain Isn't the Main Reason Canadians Choose MAID." It plots sources of intolerable suffering reported for 2024 MAID recipients by track, using Health Canada 2025, Figure 3.4a.

- **@webdevMason's claim:** Many of the reasons are culturally mediated. Once "burden on family/caregivers" is accepted as a reason, it becomes a slope toward asking what burdens a person presents.
  - Follow-up: even if burden co-occurs with loss of independence and inability to do daily activities, it's worth asking whether those would still drive requests if the person didn't feel unworthy of help.
- **@jahmad93 (me), point 1:** These reasons are not mutually exclusive. Burden rarely stands alone; it rides along with severe decline.
- **@jahmad93 (me), point 2:** What's the counterfactual? Is MAID adding deaths within, say, 6 months, or slightly accelerating the inevitable? Current concerns seem overblown for most cases.

## 2. Questions the analysis should answer

1. **Co-occurrence:** How often do "self-perceived burden" (and "isolation/loneliness") appear alone vs. alongside other sources of suffering? What does the published data allow us to say about overlap?
2. **Counterfactual time lost:** For Track 1, roughly how much earlier do people die than they otherwise would? How many MAID deaths would plausibly not have occurred within 6 or 12 months?
3. **Track 2 trend and profile:** Is Track 2 growing? Who receives it, and how does its suffering profile differ from Track 1?
4. **Policy context:** Where is the scrutiny, and what is pending (the mental-illness-as-sole-condition expansion)?

The analysis should be even-handed. It should present the strongest version of both the "concern is overblown" and the "concern is warranted" readings, and be explicit about what the data cannot show.

## 3. Primary sources

- **Health Canada, Sixth Annual Report on MAID in Canada (2024 data), published Nov 2025**
  - HTML: https://www.canada.ca/en/health-canada/services/publications/health-system-services/annual-report-medical-assistance-dying-2024.html
  - PDF: https://www.canada.ca/content/dam/hc-sc/documents/services/publications/health-system-services/annual-report-medical-assistance-dying-2024/annual-report-medical-assistance-dying-2024.pdf
  - Key sections:
    - 2.2: provisions over time (Figure 2.2a)
    - 2.3: requests not resulting in MAID (Table 2.3c)
    - 3.3: decline indicators (Figure 3.3a)
    - 3.4: nature of suffering (Figures 3.4a and 3.4b, plus the burden and loneliness subsections)
    - 4.4: disability
    - 5.3: living arrangement
  - HTML figures have "Text description" tables; scrape those rather than images.
- **Earlier annual reports (2019–2023):** the same URL pattern with the year changed (e.g. `annual-report-medical-assistance-dying-2022.html`). Use these for trends. Verify each URL exists.
- **Trachtenberg & Manns (2017), "Cost analysis of medical assistance in dying in Canada," CMAJ 189(3):E101:** https://www.cmaj.ca/content/189/3/E101
- **Office of the Parliamentary Budget Officer (2020), "Cost Estimate for Bill C-7 'Medical Assistance in Dying'":** locate on pbo-dpb.ca.
- **Statistics Canada:** total deaths by year, for context and denominators. Find the appropriate vital statistics table.
- Check whether Health Canada or open.canada.ca publishes the underlying tables as CSV. If so, prefer those over scraping.

## 4. Key facts already established (2024 data unless noted)

### Volume
- 16,499 MAID provisions: Track 1 = 15,767 (95.6%), Track 2 = 732 (4.4%)
- MAID was 5.1% of all deaths in Canada
- Median age: 78.0 (Track 1), 75.9 (Track 2)

### Track 2 trend (Figure 2.2a)

| Year | Track 1 | Track 2 | Total | Total growth |
|---|---|---|---|---|
| 2019 | 5,461 | NA | 5,461 | NA |
| 2020 | 7,451 | 18 | 7,469 | 36.8% |
| 2021 | 9,842 | 224 | 10,066 | 34.8% |
| 2022 | 12,730 | 469 | 13,199 | 31.1% |
| 2023 | 14,802 | 625 | 15,427 | 16.9% |
| 2024 | 15,767 | 732 | 16,499 | 6.9% |

- The 2020 Track 2 count is Quebec only, under a court exemption.
- Track 2 growth: +33.3% (2022→23), +17.1% (2023→24). Still growing faster than total MAID, but decelerating.
- Track 2 is 4.4% of provisions but 24.2% of ineligibility findings.

### Nature of suffering (Figure 3.4a, % of recipients; multi-select)

| Source | Track 1 | Track 2 |
|---|---|---|
| Loss of ability to engage in meaningful activities | 95.1 | 97.5 |
| Loss of ability to perform activities of daily living | 85.4 | 85.1 |
| Loss of independence | 75.4 | 78.7 |
| Loss of dignity | 63.5 | 73.9 |
| Emotional distress/anxiety/fear/existential suffering | 57.9 | 63.3 |
| Inadequate pain control, or concern about it | 55.9 | 59.8 |
| Inadequate control of other symptoms, or concern | 57.0 | 43.6 |
| Perceived burden on family, friends or caregivers | 48.4 | 50.3 |
| Isolation or loneliness | 21.9 | 44.7 |
| Loss of control of bodily functions | 32.1 | 31.8 |
| Other | 2.9 | 2.7 |

### Number of suffering sources per recipient (Figure 3.4b, %)

| # sources | Track 1 | Track 2 |
|---|---|---|
| 1 | 0.4 | X (suppressed) |
| 2 | 2.3 | X |
| 3 | 7.0 | 4.1 |
| 4 | 14.3 | 11.8 |
| 5 | 18.7 | 18.3 |
| 6 | 19.9 | 21.8 |
| 7 | 18.1 | 19.9 |
| 8 | 12.8 | 15.7 |
| 9 | 6.6 | 7.7 |

### Co-occurrence facts (Section 3.4, "self-perceived burden" and "isolation" subsections)
- **Burden**
  - Average sources cited by those citing burden: 6.8 (Track 1), 7.1 (Track 2), vs. 5.1 and 5.6 for those not citing it.
  - Note: these are *total* counts including burden itself, so roughly 6 *other* sources.
  - Burden was the sole source in fewer than 5 cases, and alongside only one other source in 18 cases, all Track 1.
- **Isolation/loneliness**
  - Average sources cited: 7.5 (Track 1), 7.1 (Track 2), vs. 5.5 and 5.8 for those not citing it.
  - Never the sole source; alongside only one other source in fewer than 5 cases.
- **Limitation:** only marginals and these few conditional stats are published. A full joint distribution would need microdata. Consider whether bounds (e.g. Fréchet bounds on pairwise overlap) or a simulation consistent with the published marginals and count distribution are worth doing, and label them clearly as estimates.

### Decline indicators, Track 1 (Figure 3.3a)
- 90.0% unable to do most or all ADLs/IADLs
- 50.5% reduced or minimal oral intake or difficulty swallowing
- 46.2% cachexia or marked weight/muscle change
- 39.9% significant shortness of breath
- 24.8% dependent on life-sustaining treatment
- Track 1 condition duration: 47.1% had their condition for less than 1 year. Cancer was cited in 63.6% of Track 1 cases.

### Requesters who died naturally before MAID (Table 2.3c)
4,017 requesters died of another cause. Median days from request to death:
- Died before both assessments were completed (n=752): 7 days
- Found eligible, died before the scheduled date (n=1,502): 19 days
- Never chose a date (n=1,661): 45 days

This is a partial empirical anchor for the Track 1 counterfactual. Caveat: it is likely biased short, because these people were probably sicker than those who survived long enough to receive MAID.

### Counterfactual assumptions from the literature (not measured)
- **CMAJ 2017:** 40% lose ~1 week, 60% lose ~1 month → expected ≈ 3 weeks.
- **PBO 2020:** 14% lose 2 weeks, 25% 1 month, 45% 3 months, 13% 6 months, 3% 1 year → expected ≈ 12 weeks. Under this distribution, ~97% would have died within 6 months anyway.
- **Rough outputs computed so far:**
  - Track 1 person-years lost: ≈ 900 (CMAJ) to ≈ 3,700 (PBO)
  - Deaths that plausibly would not have occurred within 6 months: ~3% of Track 1 (~470) + all Track 2 (732) ≈ 1,200, or ~7% of MAID deaths
- **Track 2 counterfactual:** unknown and likely years. 34.1% had lived with their condition for more than 10 years. Model it as a scenario range, not a point estimate.

### Other Track 2 profile points
- 56.7% women
- 61.5% self-report a disability (vs. 31.6% in Track 1)
- More likely to live alone (Section 5.3)

## 5. Policy context and timeline (verify for updates)

- **2016:** MAID legalized.
- **2021:** Bill C-7 creates Track 2 (death not reasonably foreseeable). Mental illness as the sole condition is excluded, with a sunset clause.
- **Feb 2024:** The mental-illness expansion is delayed (third delay) to **March 17, 2027**.
- **April 2026:** CAMH recommends an indefinite delay.
- **May 2026:** 90+ disability and mental health organizations call for a permanent halt.
- **June 2026:** The special joint parliamentary committee recommends an indefinite pause, with some dissents.
- **Sept 2026:** Private member's Bill C-218, which would block the expansion, is under debate in the House.

### Main lines of criticism
1. **Track 2 and expansion.** Non-dying recipients, long counterfactuals, and social drivers like loneliness, poverty, and gaps in disability support.
2. **Social suffering and system gaps in general, including Track 1.** Burden and loneliness pushing requests, plus gaps in palliative and home care. Mason's argument sits here.
3. **In principle / slippery slope.** Mostly from religious and pro-life groups; not an empirical claim.

### Defender responses
- Track 2 safeguards visibly filter cases (high ineligibility share, 90-day assessment period).
- Growth is decelerating.
- Burden and loneliness almost always co-occur with severe decline.
- Track 1 counterfactuals are weeks to months.

### Honest synthesis so far
- The counterfactual argument bounds the *magnitude* of harm for Track 1. It does not answer the *mechanism* question: whether burden is causally decisive even when death is near.
- Track 2 and the pending expansion are where the counterfactual is long and social factors are most prevalent. That is the most defensible place to focus concern.

## 6. Deliverable

A static site on GitHub Pages:

- **Repo structure**
  - `data/`: raw scraped tables plus cleaned CSVs, with a source URL recorded for every table
  - `analysis/`: Python or notebooks
  - `site/`: the built pages
- **Pages / sections**
  1. Overview and key takeaways
  2. Sources of suffering: the chart redone correctly as marginal rates, plus the co-occurrence facts and a sources-per-person distribution chart
  3. Counterfactual model: interactive, with sliders for the life-shortened distribution. Shows expected weeks lost, person-years, and the count dying earlier than 6 or 12 months under each scenario. CMAJ and PBO presets. Track 2 as a separate scenario range.
  4. Track 2 trend (2019–2024) and profile vs. Track 1
  5. Policy timeline
  6. Methods and limitations
- **Standards**
  - Every number links to its source table.
  - Distinguish measured data from assumptions.
  - No editorializing beyond what the data supports.
  - Present both readings fairly.
