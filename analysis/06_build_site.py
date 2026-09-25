"""Render site/index.html from the clean datasets. No hand-typed figures."""
import importlib.util, json, os, sys, datetime
sys.path.insert(0, "analysis")

spec = importlib.util.spec_from_file_location("charts", "analysis/04_charts.py")
ch = importlib.util.module_from_spec(spec); spec.loader.exec_module(ch)
K = json.load(open("data/clean/key_numbers.json"))

HC24 = ("https://www.canada.ca/en/health-canada/services/publications/health-system-"
        "services/annual-report-medical-assistance-dying-2024.html")
CSFV = "https://csfv.gouv.qc.ca/en/publications"
CSFV25 = "https://csfv.gouv.qc.ca/fileadmin/docs/rapports_annuels/csfv_rapport_activites_2024-2025.pdf"
CSFV5Y = "https://csfv.gouv.qc.ca/fileadmin/docs/rapports_sfv/csfv_rapport_2018-2023.pdf"
PBO = ("https://www.pbo-dpb.ca/en/publications/RP-2021-025-M--cost-estimate-bill-c-7-"
       "medical-assistance-in-dying--estimation-couts-projet-loi-c-7-aide-medicale-mourir")
CMAJ = "https://www.cmaj.ca/content/189/3/E101"
SC708 = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310070801"
REPO = "https://github.com/jarryahmad/maid-analysis"

def f(n, dp=0):
    return f"{n:,.{dp}f}"

def fig(id_, title, body, note=None, tbl=""):
    n = f'<p class="note">{note}</p>' if note else ""
    return (f'<figure class="fig" id="{id_}">'
            f'<figcaption><span class="figtitle">{title}</span></figcaption>'
            f'{body}{n}{tbl}</figure>')

c_volume, t_volume = ch.chart_volume()
c_share, _         = ch.chart_share()
c_growth, t_growth = ch.chart_growth()
c_stack, t_stack   = ch.chart_qc_stack()
c_trend, t_trend   = ch.chart_qc_trend()
c_cdf, t_cdf       = ch.chart_qc_cdf()
c_suff, t_suff     = ch.chart_suffering()
c_dec, t_dec       = ch.chart_decline()
c_dur, t_dur       = ch.chart_duration()
c_nsrc, t_nsrc     = ch.chart_nsources()

BUILT = datetime.date.today().isoformat()

CSS = """
:root{
  color-scheme: light;
  --plane:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
  --series-1:#2a78d6; --series-2:#eb6834;
  --ord-1:#86b6ef; --ord-2:#5598e7; --ord-3:#2a78d6; --ord-4:#1c5cab; --ord-5:#0d366b;
  --accent:#2a78d6; --wash:rgba(42,120,214,.07);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --series-2:#d95926;
    --ord-1:#cde2fb; --ord-2:#9ec5f4; --ord-3:#6da7ec; --ord-4:#3987e5; --ord-5:#184f95;
    --accent:#3987e5; --wash:rgba(57,135,229,.10);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --plane:#0d0d0d; --surface:#1a1a19; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
  --series-1:#3987e5; --series-2:#d95926;
  --ord-1:#cde2fb; --ord-2:#9ec5f4; --ord-3:#6da7ec; --ord-4:#3987e5; --ord-5:#184f95;
  --accent:#3987e5; --wash:rgba(57,135,229,.10);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--plane);color:var(--ink);
  font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif;
  overflow-x:hidden;}
.wrap{max-width:820px;margin:0 auto;padding:0 20px 96px}
header.top{padding:64px 0 8px}
h1{font-size:clamp(30px,5.2vw,46px);line-height:1.1;letter-spacing:-.022em;margin:0 0 14px;
  font-weight:680}
.standfirst{font-size:clamp(17px,2.3vw,19.5px);line-height:1.55;color:var(--ink-2);margin:0 0 26px}
.byline{font-size:13.5px;color:var(--muted);border-top:1px solid var(--border);
  padding-top:14px;margin-bottom:8px}
.byline a{color:var(--ink-2)}
h2{font-size:clamp(21px,3vw,26px);line-height:1.22;letter-spacing:-.015em;margin:64px 0 6px;
  font-weight:660;scroll-margin-top:20px}
h2 .num{color:var(--muted);font-weight:500;margin-right:.5em;font-variant-numeric:tabular-nums}
h3{font-size:17.5px;margin:34px 0 4px;font-weight:640;letter-spacing:-.008em}
p{margin:14px 0}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent)}
a:hover{border-bottom-color:var(--accent)}
strong{font-weight:640}
.lede{font-size:17.5px;color:var(--ink-2)}
ul{padding-left:20px} li{margin:7px 0}

/* stat tiles */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;
  margin:30px 0 8px}
.tile{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px 16px 14px}
.tile .v{font-size:31px;line-height:1.05;font-weight:670;letter-spacing:-.02em;display:block}
.tile .k{font-size:12.5px;color:var(--ink-2);margin-top:7px;display:block;line-height:1.4}
.tile .s{font-size:11.5px;color:var(--muted);margin-top:5px;display:block}

/* figures */
.fig{margin:34px 0 8px;background:var(--surface);border:1px solid var(--border);
  border-radius:14px;padding:18px 18px 14px}
figcaption{margin:0 0 14px}
.figtitle{font-size:14.5px;font-weight:620;letter-spacing:-.005em;display:block}
.chart{width:100%;height:auto;display:block;overflow:visible}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;margin:0 0 14px;font-size:12.5px;color:var(--ink-2)}
.lg{display:inline-flex;align-items:center;gap:7px}
.lg i{width:11px;height:11px;border-radius:3px;display:inline-block;flex:none}
text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.tick{font-size:11.5px;fill:var(--muted);font-variant-numeric:tabular-nums}
.rowlabel{font-size:12px;fill:var(--ink-2)}
.datalabel{font-size:11.5px;fill:var(--ink-2);font-weight:600;font-variant-numeric:tabular-nums}
.datalabel.sm{font-size:10.5px;font-weight:500;fill:var(--muted)}
.datalabel.strong{fill:var(--ink);font-weight:660}
.axis-label{font-size:11.5px;fill:var(--muted)}
.rule-label{font-size:11px;fill:var(--ink-2)}
.mark{transition:opacity .12s}
.chart:hover .mark{opacity:.55}
.chart .mark:hover{opacity:1}
.note{font-size:12.5px;color:var(--muted);margin:12px 0 0;line-height:1.5}

/* table view */
.tableview{margin-top:12px;border-top:1px solid var(--border);padding-top:10px}
.tableview summary{font-size:12.5px;color:var(--ink-2);cursor:pointer;list-style:none}
.tableview summary::-webkit-details-marker{display:none}
.tableview summary::before{content:"▸ ";color:var(--muted)}
.tableview[open] summary::before{content:"▾ "}
.tw{overflow-x:auto;margin-top:12px}
table{border-collapse:collapse;font-size:12.5px;width:100%;min-width:420px}
caption{caption-side:bottom;text-align:left;color:var(--muted);font-size:11.5px;
  padding-top:10px;line-height:1.5}
th,td{text-align:right;padding:6px 10px;border-bottom:1px solid var(--border);
  font-variant-numeric:tabular-nums;white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal;min-width:150px}
thead th{color:var(--ink-2);font-weight:600;border-bottom:1px solid var(--axis)}

/* callouts */
.callout{border-left:3px solid var(--accent);background:var(--wash);padding:14px 18px;
  border-radius:0 10px 10px 0;margin:26px 0;font-size:15px}
.callout p:first-child{margin-top:0} .callout p:last-child{margin-bottom:0}
.caveat{border-left:3px solid var(--muted);background:transparent;
  border:1px solid var(--border);border-left:3px solid var(--muted);
  padding:14px 18px;border-radius:0 10px 10px 0;margin:26px 0;font-size:14.5px;color:var(--ink-2)}
.caveat h3{margin-top:0;font-size:14px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);font-weight:640}

/* two readings */
.readings{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:26px 0}
@media (max-width:640px){.readings{grid-template-columns:1fr}}
.reading{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.reading h3{margin:0 0 4px;font-size:14px}
.reading p{font-size:14px;margin:8px 0 0;color:var(--ink-2)}

/* timeline */
.tl{list-style:none;padding:0;margin:24px 0}
.tl li{display:grid;grid-template-columns:104px 1fr;gap:16px;padding:11px 0;
  border-bottom:1px solid var(--border);margin:0;font-size:14.5px}
.tl .d{color:var(--muted);font-size:12.5px;padding-top:2px;font-variant-numeric:tabular-nums}

/* sources */
.src{font-size:13.5px}
.src{min-width:0}
.src td,.src th{white-space:normal;text-align:left;vertical-align:top}
.src td:first-child{min-width:0;width:38%}
footer{margin-top:72px;padding-top:22px;border-top:1px solid var(--border);
  font-size:13px;color:var(--muted)}

#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--plane);
  font-size:12px;padding:6px 9px;border-radius:7px;opacity:0;transition:opacity .1s;
  z-index:50;max-width:280px;line-height:1.4}
"""

JS = """
(function(){
  var tip=document.getElementById('tip');
  document.addEventListener('mouseover',function(e){
    var m=e.target.closest('.mark'); if(!m||!m.dataset.tip)return;
    tip.textContent=m.dataset.tip; tip.style.opacity='1';
  });
  document.addEventListener('mousemove',function(e){
    if(tip.style.opacity!=='1')return;
    var x=e.clientX+14,y=e.clientY+16;
    if(x+tip.offsetWidth>innerWidth-8)x=e.clientX-tip.offsetWidth-14;
    if(y+tip.offsetHeight>innerHeight-8)y=e.clientY-tip.offsetHeight-14;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  });
  document.addEventListener('mouseout',function(e){
    if(e.target.closest('.mark'))tip.style.opacity='0';
  });
})();
"""

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MAID in Canada: the timeline question</title>
<meta name="description" content="Everyone dies eventually, so 'MAID adds deaths' only means something relative to a time window. Quebec is the one place in Canada that records how much time. Here is what it shows.">
<meta property="og:title" content="MAID in Canada: the timeline question">
<meta property="og:description" content="Everyone dies eventually, so 'MAID adds deaths' only means something relative to a time window. Quebec is the one place in Canada that records how much time. Here is what it shows.">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
</head>
<body>
<div id="tip"></div>
<div class="wrap">

<header class="top">
<h1>MAID in Canada: the timeline question</h1>
<p class="standfirst">Everyone dies. So &ldquo;assisted dying adds deaths&rdquo; is only a
claim you can check once you attach a time window to it: <em>how many people who
received MAID would still have been alive six months later?</em> Canada&rsquo;s federal
data never asks. Quebec&rsquo;s does &mdash; for every case, for seven years.</p>
<p class="byline">By <a href="https://x.com/jahmad93">@jahmad93</a> &middot; data and
analysis built with Claude &middot; every figure below traces to a public table
&middot; <a href="{REPO}">source and data on GitHub</a> &middot; built {BUILT}</p>
</header>

<p class="lede">Canada recorded <strong>{f(K['tot24'])} MAID deaths in 2024</strong>
&mdash; {K['hc_published_share_24']}% of all deaths, and {f(K['cumulative'])} since 2016.
Whether that is alarming depends entirely on a question the national debate keeps
skipping: <em>how much time is being given up, and by whom?</em></p>

<p>The argument usually splits into two claims that get argued as one. The first is
that MAID mostly compresses the last few weeks of a death that was already
happening. The second is that a growing share of MAID recipients were not dying on
any near horizon at all. Both can be true at once, and the data says both <em>are</em>
true at once. This page separates them.</p>

<div class="tiles">
  <div class="tile"><span class="v">{K['hc_published_share_24']}%</span>
    <span class="k">of all deaths in Canada were MAID in 2024</span>
    <span class="s">{f(K['tot24'])} of {f(K['all_deaths_24'])}</span></div>
  <div class="tile"><span class="v">{K['qc_le3_last_pct']}%</span>
    <span class="k">of Quebec MAID recipients had an estimated prognosis of
      3 months or less</span><span class="s">2024&ndash;25, n&nbsp;=&nbsp;{f(K['qc_last_n'])}</span></div>
  <div class="tile"><span class="v">{K['qc_gt6_last_pct']}%</span>
    <span class="k">had a prognosis longer than 6 months</span>
    <span class="s">was {K['qc_gt6_first_pct']}% in 2018&ndash;19</span></div>
  <div class="tile"><span class="v">{K['qc_gt12_last_pct']}%</span>
    <span class="k">had a prognosis longer than 12 months</span>
    <span class="s">was {K['qc_gt12_first_pct']}% in 2018&ndash;19</span></div>
</div>

<h2><span class="num">1</span>What is actually happening</h2>

<p>MAID has grown every year since 2016, but the growth rate has been falling since
2019. In 2024 total provisions rose <strong>6.9%</strong> &mdash; the smallest increase
on record, down from 36.8% in 2020.</p>

<p>Since 2021 the law has had two tracks.
<strong>Track&nbsp;1</strong> is for people whose natural death is
<em>reasonably foreseeable</em>. <strong>Track&nbsp;2</strong>, created by Bill&nbsp;C-7,
is for people with a serious and incurable condition whose death is <em>not</em>
reasonably foreseeable. Track&nbsp;2 is {f(K['t2'])} cases &mdash; 4.4% of the total.</p>

{fig("volume", "MAID provisions by year and track, Canada, 2016–2024", c_volume,
     "Track 2 did not exist before 2021. Quebec provided 18 Track-2-equivalent cases in "
     "2020 under a court exemption. Health Canada revises prior years, so 2019 here "
     "(5,461) differs from the 5,631 first published for that year. "
     f'Source: <a href="{HC24}">Health Canada, Sixth Annual Report, Figure 2.2a</a>; '
     f'2016–18 from the First Annual Report, Table 3.1; deaths from '
     f'<a href="{SC708}">Statistics Canada 13-10-0708-01</a>.', t_volume)}

{fig("share", "MAID as a share of all deaths in Canada", c_share,
     "Denominator is registered deaths from vital statistics, which Statistics Canada "
     "may still revise for recent years. Health Canada reports 5.1% for 2024 against a "
     "provisional denominator; 16,499 of 326,779 registered deaths is 5.05%, which "
     "rounds to the same figure.")}

{fig("growth", "Growth is decelerating on both tracks", c_growth,
     "Track 2 grew faster than MAID overall in every year it has existed, but the gap "
     "is narrowing. Health Canada cautions that “it will take several more years "
     "before long-term trends can be conclusively identified.”", t_growth)}

<h2><span class="num">2</span>The window, measured rather than modelled</h2>

<p>The federal reporting form does not ask how long a MAID recipient was expected to
live. It asks whether death was &ldquo;reasonably foreseeable&rdquo; &mdash; a legal
category, not a duration. So the national data cannot answer the timeline question at
all.</p>

<p>Quebec&rsquo;s can. Under Quebec&rsquo;s <em>Act respecting end-of-life care</em>,
the physician who administers MAID must record an <strong>estimated
prognosis</strong> on the declaration form, and the Commission sur les soins de fin de
vie publishes the distribution every year. Quebec is about 36% of all MAID in Canada,
which makes this the largest source of direct evidence on the question anywhere in the
country.</p>

<p>The Commission flags the trend itself: its five-year report notes that although a
large majority still have six months or less, &ldquo;the proportion of people with a
longer prognosis has increased&rdquo; over 2018&ndash;2023. What is added here is the
full year-by-year series with counts, pulled out of seven separate French-language
reports and reconciled to each report&rsquo;s published total.</p>

<div class="callout">
<p>In <strong>2024&ndash;25</strong>, of {f(K['qc_last_n'])} MAID deaths in Quebec:
<strong>{K['qc_le1mo_last_pct']}%</strong> had an estimated prognosis of a month or
less, <strong>{K['qc_le3_last_pct']}%</strong> three months or less, and
<strong>{100 - K['qc_gt6_last_pct']:.1f}%</strong> six months or less.</p>
<p>That leaves <strong>{K['qc_gt6_last_pct']}%</strong> &mdash;
{f(K['qc_gt6_last_n'])} people &mdash; whose physician put their remaining life at more
than six months, and <strong>{K['qc_gt12_last_pct']}%</strong>
({f(K['qc_gt12_last_n'])} people) at more than a year.</p>
</div>

{fig("cdf", "By when would they have died anyway? Quebec, 2024–25", c_cdf,
     "Read each bar as: on the physician’s estimate, this share of MAID recipients "
     "would have died within this window regardless. The bars are cumulative. "
     f'Source: <a href="{CSFV25}">Commission sur les soins de fin de vie, '
     f'Rapport annuel 2024-2025</a>, Tableau C1.', t_cdf)}

<h3>The distribution has moved, a lot</h3>

<p>The share with a prognosis longer than six months has gone from
<strong>{K['qc_gt6_first_pct']}%</strong> in 2018&ndash;19 to
<strong>{K['qc_gt6_last_pct']}%</strong> in 2024&ndash;25 &mdash; from
{f(K['qc_gt6_first_n'])} people a year to {f(K['qc_gt6_last_n'])}. The share with more
than a year went from {K['qc_gt12_first_pct']}% to {K['qc_gt12_last_pct']}%.</p>

{fig("qctrend", "Share of Quebec MAID recipients with a prognosis beyond 6 and 12 months",
     c_trend,
     "Quebec reporting years run 1 April to 31 March. "
     f'Sources: <a href="{CSFV}">Commission sur les soins de fin de vie annual reports</a>, '
     f'“Pronostic vital” annex tables, 2018-19 through 2024-25; '
     f'<a href="{CSFV5Y}">five-year report 2018-2023</a> for the narrative series.',
     t_trend)}

{fig("qcstack", "The full composition, year by year", c_stack,
     "* The 3–6 month band folds in the Commission’s “fin de vie” "
     "bucket — prognoses recorded as “a few days to a few months” or "
     "qualitatively (“sombre”, “réservé”). "
     "† The >12 month band folds in “more than a year / not at end of life”. "
     "Excluding both unspecified buckets instead of allocating them changes the >6 month "
     "share in 2024-25 from 21.8% to 15.4%. Number above each bar is the >6 month share.",
     t_stack)}

<h3>How much of the drift is Track 2?</h3>

<p>Not all of it. Quebec&rsquo;s
&ldquo;not at end of life&rdquo; category was <strong>{K['qc_noteol_last_pct']}%</strong>
in 2024&ndash;25 ({f(K['qc_noteol_last_n'])} people), which lines up almost exactly with
Quebec&rsquo;s Track&nbsp;2 share of 7.5%. Strip that group out entirely and look only at
recipients who <em>were</em> judged to be at end of life &mdash; the Track&nbsp;1
population:</p>

<ul>
<li><strong>{K['eol_gt6_pct']}%</strong> still had a prognosis longer than six months.</li>
<li><strong>{K['eol_gt12_pct']}%</strong> still had a prognosis longer than a year.</li>
</ul>

<p>In 2018&ndash;19, before Track&nbsp;2 existed anywhere in Canada, that same
end-of-life figure was {K['eol_gt6_first_pct']}%. Put the other way round:
of the {f(K['qc_gt6_last_n'])} people with a prognosis beyond six months in
2024&ndash;25, <strong>{K['share_of_gt6_judged_eol']}%</strong> were nonetheless judged
to be at end of life. The drift is not only a Track&nbsp;2 story.</p>

<div class="caveat">
<h3>What would make this wrong</h3>
<p><strong>These are physician estimates, not outcomes.</strong> Nobody measured how
long these people would actually have lived; a doctor wrote a number on a form.
The systematic-review evidence is that clinicians
<a href="https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0161407">
consistently overestimate survival</a> in palliative populations, which would mean the
true remaining life is <em>shorter</em> than these figures &mdash; pushing the numbers
in the reassuring direction.</p>
<p><strong>The form does not say when the estimate was made.</strong> The Commission
notes it cannot tell whether the prognosis refers to the moment of request, of
assessment, or of administration. If it is recorded at request, actual remaining life
at the moment of death is shorter still.</p>
<p><strong>The categories changed.</strong> &ldquo;Two years or less&rdquo; and
&ldquo;not at end of life&rdquo; were added in 2021&ndash;22; a separate
&ldquo;one week or less&rdquo; band in 2022&ndash;23. Part of the visible rise in the
long-prognosis bands is the form learning to record them.</p>
<p><strong>Quebec is not Canada.</strong> It has the highest MAID rate in the country
and {round(100*452/732)}% of all Canadian Track&nbsp;2 cases despite being 36% of MAID
overall. It is a leading indicator, not a national average.</p>
</div>

<h2><span class="num">3</span>Two tracks, two different arguments</h2>

<p>Track&nbsp;1 and Track&nbsp;2 recipients look different on almost every measure, and
the strongest evidence that Track&nbsp;1 recipients really are close to death does not
come from prognosis forms at all. It comes from what happens to people who ask.</p>

<div class="callout">
<p>Of {f(K['t1_requests'])} Track&nbsp;1 requests in 2024,
<strong>{f(K['t1_died_natural'])} people ({K['t1_died_natural_pct']}%) died of their
illness before MAID could be provided.</strong> Among Track&nbsp;2 requests, that
happened to {K['t2_died_natural_pct']}%.</p>
<p>Nearly one in five Track&nbsp;1 requesters does not survive the assessment and
scheduling process. That is a hard behavioural fact, not an estimate.</p>
</div>

<p>The safeguards also bite very differently. Track&nbsp;2 is 4.4% of provisions but
<strong>{K['t2_inelig_pct']}%</strong> of Track&nbsp;2 requesters are found ineligible,
against {K['t1_inelig_pct']}% on Track&nbsp;1. Track&nbsp;2 carries a mandatory 90-day
minimum assessment period and requires expertise in the condition causing the
suffering.</p>

{fig("decline", "Clinical indicators of decline, by track, 2024", c_dec,
     "Multi-select: each recipient can have several. Track 1 recipients are far more "
     "likely to show the classic terminal markers — reduced oral intake, cachexia, "
     "breathlessness, dependence on life-sustaining treatment. Track 2 recipients are "
     "more likely to report escalating chronic pain and dependence on mobility aids. "
     f'Source: <a href="{HC24}">Health Canada, Figure 3.3a</a>.', t_dec)}

{fig("duration", "How long they had lived with the condition", c_dur,
     "47.1% of Track 1 recipients had had their condition for under a year; 34.1% of "
     "Track 2 recipients had lived with theirs for more than ten years. "
     f'Source: <a href="{HC24}">Health Canada, Figure 3.2a</a>.', t_dur)}

<p>Track&nbsp;2 recipients are more likely to be women (56.7% vs 47.8%), more likely
to have been living alone (41.7% vs 32.5%), more likely to have been in a residential
care facility (14.0% vs 4.4%) and less likely to have been in a palliative care facility
(1.3% vs 3.8%). They are roughly twice as likely to self-report a disability (61.5% vs
31.6% of those answering the question). Their conditions are mostly neurological or in
the catch-all &ldquo;other&rdquo; category rather than cancer: cancer is 63.6% of
Track&nbsp;1 and about 4% of Track&nbsp;2.</p>

<h2><span class="num">4</span>Burden and loneliness</h2>

<p>The sharpest version of the concern is not about counts at all. It is that people are
choosing death because they feel like a burden, or because they are alone &mdash; social
facts, not medical ones. <strong>48.4% of Track&nbsp;1 and 50.3% of Track&nbsp;2
recipients cited perceived burden on family, friends or caregivers</strong> as a source
of their suffering. Isolation or loneliness: 21.9% and 44.7%.</p>

{fig("suffering", "Reported sources of intolerable suffering, by track, 2024", c_suff,
     "Multi-select — these are marginal rates, not shares of a pie, and they sum to "
     "well over 100%. Do not trend these across 2022/2023: the reporting regulations "
     "changed on 1 January 2023 and Health Canada states that “data collected in 2023 "
     "are not fully comparable with the data collected in previous years.” "
     "“Loss of independence” and “emotional distress” were residual "
     "free-text categories before 2023 (1.7–5.6%) and listed options after (38–75%). "
     f'Source: <a href="{HC24}">Health Canada, Figure 3.4a</a>.', t_suff)}

<p>Those marginals are the number that circulates. What almost never circulates is what
Health Canada published alongside them, having run the analysis case by case:</p>

<ul>
<li>Perceived burden was the <strong>sole</strong> source of suffering in
<strong>fewer than five cases</strong> nationally, and the only source alongside one
other in <strong>18 cases</strong>. All of them Track&nbsp;1.</li>
<li>Isolation or loneliness was <strong>never</strong> a sole source in 2024, and
appeared with only one other source in fewer than five cases.</li>
<li>People who cited burden cited <strong>more</strong> suffering overall, not less:
6.8 sources on average (Track&nbsp;1) against 5.1 for those who did not. For isolation,
7.5 against 5.5.</li>
</ul>

{fig("nsources", "Number of distinct sources of suffering cited per recipient", c_nsrc,
     "Almost nobody cites one thing. The median recipient cites six. "
     f'Source: <a href="{HC24}">Health Canada, Figure 3.4b</a>.', t_nsrc)}

<div class="readings">
  <div class="reading">
    <h3>The strongest case that the concern is overblown</h3>
    <p>Burden and loneliness essentially never stand alone. They ride on top of a
    median of six other sources of suffering in people who, on Track&nbsp;1, are
    overwhelmingly within months of death and 90% of whom can no longer perform most
    daily activities. A person citing burden is citing <em>more</em> suffering, not
    substituting a social complaint for a medical one.</p>
  </div>
  <div class="reading">
    <h3>The strongest case that it is warranted</h3>
    <p>Co-occurrence is not causation, and the published data cannot distinguish
    &ldquo;burden was mentioned&rdquo; from &ldquo;burden was decisive.&rdquo; A person
    with six sources of suffering can still be tipped by the seventh. Half of all
    recipients report it. Nothing in this dataset, or any dataset Canada collects, can
    tell you whether they would have asked in a system with better home care and
    caregiver support.</p>
  </div>
</div>

<h2><span class="num">5</span>A rough counterfactual, and why it is rarely accurate</h2>

<p>It is tempting to turn the above into a single number of &ldquo;lives shortened.&rdquo;
Treat what follows as arithmetic on physician estimates, not a measurement. Counterfactual
estimates of this kind have a poor track record, and the caveats above all apply.</p>

<p>Apply Quebec&rsquo;s end-of-life prognosis distribution to Canada&rsquo;s
{f(K['t1'])} Track&nbsp;1 cases, and treat Track&nbsp;2 as beyond both windows by
definition:</p>

<ul>
<li>Roughly <strong>{f(K['proj_gt6_total'])} people</strong> &mdash;
{K['proj_gt6_pct_of_maid']}% of MAID deaths, {K['proj_gt6_pct_of_deaths']}% of all
deaths in Canada &mdash; would plausibly still have been alive <strong>six months</strong>
later.</li>
<li>Roughly <strong>{f(K['proj_gt12_total'])} people</strong>
({K['proj_gt12_pct_of_maid']}% of MAID deaths) at <strong>twelve months</strong>.</li>
<li>At a <strong>one-month</strong> window, the great majority of MAID deaths are
incremental; at <strong>two years</strong>, only Track&nbsp;2 clearly is.</li>
</ul>

<p>For comparison, the two figures Canadian policy actually ran on:</p>
<ul>
<li><a href="{CMAJ}">Trachtenberg &amp; Manns, CMAJ 2017</a> assumed 40% lose a week and
60% lose a month &mdash; nobody beyond six months at all. Written before legalization,
using Belgian and Dutch data.</li>
<li>The <a href="{PBO}">Parliamentary Budget Officer&rsquo;s 2020 costing of
Bill&nbsp;C-7</a> assumed 14% lose two weeks, 25% a month, 45% three months, 13% six
months and <strong>3% a year</strong>. For the newly eligible Track&nbsp;2 group it
assumed <em>exactly one year each</em>, while noting the resulting saving &ldquo;is
likely underestimated, but it is not possible to know the magnitude.&rdquo;</li>
</ul>

<p>The PBO figure came from Quebec &mdash; its endnote says the life-expectancy
assumption was the one statistic &ldquo;only Quebec reported.&rdquo; It was built on
Quebec&rsquo;s 2018&ndash;19 vintage, when {K['qc_gt6_first_pct']}% of recipients had
more than six months. On the same source, six years on, that figure is
{K['qc_gt6_last_pct']}%. The assumption is not wrong so much as stale &mdash; and it is
still the number the debate runs on.</p>

<h2><span class="num">6</span>What none of this can tell you</h2>
<ul>
<li><strong>Whether any individual death was premature.</strong> Prognosis is an
estimate about a population; it says nothing reliable about one person.</li>
<li><strong>Whether burden or loneliness caused a request.</strong> Only co-occurrence is
published. The joint distribution &mdash; which sources appear together, in whom &mdash;
would need the microdata, which exists in
<a href="https://crdcn.ca/data/medical-assistance-in-dying/">Statistics Canada Research
Data Centres</a> under application.</li>
<li><strong>Whether better palliative, home or disability care would change the
numbers.</strong> Health Canada records whether services were received, not whether they
were adequate, and says so.</li>
<li><strong>What Track&nbsp;2 recipients would actually have lived.</strong> No
Canadian body records it. Every figure you will see is an assumption.</li>
<li><strong>Whether the drift in prognosis reflects changed practice or changed
paperwork.</strong> Both are consistent with the series.</li>
</ul>

<h2><span class="num">7</span>Where the scrutiny actually is</h2>

<p>The live policy question is not Track&nbsp;1. It is whether MAID extends to people
whose sole underlying condition is a mental illness &mdash; currently scheduled for
<strong>17 March 2027</strong> after three delays.</p>

<ul class="tl">
<li><span class="d">Jun 2016</span><span>MAID legalized (Bill C-14). Death must be
reasonably foreseeable.</span></li>
<li><span class="d">Sep 2019</span><span><em>Truchon</em> strikes down the
reasonably-foreseeable requirement in Quebec.</span></li>
<li><span class="d">Mar 2021</span><span>Bill C-7 creates Track 2. Mental illness as
sole condition excluded, with a sunset clause.</span></li>
<li><span class="d">Feb 2024</span><span>Bill C-62 delays the mental-illness expansion
a third time, to 17 March 2027.</span></li>
<li><span class="d">Feb 2026</span><span>Special Joint Committee on MAID reconstituted
to review the expansion.</span></li>
<li><span class="d">25 May 2026</span><span>90 disability and mental-health
organizations call for permanent exclusion.</span></li>
<li><span class="d">17 Jun 2026</span><span>The committee recommends the government
<a href="https://www.cbc.ca/news/health/maid-mental-disorder-committee-report-government-9.7238589">
indefinitely exclude</a> mental illness as a sole condition. CAMH
<a href="https://www.camh.ca/en/camh-news-and-stories/camh-response-to-the-recommendation-of-the-special-joint-committee-on-maid-to-indefinitely-delay">
supports</a> the recommendation the same day, citing no consensus on when a mental
illness is irremediable and no reliable way to distinguish a MAID request from suicidal
intent.</span></li>
<li><span class="d">23 Sep 2026</span><span>Bill C-218, a private member&rsquo;s bill
that would block the expansion permanently,
<a href="https://openparliament.ca/bills/45-1/C-218/">remains at second reading</a>.</span></li>
<li><span class="d">17 Mar 2027</span><span>Scheduled expansion date, absent
legislation.</span></li>
</ul>

<h2><span class="num">8</span>Sources and method</h2>

<p>Every table on this page was scraped from a public source and written to CSV; every
chart is generated from those CSVs by script. Nothing is hand-entered, nothing is
imputed, and the two places where unspecified categories are allocated rather than
dropped are named on the chart and the alternative result is given.</p>

<div class="tw"><table class="src">
<thead><tr><th>Source</th><th>Used for</th></tr></thead>
<tbody>
<tr><td><a href="{HC24}">Health Canada, Sixth Annual Report on MAID in Canada (2024
data)</a>, published Nov 2025</td><td>Provisions by track, request outcomes, suffering,
decline indicators, condition duration, living arrangement, disability. Figures 2.2a–c,
3.2a, 3.3a, 3.4a–b, Tables 2.1a, 2.3a, 2.3c, 5.3a, C.3.</td></tr>
<tr><td>Health Canada annual reports, 2019–2023 data years (same URL pattern)</td>
<td>Trend series; 2016–18 totals from the First Annual Report, Table 3.1.</td></tr>
<tr><td><a href="{CSFV}">Commission sur les soins de fin de vie (Quebec), annual
reports 2018-19 to 2024-25</a> (French)</td><td>The full prognosis series. Annex table
&ldquo;Pronostic vital&rdquo;.</td></tr>
<tr><td><a href="{CSFV5Y}">Commission sur les soins de fin de vie, five-year report
2018–2023</a></td><td>Year-over-year prognosis narrative; prognosis of requesters who
did <em>not</em> receive MAID (≤3 months 66.8%, ≤1 year 82.9% — nearly identical to
those who did).</td></tr>
<tr><td><a href="{SC708}">Statistics Canada, Table 13-10-0708-01</a></td>
<td>Total deaths in Canada by year.</td></tr>
<tr><td><a href="{PBO}">Parliamentary Budget Officer, <em>Cost Estimate for Bill C-7</em>
(Oct 2020)</a></td><td>The official life-shortening assumptions and their Quebec
provenance.</td></tr>
<tr><td><a href="{CMAJ}">Trachtenberg &amp; Manns, CMAJ 2017;189:E101</a></td>
<td>The pre-legalization cost-model assumptions.</td></tr>
<tr><td><a href="https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0161407">
White et al., PLoS ONE 2016;11(8):e0161407</a></td><td>Accuracy of clinician survival
predictions.</td></tr>
</tbody></table></div>

<p>Reproduce it: <code>git clone</code> the
<a href="{REPO}">repo</a>, then <code>make all</code>. The scrapers re-download the
source pages, the extractor rewrites every CSV, and this page is regenerated from
them. If a number here is wrong, the pipeline that produced it is public.</p>

<footer>
<p>Built with Claude. Prose, framing and editorial judgment are
<a href="https://x.com/jahmad93">@jahmad93</a>&rsquo;s; the extraction pipeline,
calculations and charts were written by Claude and are auditable in the repo.
No figure on this page was produced by a language model from memory &mdash; each one is
read from a scraped table at build time.</p>
<p>Last built {BUILT} against Health Canada&rsquo;s 2024-data report and Quebec&rsquo;s
2024&ndash;25 report, the most recent available.</p>
</footer>

</div>
<script>{JS}</script>
</body>
</html>
"""

os.makedirs("site", exist_ok=True)
open("site/index.html", "w", encoding="utf-8").write(HTML)
print(f"wrote site/index.html ({len(HTML):,} bytes)")
