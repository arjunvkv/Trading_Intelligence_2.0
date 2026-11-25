"""
SERVER APPLICATION (FASTAPI & STATIC ASSETS)
High-performance REST API and interactive D3 canvas mesh interface.
"""

import os
import time
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

def create_app(manifold, radar, intermarket_collector, health_provider: Optional[Callable[[], Dict[str, Any]]] = None) -> FastAPI:
    app = FastAPI(title="Sovereign Macro Topological Mesh V3", version="3.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    mesh_html_path = os.path.join(static_dir, "mesh.html")
    d3_js_path = os.path.join(static_dir, "d3.v7.min.js")

    def _serve_mesh():
        if os.path.exists(mesh_html_path):
            with open(mesh_html_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h3>Topological Mesh V3 running. static/mesh.html not found.</h3>"

    @app.get("/", response_class=HTMLResponse)
    def get_index():
        return _serve_mesh()

    @app.get("/mesh.html", response_class=HTMLResponse)
    def get_mesh():
        return _serve_mesh()

    @app.get("/d3.v7.min.js")
    def get_d3():
        if os.path.exists(d3_js_path):
            return FileResponse(d3_js_path, media_type="application/javascript")
        return Response(status_code=404)

    @app.get("/api/graph")
    def get_graph():
        health = health_provider() if health_provider else None
        return manifold.get_graph_export(radar=radar, collector_health=health)

    @app.get("/api/nodes")
    def get_nodes():
        health = health_provider() if health_provider else None
        data = manifold.get_graph_export(radar=radar, collector_health=health)
        nodes = data.get("nodes", [])
        sorted_nodes = sorted(nodes, key=lambda n: (n.get("centrality", 0.0), n.get("hawkes_lambda", 0.0)), reverse=True)
        return {
            "total_nodes": len(sorted_nodes),
            "nodes": sorted_nodes[:300]
        }

    @app.get("/api/telemetry")
    def get_telemetry():
        health = health_provider() if health_provider else None
        graph_data = manifold.get_graph_export(radar=radar, collector_health=health)
        market_telemetry = intermarket_collector.get_latest_telemetry()
        radar_telemetry = radar.get_summary_telemetry()
        
        communities = graph_data.get("communities", [])
        cascades = graph_data.get("cascades", [])

        # Calculate attention divergence from sovereign wire velocity vs crowd
        wire_z = [n["z_score"] for n in graph_data.get("nodes", []) if n.get("category") != "CROWD_DIVERGENCE"]
        crowd_z = [n["z_score"] for n in graph_data.get("nodes", []) if n.get("category") == "CROWD_DIVERGENCE"]
        avg_wire = sum(wire_z) / max(1, len(wire_z)) if wire_z else 0.0
        avg_crowd = sum(crowd_z) / max(1, len(crowd_z)) if crowd_z else 0.0
        delta = round(avg_wire - avg_crowd, 2)
        lead_quality = "ASYMMETRIC LEAD" if delta >= 1.0 else ("BALANCED" if delta >= -0.5 else "CROWD SPECULATION")

        return {
            "timestamp": time.time(),
            "nodes_count": graph_data.get("nodes_count", 0),
            "links_count": graph_data.get("links_count", 0),
            "communities_count": graph_data.get("communities_count", 0),
            "active_cascades_count": len(cascades),
            "cascades": cascades[:10],
            "communities": communities,
            "radar_clues": radar_telemetry,
            "intermarket_flows": market_telemetry,
            "collector_health": health,
            "attention_divergence": {
                "divergence_delta": delta,
                "lead_quality": lead_quality,
                "wire_velocity_z": round(avg_wire, 2),
                "crowd_velocity_z": round(avg_crowd, 2)
            },
            "latest_decision": {
                "decision": "STAND_DOWN",
                "reason": "Sovereign macroeconomic equilibrium; awaiting high-conviction transmission gate"
            }
        }

    @app.get("/api/health")
    def get_health():
        health = health_provider() if health_provider else {}
        return {
            "status": "HEALTHY",
            "version": "3.0.0-apex",
            "nodes": len(manifold.nodes),
            "edges": len(manifold.edge_weights),
            "collector_health": health,
            "timestamp": time.time()
        }

    return app
