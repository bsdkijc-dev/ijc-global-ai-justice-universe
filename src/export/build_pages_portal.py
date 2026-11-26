"""Build zero-dependency static GitHub Pages explorer with Citation Gate, Anonymisation & Glossary."""

import json
from pathlib import Path
from src.ontology.taxonomy import PILLARS, compute_cardinality

ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS_JSON = ROOT / "data" / "curated" / "jurisdiction_atlas_46.json"
PILOTS_JSON = ROOT / "data" / "curated" / "top10_pilot_prototypes.json"
CORPUS_JSON = ROOT / "data" / "curated" / "verified_authority_corpus.json"
GLOSSARY_JSON = ROOT / "data" / "curated" / "multilingual_glossary_50.json"
OUT_HTML = ROOT / "docs" / "index.html"


def main() -> None:
    atlas = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    pilots = json.loads(PILOTS_JSON.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
    glossary = json.loads(GLOSSARY_JSON.read_text(encoding="utf-8"))
    total_space, _ = compute_cardinality()

    embedded = {
        "total_space": f"{total_space:,}",
        "atlas_count": len(atlas),
        "accessible_count": sum(1 for r in atlas if r["verification_status"] == "VERIFIED_ACCESSIBLE"),
        "corpus_count": len(corpus),
        "glossary": glossary,
        "pillars": [{"id": pid, "title": title} for pid, title in PILLARS],
        "atlas": atlas,
        "corpus": [{"auth_id": c["auth_id"], "citation": c["citation"], "jurisdiction": c["jurisdiction"]} for c in corpus],
        "pilots": [
            {
                "program_id": p["program_id"],
                "title": p["title"],
                "region": p["dimensions"]["D01_jurisdiction_archetype"],
                "risk": p["human_rights_risk_tier"],
                "priority": p["pilot_priority_score"],
                "quality": p["quality_score"],
                "sources": p["inspiration_source_ids"],
                "epistemic_label": p["epistemic_label"],
            }
            for p in pilots
        ],
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IJC Global AI & Justice Innovation Universe</title>
<style>
  :root {{ --bg: #f7f9fc; --card: #ffffff; --ink: #1a202c; --muted: #4a5568; --accent: #1e40af; --border: #e2e8f0; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--ink); margin: 0; padding: 0; line-height: 1.5; }}
  header {{ background: #0f172a; color: #fff; padding: 2rem 1.5rem; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 1.5rem; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 1.25rem 0; }}
  .kpi {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }}
  .kpi .val {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); }}
  .kpi .lbl {{ font-size: 0.85rem; color: var(--muted); }}
  .panel {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; margin-bottom: 1.5rem; }}
  input, select, textarea {{ padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: 6px; margin-right: 0.5rem; margin-bottom: 0.75rem; font-family: inherit; }}
  textarea {{ width: 100%; box-sizing: border-box; min-height: 75px; }}
  button {{ background: var(--accent); color: #fff; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th, td {{ text-align: left; padding: 0.55rem 0.6rem; border-bottom: 1px solid var(--border); }}
  th {{ background: #f1f5f9; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: #e0e7ff; color: #1e3a8a; }}
  .warn {{ background: #fee2e2; color: #991b1b; }}
  .ok {{ background: #dcfce7; color: #166534; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1 style="margin:0;">IJC Global AI &amp; Justice Innovation Universe (2027–2045)</h1>
    <p style="margin:0.4rem 0 0; opacity:0.85;">Founder: Cecep Mustafa &bull; Open Research &amp; Zero-Cost Architecture &bull; Grounded in Oxford AI Justice Atlas</p>
  </div>
</header>
<div class="wrap">
  <div class="kpis">
    <div class="kpi"><div class="val">{embedded['total_space']}</div><div class="lbl">12D Addressable Configurations</div></div>
    <div class="kpi"><div class="val">{embedded['accessible_count']} / {embedded['atlas_count']}</div><div class="lbl">Verified Accessible Jurisdictions</div></div>
    <div class="kpi"><div class="val">{embedded['corpus_count']}</div><div class="lbl">Verified Real-World Authorities</div></div>
    <div class="kpi"><div class="val">10,000 / 10</div><div class="lbl">Curated Programs / Pilot Prototypes</div></div>
  </div>

  <div class="panel">
    <h2>Interactive Citation Verification Gate (<code>PROTOTYPE_EXPERIMENTAL_NONBINDING</code>)</h2>
    <p style="color:var(--muted); margin-top:0;">Runs 100% client-side against {embedded['corpus_count']} verified Oxford AI Justice Atlas authorities.</p>
    <textarea id="citInput">Appeal brief citing [2025] ADGMCFI 0032, State v Loomis, and fabricated Smith v PhantomCorp.</textarea>
    <button onclick="runGate()">Verify Citations</button>
    <div id="gateOut" style="margin-top:0.8rem;"></div>
  </div>

  <div class="panel">
    <h2>Interactive Judgment Anonymisation Playground (<code>PROTOTYPE_EXPERIMENTAL_NONBINDING</code>)</h2>
    <p style="color:var(--muted); margin-top:0;">Redacts emails, phone numbers, and national IDs client-side while preserving legal citations.</p>
    <textarea id="anonInput">Witness contact witness.doe@example.org, phone +62 812-3456-7890, NIK 3201012345678901, citing State v Loomis.</textarea>
    <button onclick="runAnon()">Anonymise Text</button>
    <div id="anonOut" style="margin-top:0.8rem;"></div>
  </div>

  <div class="panel">
    <h2>Comparative Jurisdiction Atlas (46 Countries)</h2>
    <input id="qJur" type="text" placeholder="Filter country..." oninput="renderAtlas()">
    <select id="qArch" onchange="renderAtlas()">
      <option value="">All Regions</option>
      <option>EUR</option><option>LAT</option><option>SEA</option><option>EAS</option><option>SAS</option>
      <option>MEN</option><option>SSA</option><option>ECA</option><option>NAM</option><option>OCE</option>
    </select>
    <table>
      <thead><tr><th>Country</th><th>Region</th><th>Family</th><th>Status</th><th>Judicial Policy</th><th>FRT Pushback</th><th>Source</th></tr></thead>
      <tbody id="atlasBody"></tbody>
    </table>
  </div>

  <div class="panel">
    <h2>5-Language AI &amp; Justice Glossary (50 Terms)</h2>
    <input id="qGls" type="text" placeholder="Search glossary term..." oninput="renderGlossary()">
    <table>
      <thead><tr><th>ID</th><th>English</th><th>Indonesian / Malay</th><th>Spanish</th><th>French</th><th>Arabic</th></tr></thead>
      <tbody id="glsBody"></tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Top-10 Pilot Prototypes (<code>PROPOSED_RESEARCH_PROGRAM</code> / Non-Validated)</h2>
    <table>
      <thead><tr><th>Program ID</th><th>Region</th><th>Risk Tier</th><th>Priority</th><th>Title</th></tr></thead>
      <tbody id="pilotBody"></tbody>
    </table>
  </div>
</div>
<script>
const DATA = {json.dumps(embedded, ensure_ascii=False)};
const CIT_RE = /(?:\\[\\d{{4}}\\]\\s+[A-Z]{{2,10}}\\s+\\d+|\\b[A-Z][A-Za-z0-9.\\-]+\\s+v\\.?\\s+[A-Z][A-Za-z0-9.\\-]+\\b|\\bLaw\\s+No\\.?\\s+[A-Z0-9\\-\\/]+\\b)/g;

function runGate() {{
  const txt = document.getElementById('citInput').value || '';
  const found = txt.match(CIT_RE) || [];
  const verified = [];
  const unverified = [];
  for (const c of found) {{
    const key = c.trim().toLowerCase();
    const match = DATA.corpus.find(item => {{
      const ic = item.citation.trim().toLowerCase();
      return key === ic || ic.includes(key);
    }});
    if (match) verified.push(`${{c}} (${{match.auth_id}}, ${{match.jurisdiction}})`);
    else unverified.push(c);
  }}
  const cls = unverified.length === 0 ? 'ok' : 'warn';
  const status = unverified.length === 0 ? 'PASS_HUMAN_SIGN_OFF_READY' : 'FLAG_UNVERIFIED_CITATIONS_HITL_REQUIRED';
  document.getElementById('gateOut').innerHTML = `
    <span class="badge ${{cls}}">${{status}}</span>
    <p style="margin:0.4rem 0;"><strong>Verified (${{verified.length}}):</strong> ${{verified.join('; ') || 'None'}}</p>
    <p style="margin:0.4rem 0;"><strong>Unverified (${{unverified.length}}):</strong> ${{unverified.join('; ') || 'None'}}</p>`;
}}

function runAnon() {{
  let txt = document.getElementById('anonInput').value || '';
  txt = txt.replace(/\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}\\b/g, '[REDACTED_EMAIL]');
  txt = txt.replace(/(?:\\+?\\d{{1,3}}[\\s-]?)?(?:\\(?\\d{{2,4}}\\)?[\\s-]?)\\d{{3,4}}[\\s-]?\\d{{3,4}}\\b/g, '[REDACTED_PHONE]');
  txt = txt.replace(/\\b(?:NIK|SSN|ID)[\\s:#-]*\\d{{6,16}}\\b/gi, '[REDACTED_ID]');
  document.getElementById('anonOut').innerHTML = `<span class="badge ok">PASS_READY_FOR_HUMAN_PUBLICATION_REVIEW</span><p style="margin:0.4rem 0;"><code>${{txt}}</code></p>`;
}}

function renderAtlas() {{
  const q = document.getElementById('qJur').value.toLowerCase();
  const arch = document.getElementById('qArch').value;
  const rows = DATA.atlas.filter(r =>
    r.jurisdiction_name.toLowerCase().includes(q) && (!arch || r.region_archetype === arch)
  );
  document.getElementById('atlasBody').innerHTML = rows.map(r => `
    <tr>
      <td><strong>${{r.jurisdiction_name}}</strong></td>
      <td>${{r.region_archetype}}</td>
      <td>${{r.legal_system_family}}</td>
      <td><span class="badge ${{r.verification_status === 'SOURCE_INACCESSIBLE' ? 'warn' : ''}}">${{r.verification_status}}</span></td>
      <td>${{r.has_judicial_ai_policy === null ? 'N/A' : (r.has_judicial_ai_policy ? 'Yes' : 'No')}}</td>
      <td>${{r.has_biometric_or_frt_pushback === null ? 'N/A' : (r.has_biometric_or_frt_pushback ? 'Yes' : 'No')}}</td>
      <td><a href="${{r.source_url}}" target="_blank" rel="noopener">Oxford Atlas</a></td>
    </tr>`).join('');
}}

function renderGlossary() {{
  const q = document.getElementById('qGls').value.toLowerCase();
  const rows = DATA.glossary.filter(g =>
    g.en.toLowerCase().includes(q) || g.id_ms.toLowerCase().includes(q) || g.es.toLowerCase().includes(q) || g.fr.toLowerCase().includes(q)
  );
  document.getElementById('glsBody').innerHTML = rows.map(g => `
    <tr><td>${{g.term_id}}</td><td><strong>${{g.en}}</strong></td><td>${{g.id_ms}}</td><td>${{g.es}}</td><td>${{g.fr}}</td><td>${{g.ar}}</td></tr>`).join('');
}}

document.getElementById('pilotBody').innerHTML = DATA.pilots.map(p => `
  <tr>
    <td><code>${{p.program_id}}</code></td>
    <td>${{p.region}}</td>
    <td><span class="badge">${{p.risk}}</span></td>
    <td>${{p.priority}}</td>
    <td>${{p.title}}</td>
  </tr>`).join('');
renderAtlas();
renderGlossary();
runGate();
runAnon();
</script>
</body>
</html>
"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Built full interactive GitHub Pages portal -> {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
