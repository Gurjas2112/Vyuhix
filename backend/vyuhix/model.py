"""Loads the organisation's evidence model and turns it into edge probabilities and attack paths."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx
import numpy as np


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


@dataclass
class Model:
    org: dict
    nodes: dict[str, dict]
    edges: list[dict]
    controls: dict[str, dict]
    assumptions: dict
    epss: dict[str, float]
    edge_index: dict[str, int] = field(default_factory=dict)

    @property
    def entries(self) -> list[str]:
        return [n for n, v in self.nodes.items() if v["type"] == "entry"]

    @property
    def jewels(self) -> list[str]:
        return [n for n, v in self.nodes.items() if v["type"] == "crown_jewel"]


class ModelError(ValueError):
    """Raised for malformed models. The message names the first bad element; nothing is invented."""


def load_model(data_dir: Path) -> Model:
    org = _load(data_dir / "org.json")
    graph = _load(data_dir / "assets.json")
    controls = {c["id"]: c for c in _load(data_dir / "controls.json")["controls"]}
    assumptions = _load(data_dir / "assumptions.json")
    epss = {r["cve"]: float(r["epss"]) for r in _load(data_dir / "feeds" / "epss_snapshot.json")["data"]}
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = graph["edges"]
    validate(nodes, edges, controls)
    m = Model(org, nodes, edges, controls, assumptions, epss)
    m.edge_index = {e["id"]: i for i, e in enumerate(edges)}
    return m


def validate(nodes: dict, edges: list, controls: dict) -> None:
    seen = set()
    for e in edges:
        if e["id"] in seen:
            raise ModelError(f"duplicate edge id {e['id']}")
        seen.add(e["id"])
        for end in ("src", "dst"):
            if e[end] not in nodes:
                raise ModelError(f"edge {e['id']} references unknown node '{e[end]}'")
        if e["type"] != "exploits" and not 0.0 <= float(e.get("p", -1)) <= 1.0:
            raise ModelError(f"edge {e['id']} needs a probability p between 0 and 1")
    for c in controls.values():
        for eid in c.get("effects", {}):
            if eid not in seen:
                raise ModelError(f"control {c['id']} references unknown edge '{eid}'")


def edge_probabilities(m: Model, kev: set[str], controls_on: list[str], assumptions: dict) -> np.ndarray:
    ep = assumptions["edge_probability"]
    p = np.zeros(len(m.edges))
    for i, e in enumerate(m.edges):
        if e["type"] == "exploits":
            dst = m.nodes[e["dst"]]
            exposure = ep["exposure_internet"] if dst.get("internet_facing") else ep["exposure_internal"]
            floor = ep["kev_floor_internet"] if (e["cve"] in kev and dst.get("internet_facing")) else 0.0
            p[i] = max(m.epss.get(e["cve"], 0.05), floor) * exposure
        else:
            p[i] = float(e["p"])
    for cid in controls_on:
        for eid, factor in m.controls[cid].get("effects", {}).items():
            p[m.edge_index[eid]] *= factor
    return np.clip(p, 0.0, 1.0)


def edge_basis(m: Model, kev: set[str], assumptions: dict) -> dict[str, dict]:
    """Why each edge has its probability — shown in the provenance drawer."""
    ep = assumptions["edge_probability"]
    out = {}
    for e in m.edges:
        if e["type"] == "exploits":
            dst = m.nodes[e["dst"]]
            out[e["id"]] = {
                "source": "feeds",
                "cve": e["cve"],
                "epss": m.epss.get(e["cve"], 0.05),
                "in_kev": e["cve"] in kev,
                "internet_facing": bool(dst.get("internet_facing")),
                "kev_floor": ep["kev_floor_internet"],
            }
        else:
            out[e["id"]] = {"source": "evidence", "p": e["p"]}
    return out


def enumerate_paths(m: Model, max_hops: int) -> list[dict]:
    g = nx.DiGraph()
    for e in m.edges:
        g.add_edge(e["src"], e["dst"], id=e["id"])
    paths = []
    for entry in m.entries:
        for jewel in m.jewels:
            if entry not in g or jewel not in g:
                continue
            for nodes in nx.all_simple_paths(g, entry, jewel, cutoff=max_hops):
                eids = [g.edges[a, b]["id"] for a, b in zip(nodes, nodes[1:])]
                paths.append({"entry": entry, "jewel": jewel, "nodes": nodes, "edges": eids})
    paths.sort(key=lambda p: (p["jewel"], p["entry"], len(p["edges"]), p["edges"]))
    for k, p in enumerate(paths, 1):
        p["id"] = f"P{k}"
        p["text"] = path_text(m, p)
    return paths


def path_text(m: Model, path: dict) -> str:
    by_id = {e["id"]: e for e in m.edges}
    steps = [by_id[eid]["text"] for eid in path["edges"]]
    return f"From {m.nodes[path['entry']]['label']}: " + " → ".join(steps) + "."
