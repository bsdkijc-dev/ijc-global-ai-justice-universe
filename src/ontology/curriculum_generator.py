"""Generate a 10-module open Judicial & Legal Education AI Curriculum (Pillar P19)."""

import csv
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_CSV = ROOT / "data" / "curated" / "judicial_ai_curriculum_10.csv"
OUT_MD = ROOT / "reports" / "JUDICIAL_AI_CURRICULUM_2027.md"

MODULES: List[Dict[str, str]] = [
    {"module_id": "MOD-01", "title": "Comparative Judicial AI Landscape (46 Jurisdictions)", "audience": "Judges & Judicial Academies", "pillar": "P19", "lab_module": "src/evidence/jurisdiction_atlas.py", "benchmark_ref": "UNESCO AI Guidelines; CNJ Res 615/2025"},
    {"module_id": "MOD-02", "title": "Constitutional Separation of Powers & Non-Delegation", "audience": "Constitutional & Appellate Judges", "pillar": "P01", "lab_module": "src/evidence/precedent_graph.py", "benchmark_ref": "Colombia T-323/2024; Italy Law 132/2025"},
    {"module_id": "MOD-03", "title": "Detecting & Preventing AI Citation Hallucinations", "audience": "Judges, Clerks & Bar Associations", "pillar": "P18", "lab_module": "src/prototype/citation_and_triage_gate.py", "benchmark_ref": "Mata v Avianca; Ayinde; Arabyads"},
    {"module_id": "MOD-04", "title": "Algorithmic Due Process & Source-Code Transparency", "audience": "Defence Counsel & Trial Judges", "pillar": "P02", "lab_module": "src/prototype/aia_generator.py", "benchmark_ref": "Spain SC 1119/2025; State v Loomis"},
    {"module_id": "MOD-05", "title": "Biometrics, Facial Recognition & Corroboration Standards", "audience": "Prosecutors & Police Oversight", "pillar": "P07", "lab_module": "src/evidence/query_cli.py", "benchmark_ref": "Germany hessenDATA; Bridges; Taiwan 114 Tai-Shang 5166"},
    {"module_id": "MOD-06", "title": "Fairness & False-Positive Disparity Auditing in Risk Tools", "audience": "Probation, Bail & Sentencing Judges", "pillar": "P11", "lab_module": "src/prototype/risk_audit_simulator.py", "benchmark_ref": "Ewert v Canada; Netherlands OxRec/SyRI"},
    {"module_id": "MOD-07", "title": "Synthetic Media, Deepfakes & Chain-of-Custody Admissibility", "audience": "Forensic Experts & Criminal Courts", "pillar": "P08", "lab_module": "src/prototype/synthetic_media_gate.py", "benchmark_ref": "Proposed US FRE 707; South Korea NPA"},
    {"module_id": "MOD-08", "title": "Automated Judgment Anonymisation & Open Justice", "audience": "Court Registrars & Data Protection Officers", "pillar": "P10", "lab_module": "src/prototype/anonymisation_gate.py", "benchmark_ref": "Estonia Krat; EU GDPR/LED"},
    {"module_id": "MOD-09", "title": "Multilingual Courtroom ASR & Access to Justice", "audience": "Court Administrators & Legal Aid", "pillar": "P09", "lab_module": "src/prototype/multilingual_glossary.py", "benchmark_ref": "India SUVAS; Philippines Scriptix; Tanzania"},
    {"module_id": "MOD-10", "title": "Zero-Budget Sovereign Computing & 2027-2045 Governance", "audience": "Ministries of Justice & Tech Leads", "pillar": "P27", "lab_module": "src/run_all.py", "benchmark_ref": "Uzbekistan Law ORK-1115; Philippines AM 25-11-28-SC"},
]


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(MODULES[0].keys()))
        writer.writeheader()
        writer.writerows(MODULES)

    md = [
        "# Judicial & Legal Education AI Curriculum (2027 Edition)",
        "",
        "**Pillar:** `P19 — Judicial & Legal Education Transformation` | **Cost:** Zero Incremental Cash Expenditure",
        "",
        "| Module | Title | Target Audience | Offline Lab | Comparative Benchmark |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for m in MODULES:
        md.append(f"| {m['module_id']} | {m['title']} | {m['audience']} | `{m['lab_module']}` | {m['benchmark_ref']} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Generated 10-module Judicial AI Curriculum -> {OUT_CSV.name}")


if __name__ == "__main__":
    main()
