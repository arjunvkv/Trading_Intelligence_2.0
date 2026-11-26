"""
SOVEREIGN MACRO TOPOLOGICAL MESH V3 (APEX CAUSAL MANIFOLD)
Main Application & High-Velocity Decoupled Streaming Ingestion Daemon.
"""

import os
import sys
import time
import threading
import collections
import uvicorn
from typing import Dict, Any, List

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
        log("Initializing Sovereign Macro Topological Mesh V3 (Streaming Engine)...")
        self.manifold = TopologicalManifold()
        self.radar = SovereignRadar()
        
        self.sovereign_collector = SovereignWiresCollector()
        self.geopolitical_collector = GeopoliticalWiresCollector()
        self.intermarket_collector = IntermarketFlowsCollector()
        self.crowd_collector = CrowdDivergenceCollector()

        self.running = False
        self.document_queue = collections.deque(maxlen=10000)
        self.queue_lock = threading.Lock()
        
        self.latest_crowd_docs = []
        self.latest_health = None
        self.latest_graph_export = None
        self.export_lock = threading.Lock()

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

    def get_latest_graph_export(self) -> Dict[str, Any]:
        """Returns the pre-computed graph export in <1ms without locking API callers."""
        with self.export_lock:
            if self.latest_graph_export is not None:
                return self.latest_graph_export
        health = self.get_collector_health()
        return self.manifold.get_graph_export(radar=self.radar, collector_health=health)

    def start_ingestion_loop(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._run_pipeline, daemon=True)
        self.worker_thread.start()
        log("Ingestion background pipeline launched.")

    def _run_pipeline(self):
        # 1. Initial Bootstrap
        log("Executing bootstrap data ingestion...")
        self._initial_bootstrap()

        # 2. Worker 1: High-Velocity Stream Poller (Telegram, StockTwits, Mastodon, Breaking 1h) - every 8s
        t_fast = threading.Thread(target=self._fast_crowd_worker, daemon=True)
        t_fast.start()

        # 3. Worker 2: Sovereign & Kinetic Wire Poller (Central Banks, Conflict) - every 35s
        t_sov = threading.Thread(target=self._sovereign_worker, daemon=True)
        t_sov.start()

        # 4. Worker 3: Manifold Evolution Processor - every 4s continuous cycle
        t_evo = threading.Thread(target=self._evolution_worker, daemon=True)
        t_evo.start()

        log("Decoupled high-velocity streaming workers started successfully.")

    def _initial_bootstrap(self):
        start_time = time.time()
        sov_docs = self.sovereign_collector.fetch_wires()
        geo_docs = self.geopolitical_collector.fetch_wires()
        flow_docs = self.intermarket_collector.fetch_flows()
        crowd_docs = self.crowd_collector.fetch_crowd_divergences()

        all_docs = sov_docs + geo_docs + flow_docs + crowd_docs
        self.latest_crowd_docs = crowd_docs
        self.latest_health = self.get_collector_health()

        log(f"Bootstrap fetched {len(all_docs)} raw documents ({len(sov_docs)} sovereign, {len(geo_docs)} geopo, {len(flow_docs)} flow, {len(crowd_docs)} crowd).")
        self.manifold.ingest_batch(all_docs)
        self.manifold.update_topology()
        active_clues = self.radar.scan_manifold(
            nodes=self.manifold.nodes,
            cascades=self.manifold.active_cascades,
            crowd_divergences=crowd_docs
        )
        export = self.manifold.get_graph_export(radar=self.radar, collector_health=self.latest_health)
        with self.export_lock:
            self.latest_graph_export = export

        elapsed = time.time() - start_time
        log(
            f"Bootstrap completed in {elapsed:.2f}s | Nodes: {export['nodes_count']} | "
            f"Edges: {export['links_count']} | Communities: {export['communities_count']} | "
            f"Cascades: {export['cascades_count']} | Radar Clues: {len(active_clues)}"
        )

    def _fast_crowd_worker(self):
        while self.running:
            try:
                time.sleep(7.5)
                crowd_docs = self.crowd_collector.fetch_crowd_divergences()
                flow_docs = self.intermarket_collector.fetch_flows()
                new_pulses = crowd_docs + flow_docs
                self.latest_crowd_docs = crowd_docs
                if new_pulses:
                    with self.queue_lock:
                        self.document_queue.extend(new_pulses)
            except Exception as e:
                log(f"Fast crowd worker error: {e}")

    def _sovereign_worker(self):
        while self.running:
            try:
                time.sleep(35.0)
                sov_docs = self.sovereign_collector.fetch_wires()
                geo_docs = self.geopolitical_collector.fetch_wires()
                self.latest_health = self.get_collector_health()
                new_wires = sov_docs + geo_docs
                if new_wires:
                    with self.queue_lock:
                        self.document_queue.extend(new_wires)
            except Exception as e:
                log(f"Sovereign worker error: {e}")

    def _evolution_worker(self):
        while self.running:
            try:
                time.sleep(4.0)
                batch_docs = []
                with self.queue_lock:
                    while self.document_queue:
                        batch_docs.append(self.document_queue.popleft())

                t0 = time.time()
                if batch_docs:
                    self.manifold.ingest_batch(batch_docs)

                self.manifold.update_topology()
                active_clues = self.radar.scan_manifold(
                    nodes=self.manifold.nodes,
                    cascades=self.manifold.active_cascades,
                    crowd_divergences=self.latest_crowd_docs
                )
                health = self.latest_health or self.get_collector_health()
                export = self.manifold.get_graph_export(radar=self.radar, collector_health=health)
                with self.export_lock:
                    self.latest_graph_export = export

                t_diff = time.time() - t0
                if batch_docs:
                    age_dist = export.get('age_distribution', {})
                    living_core = age_dist.get('under_5m', 0) + age_dist.get('5m_to_15m', 0)
                    log(
                        f"⚡ Living Pulse: Ingested {len(batch_docs)} pulses in {t_diff:.2f}s | "
                        f"Nodes: {export['nodes_count']} | Edges: {export['links_count']} | "
                        f"Living Core (<15m): {living_core} | Clues: {len(active_clues)}"
                    )
            except Exception as e:
                log(f"Evolution worker error: {e}")

def main():
    daemon = SovereignMeshDaemon()
    daemon.start_ingestion_loop()

    app = create_app(
        manifold=daemon.manifold,
        radar=daemon.radar,
        intermarket_collector=daemon.intermarket_collector,
        health_provider=daemon.get_collector_health,
        graph_provider=daemon.get_latest_graph_export
    )

    port = int(os.environ.get("PORT", 8080))
    log(f"Starting API & Visualization Server on http://0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    main()
