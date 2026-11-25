"""
SERVER APPLICATION (FASTAPI & STATIC ASSETS)
High-performance REST API and interactive D3 canvas mesh interface.
"""

import os
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

def create_app(manifold, radar, intermarket_collector) -> FastAPI:
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

    @app.get("/", response_class=HTMLResponse)
    def get_index():
        if os.path.exists(mesh_html_path):
            with open(mesh_html_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h3>Topological Mesh V3 running. static/mesh.html not found.</h3>"

    @app.get("/d3.v7.min.js")
    def get_d3():
        if os.path.exists(d3_js_path):
            return FileResponse(d3_js_path, media_type="application/javascript")
        return Response(status_code=404)

    @app.get("/api/graph")
    def get_graph():
        return manifold.get_graph_export()

    @app.get("/api/nodes")
    def get_nodes():
        data = manifold.get_graph_export()
        nodes = data.get("nodes", [])
        # Return sorted by centrality and Hawkes intensity
        sorted_nodes = sorted(nodes, key=lambda n: (n.get("centrality", 0.0), n.get("hawkes_lambda", 0.0)), reverse=True)
        return {
            "total_nodes": len(sorted_nodes),
            "nodes": sorted_nodes[:200]
        }

    @app.get("/api/telemetry")
    def get_telemetry():
        graph_data = manifold.get_graph_export()
        market_telemetry = intermarket_collector.get_latest_telemetry()
        radar_telemetry = radar.get_summary_telemetry()
        
        # Emerging clusters
        communities = graph_data.get("communities", {})
        cascades = graph_data.get("cascades", [])

        return {
            "timestamp": time.time(),
            "nodes_count": graph_data.get("nodes_count", 0),
            "links_count": graph_data.get("links_count", 0),
            "communities_count": graph_data.get("communities_count", 0),
            "active_cascades_count": len(cascades),
            "cascades": cascades[:10],
            "communities": communities,
            "radar_clues": radar_telemetry,
            "intermarket_flows": market_telemetry
        }

    @app.get("/api/health")
    def get_health():
        return {
            "status": "HEALTHY",
            "version": "3.0.0-apex",
            "nodes": len(manifold.nodes),
            "edges": len(manifold.edge_weights),
            "timestamp": time.time()
        }

    return app
