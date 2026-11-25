"""
SOVEREIGN MACRO TOPOLOGICAL MESH V3 (APEX CAUSAL MANIFOLD)
Main Application & Live Ingestion Daemon.
"""

import os
import sys
import time
import threading
import uvicorn
from typing import Dict, Any

from topological_macro_mesh_v3.collectors import (
    SovereignWiresCollector,
    GeopoliticalWiresCollector,
    IntermarketFlowsCollector,
    CrowdDivergenceCollector
)
from topological_macro_mesh_v3.engine import (
    TopologicalManifold,
    SovereignRadar
)
from topological_macro_mesh_v3.server.app import create_app

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    safe_msg = f"[{timestamp} UTC] {msg}".encode("ascii", "replace").decode()
    print(safe_msg, flush=True)

class SovereignMeshDaemon:
    def __init__(self):
        log("Initializing Sovereign Macro Topological Mesh V3...")
        self.manifold = TopologicalManifold()
        self.radar = SovereignRadar()
        
        self.sovereign_collector = SovereignWiresCollector()
        self.geopolitical_collector = GeopoliticalWiresCollector()
        self.intermarket_collector = IntermarketFlowsCollector()
        self.crowd_collector = CrowdDivergenceCollector()

        self.running = False
        self.worker_thread = None

    def get_collector_health(self) -> Dict[str, Any]:
        """Aggregates real-time collector states for UI diagnostics."""
        sov = self.sovereign_collector.get_health_states()
        geo = self.geopolitical_collector.get_health_states()
        states = sov.get("states", []) + geo.get("states", [])
        active_errs = [s for s in states if s["status"] != "HEALTHY"]
        return {
            "healthy_count": sov.get("healthy_count", 0) + geo.get("healthy_count", 0),
            "total_count": sov.get("total_count", 0) + geo.get("total_count", 0),
            "all_healthy": len(active_errs) == 0,
            "active_errors": active_errs,
            "states": states
        }

    def start_ingestion_loop(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()
        log("Ingestion worker thread started.")

    def _run_loop(self):
        # Initial bootstrap
        log("Executing bootstrap data ingestion...")
        self._ingest_cycle()

        while self.running:
            try:
                time.sleep(35.0)
                self._ingest_cycle()
            except Exception as e:
                log(f"Error in ingestion cycle: {e}")

    def _ingest_cycle(self):
        start_time = time.time()
        
        # 1. Fetch live sovereign wires (expanded 18 global central bank & debt feeds)
        sovereign_docs = self.sovereign_collector.fetch_wires()
        # 2. Fetch live geopolitical kinetic wires (expanded 11 conflict & chokepoint feeds)
        geopolitical_docs = self.geopolitical_collector.fetch_wires()
        # 3. Fetch intermarket flow pulses
        intermarket_docs = self.intermarket_collector.fetch_flows()
        # 4. Fetch crowd attention divergences
        crowd_docs = self.crowd_collector.fetch_crowd_divergences()

        all_docs = sovereign_docs + geopolitical_docs + intermarket_docs + crowd_docs
        log(f"Fetched {len(all_docs)} raw documents ({len(sovereign_docs)} sovereign, {len(geopolitical_docs)} geopo, {len(intermarket_docs)} flow, {len(crowd_docs)} crowd).")

        # Ingest into manifold using high-speed parallel batching
        accepted = self.manifold.ingest_batch(all_docs)

        # Update topology: decay, Hawkes processes, community detection, Transfer Entropy
        self.manifold.update_topology()

        # Update radar clues
        active_clues = self.radar.scan_manifold(
            nodes=self.manifold.nodes,
            cascades=self.manifold.active_cascades,
            crowd_divergences=crowd_docs
        )

        elapsed = time.time() - start_time
        health = self.get_collector_health()
        graph_export = self.manifold.get_graph_export(radar=self.radar, collector_health=health)
        log(
            f"Cycle completed in {elapsed:.2f}s | Nodes: {graph_export['nodes_count']} | "
            f"Edges: {graph_export['links_count']} | Communities: {graph_export['communities_count']} | "
            f"Cascades: {graph_export['cascades_count']} | Radar Clues: {len(active_clues)} | "
            f"Feeds Healthy: {health['healthy_count']}/{health['total_count']}"
        )

def main():
    daemon = SovereignMeshDaemon()
    daemon.start_ingestion_loop()

    app = create_app(
        manifold=daemon.manifold,
        radar=daemon.radar,
        intermarket_collector=daemon.intermarket_collector,
        health_provider=daemon.get_collector_health
    )

    port = int(os.environ.get("PORT", 8080))
    log(f"Starting API & Visualization Server on http://0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    main()
