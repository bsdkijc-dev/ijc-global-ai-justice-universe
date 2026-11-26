"""Build Cross-Jurisdictional Constitutional & Due Process Precedent Graph from jurisdiction_atlas_46.json."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS_JSON = ROOT / "data" / "curated" / "jurisdiction_atlas_46.json"
SOURCES_JSON = ROOT / "sources" / "source-registry.json"
OUT_CSV = ROOT / "data" / "curated" / "precedent_graph_edges.csv"
OUT_JSON = ROOT / "data" / "curated" / "precedent_graph.json"
OUT_MD = ROOT / "reports" / "PRECEDENT_GRAPH_REPORT.md"

THEME_MAP = [
    ("has_hallucination_cases", "THEME-HALLUCINATION-SANCTIONS", "Hallucination & Citation Sanctions"),
    ("has_biometric_or_frt_pushback", "THEME-FRT-BIOMETRIC-LIMITS", "Biometric / FRT Oversight & Limits"),
    ("has_judicial_ai_policy", "THEME-JUDICIAL-AI-POLICY", "Judicial AI Policy / Guidelines"),
    ("has_national_ai_law_or_strategy", "THEME-NATIONAL-AI-STATUTE", "National AI Law / Strategy"),
    ("has_multilingual_court_asr", "THEME-MULTILINGUAL-ASR", "Multilingual Court ASR / Translation"),
]


def build_graph() -> Dict[str, Any]:
    atlas = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    reg = json.loads(SOURCES_JSON.read_text(encoding="utf-8"))
    unesco_countries = {
        s["jurisdiction"]
        for s in reg["sources"]
        if s["verification_status"] == "VERIFIED_ACCESSIBLE"
        and "unesco" in (s.get("judicial_policies", "") + s.get("regulatory_instruments", "") + s.get("training_initiatives", "")).lower()
    }

    edges: List[Dict[str, str]] = []
    for rec in atlas:
        if rec["verification_status"] != "VERIFIED_ACCESSIBLE":
            continue
        jur = rec["jurisdiction_name"]
        sid = rec["source_ids"][0]
        fam = rec["legal_system_family"]

        for field, theme_id, theme_label in THEME_MAP:
            if rec.get(field) is True:
                edges.append({
                    "source_node": rec["jurisdiction_code"],
                    "jurisdiction": jur,
                    "legal_family": fam,
                    "relation": "EXHIBITS_GOVERNANCE_THEME",
                    "target_node": theme_id,
                    "target_label": theme_label,
                    "source_id": sid,
                    "evidence_label": "EXISTING_REAL_WORLD_RECORD",
                })
        if jur in unesco_countries:
            edges.append({
                "source_node": rec["jurisdiction_code"],
                "jurisdiction": jur,
                "legal_family": fam,
                "relation": "ALIGNS_WITH_UNESCO_GUIDELINES",
                "target_node": "THEME-UNESCO-GUIDELINES",
                "target_label": "UNESCO Judicial AI Guidelines Alignment",
                "source_id": sid,
                "evidence_label": "EXISTING_REAL_WORLD_RECORD",
            })

    return {"nodes_jurisdictions": 45, "edges_count": len(edges), "edges": edges}


def main() -> None:
    graph = build_graph()
    edges = graph["edges"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(edges[0].keys()))
        writer.writeheader()
        writer.writerows(edges)

    theme_counts: Dict[str, int] = {}
    for e in edges:
        theme_counts[e["target_label"]] = theme_counts.get(e["target_label"], 0) + 1

    md = [
        "# Cross-Jurisdictional Precedent & Governance Graph Report",
        "",
        f"- **Accessible Jurisdiction Nodes:** {graph['nodes_jurisdictions']} (Zambia `OXF-AIATLAS-44` excluded due to `SOURCE_INACCESSIBLE`)",
        f"- **Total Verified Edges (`EXISTING_REAL_WORLD_RECORD`):** {graph['edges_count']}",
        "",
        "## Theme Degree Centrality",
        "| Governance / Precedent Theme | Connected Jurisdictions |",
        "| :--- | :--- |",
    ]
    for lbl, cnt in sorted(theme_counts.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"| {lbl} | {cnt} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Built precedent graph: {graph['edges_count']} verified edges across {graph['nodes_jurisdictions']} jurisdictions")


if __name__ == "__main__":
    main()
