"""
SERVER & ORCHESTRATOR MODULE (100% GROUND TRUTH)
Coordinates:
1. Periodic ingestion of real-world wires, unseeded trends, and dynamic verification via collectors.py
2. Zero-fake-edge topological math via topology.py with graph reachability and noise purging
3. Honest market physics, session conductivity & Attention Divergence via lead_arbiter.py
4. Dual-Key Trade Arbiter & Telegram Alert Dispatcher via trade_arbiter.py
5. Lightweight local HTTP server serving the visual constellation mesh at http://localhost:8080
"""

import http.server
import socketserver
import threading
import time
import json
import os
from collectors import DataCollector
from topology import TopologyEngine
from lead_arbiter import LeadArbiter

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class EngineService:
    def __init__(self):
        self.collector = DataCollector()
        self.topology = TopologyEngine()
        self.arbiter = LeadArbiter()
        self.is_running = True
        self.latest_graph = {}
        cache_file = os.path.join(BASE_DIR, "live_graph.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.latest_graph = json.load(f)
            except Exception:
                pass
        self.latest_decision = {"decision": "INITIALIZING", "reason": "Engine starting up"}

    def cycle(self):
        """Single discovery, topology update, and Dual-Key arbiter cycle with 100% genuine data."""
        try:
            # 1. Fetch real unmanipulated streams with dynamic closed-loop steering from graph
            dynamic_seeds = self.topology.get_surging_entities(top_k=5)
            dynamic_search = "+OR+".join(dynamic_seeds[:4]) if dynamic_seeds else None
            snapshot = self.collector.fetch_all(dynamic_seeds=dynamic_seeds, dynamic_search_query=dynamic_search)
            
            # 2. Ingest into topology (True multi-source provenance: Wires vs Crowd)
            self.topology.ingest_stream_items(snapshot.get("sovereign_wires", []), is_crowd=False)
            self.topology.ingest_stream_items(snapshot.get("geopolitical_wires", []), is_crowd=False)
            self.topology.ingest_stream_items(snapshot.get("market_wires", []), is_crowd=False)
            self.topology.ingest_stream_items(snapshot.get("crowd_discussions", []), is_crowd=True)

            # 3. Export latest graph (runs mathematical prune & orphan cull)
            self.latest_graph = self.topology.export_graph_json()
            self.latest_graph["collector_health"] = snapshot.get("collector_health", {})
            
            # 4. Compute Attention Divergence (Strict Mathematical Provenance: Wires vs Crowd)
            wire_z = [n["z_score"] for n in self.latest_graph.get("nodes", []) if not n.get("is_crowd") and not n.get("is_god")]
            crowd_z = [n["z_score"] for n in self.latest_graph.get("nodes", []) if n.get("is_crowd") and not n.get("is_god")]
            att_div = self.arbiter.calculate_attention_divergence(wire_z, crowd_z)

            self.latest_decision = {
                "status": "MACRO_INTELLIGENCE_ACTIVE",
                "attention_regime": att_div.get("attention_regime", "STRUCTURAL_EQUILIBRIUM"),
                "lead_quality": att_div.get("lead_quality", "NEUTRAL"),
                "wire_velocity_z": att_div.get("wire_velocity_z", 0.0),
                "crowd_velocity_z": att_div.get("crowd_velocity_z", 0.0),
                "divergence_delta": att_div.get("divergence_delta", 0.0)
            }

            # Save state to local file
            with open(os.path.join(BASE_DIR, "live_graph.json"), "w", encoding="utf-8") as f:
                json.dump(self.latest_graph, f, indent=2)

        except Exception as e:
            print("Error in Engine cycle:", e)

    def run_loop(self):
        print("Kinetic Discovery Engine started.")
        while self.is_running:
            self.cycle()
            time.sleep(35) # rapid 35-second rolling refresh

engine_service = EngineService()

def get_api_catalog(base_url: str) -> dict:
    return {
        "title": "XAUUSD Sovereign Macro Intelligence & Topological Constellation Mesh API",
        "version": "2.0.0-PROVENANCE",
        "description": "Autonomous, zero-AI, zero-hardcode macro intelligence engine for Gold (XAUUSD). Discovers real-world breaking precursor clues across global fronts/theaters before mainstream headlines, with 100% ground-truth provenance and invalidation off-ramps.",
        "server_status": "ONLINE",
        "cycle_interval_seconds": 35,
        "base_url": base_url,
        "endpoints": [
            {
                "path": "/api",
                "aliases": ["/api/index", "/api/docs", "/api/help"],
                "method": "GET",
                "name": "API Master Index & Documentation",
                "description": "Returns the complete master index of all endpoints, parameters, schemas, and usage examples.",
                "example_url": f"{base_url}/api",
                "curl_example": f"curl -k -s {base_url}/api"
            },
            {
                "path": "/api/nodes",
                "method": "GET",
                "name": "Single Nodes Granular Stream",
                "description": "Stream of all individual entity nodes in the global graph with entity ID, burst Z-score, degree, hops to Gold (XAUUSD), verbatim wire headline, full publisher provenance list, age, and 1-click Google/X verification links.",
                "parameters": {
                    "sort": "Sort field: 'z' (highest burst velocity), 'fresh' (newest arrival), 'hops' (closest geodesic distance to Gold), 'publishers' (most newsrooms reporting). Default: 'z'.",
                    "min_z": "Filter nodes with minimum Poisson arrival Z-score (e.g. min_z=2.5).",
                    "q": "Search keyword or entity across IDs, labels, and verbatim headlines (e.g. q=dollar, q=iran, q=fed).",
                    "limit": "Maximum number of nodes to return (e.g. limit=25)."
                },
                "example_url": f"{base_url}/api/nodes?sort=z&limit=10",
                "curl_example": f"curl -k -s '{base_url}/api/nodes?sort=z&limit=10'"
            },
            {
                "path": "/api/graph",
                "method": "GET",
                "name": "Full Graph Topology & Precursor Constellations",
                "description": "Complete topological manifold containing all nodes, co-occurrence/transfer-entropy links, multi-front emerging clue constellations with maturation stages and off-ramps, dominant primary market driver, and age distribution.",
                "parameters": {},
                "example_url": f"{base_url}/api/graph",
                "curl_example": f"curl -k -s {base_url}/api/graph"
            },
            {
                "path": "/api/telemetry",
                "method": "GET",
                "name": "Attention Divergence & Lead Physics",
                "description": "Calculates Attention Divergence between institutional wire velocity (Key 1) and public search/squawk queries (Key 2), determining if smart money is accumulating ahead of public awareness.",
                "parameters": {
                    "cluster": "Realm cluster name (default: 'Sovereign & Central Banks')",
                    "z": "Surge outlier threshold (default: 3.0)",
                    "hops": "Geodesic hops to Gold (default: 2)"
                },
                "example_url": f"{base_url}/api/telemetry?cluster=Sovereign+%26+Central+Banks&z=3.5&hops=1",
                "curl_example": f"curl -k -s '{base_url}/api/telemetry?cluster=Sovereign+%26+Central+Banks&z=3.5&hops=1'"
            },
            {
                "path": "/api/health",
                "method": "GET",
                "name": "Collector Health & Diagnostics",
                "description": "Real-time health status of all 22 live feeds (sovereign banks, geopolitical wires, intermarket tickers, crowd squawks). Reports domain backoff, latencies, cooldown counters, and HTTP statuses.",
                "parameters": {},
                "example_url": f"{base_url}/api/health",
                "curl_example": f"curl -k -s {base_url}/api/health"
            },
            {
                "path": "/mesh.html",
                "method": "GET",
                "name": "Interactive Living Mesh Canvas UI",
                "description": "Full interactive browser visualization with D3 topological force graph, emergent community trays, multi-front precursor clue radar, and node inspector drawer.",
                "parameters": {},
                "example_url": f"{base_url}/mesh.html"
            }
        ],
        "provenance_rules": {
            "zero_ai_loop": "Pure information geometry, Poisson arrival burst calculations, and graph modularity. Zero LLM hallucinations in the mathematical pipeline.",
            "anti_echo_rule": "Bursts strictly require multi-source corroboration from >= 2 independent primary newsrooms (not syndication mirrors).",
            "distinct_event_dedup": "Entities across headlines are deduplicated so every card represents an independent global front/theater.",
            "off_ramp_rule": "Every precursor clue constellation has an explicit maturation timer and invalidation off-ramp (decays naturally if unconfirmed within 15 minutes)."
        }
    }

def get_openapi_spec(base_url: str) -> dict:
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "XAUUSD Macro Intelligence Precursor Engine API",
            "version": "2.0.0",
            "description": "Zero-AI, zero-hardcode macro intelligence engine discovering real-world precursor clues for Gold (XAUUSD)."
        },
        "servers": [{"url": base_url}],
        "paths": {
            "/api": {
                "get": {
                    "summary": "Master API Index & Schema Catalog",
                    "responses": {"200": {"description": "Full API Catalog"}}
                }
            },
            "/api/nodes": {
                "get": {
                    "summary": "Stream of all individual entity nodes in the world",
                    "parameters": [
                        {"name": "sort", "in": "query", "schema": {"type": "string"}, "description": "Sort by 'z', 'fresh', 'hops', 'publishers'"},
                        {"name": "min_z", "in": "query", "schema": {"type": "number"}, "description": "Filter by minimum Z-score (e.g. 2.5)"},
                        {"name": "q", "in": "query", "schema": {"type": "string"}, "description": "Search keyword or entity"},
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}, "description": "Max items to return"}
                    ],
                    "responses": {"200": {"description": "List of single entity nodes"}}
                }
            },
            "/api/graph": {
                "get": {
                    "summary": "Full topological manifold and precursor constellations",
                    "responses": {"200": {"description": "Graph topology and multi-front constellations"}}
                }
            },
            "/api/telemetry": {
                "get": {
                    "summary": "Attention Divergence & Lead Physics",
                    "responses": {"200": {"description": "Attention divergence telemetry"}}
                }
            },
            "/api/health": {
                "get": {
                    "summary": "Collector health status for all 22 live feeds",
                    "responses": {"200": {"description": "Diagnostic health state"}}
                }
            }
        }
    }

class MeshHTTPHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json(self, data, status=200, compact=True):
        if compact:
            body = json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def _send_text(self, text, content_type='text/plain; charset=utf-8', status=200):
        body = text.encode('utf-8') if isinstance(text, str) else text
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_HEAD(self):
        clean_path = self.path.split('?')[0].rstrip('/')
        if clean_path in ['', '/']:
            self.send_response(302)
            self.send_header('Location', '/mesh.html')
            self.end_headers()
            return
        self.send_response(200)
        if clean_path.startswith('/api') or clean_path in ['/openapi.json', '/openapi.yaml']:
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        elif clean_path.endswith('.html'):
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        elif clean_path == '/robots.txt':
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        host = self.headers.get('Host', f'localhost:{PORT}')
        proto = "https" if ("trycloudflare" in host or "lhr.life" in host or "ts.net" in host or self.headers.get('X-Forwarded-Proto') == 'https') else "http"
        base_url = f"{proto}://{host}"
        ua = self.headers.get('User-Agent', 'Unknown')
        print(f"[{time.strftime('%X')}] GET {self.path} | Host: {host} | UA: {ua[:40]}")

        clean_path = self.path.split('?')[0].rstrip('/')
        if clean_path in ['', '/']:
            self.send_response(302)
            self.send_header('Location', '/mesh.html')
            self.end_headers()
            return
        elif clean_path == '/robots.txt':
            self._send_text("User-agent: *\nAllow: /\n")
            return
        elif clean_path == '/sitemap.xml':
            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{base_url}/api</loc></url>
  <url><loc>{base_url}/api/nodes</loc></url>
  <url><loc>{base_url}/api/graph</loc></url>
  <url><loc>{base_url}/api/telemetry</loc></url>
  <url><loc>{base_url}/api/health</loc></url>
  <url><loc>{base_url}/mesh.html</loc></url>
</urlset>"""
            self._send_text(xml, content_type='application/xml; charset=utf-8')
            return
        elif clean_path == '/favicon.ico':
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            return
        elif clean_path in ['/openapi.json', '/openapi.yaml']:
            spec = get_openapi_spec(base_url)
            self._send_json(spec)
            return
        elif clean_path in ['/api', '/api/index', '/api/docs', '/api/help']:
            catalog = get_api_catalog(base_url)
            self._send_json(catalog)
            return
        elif clean_path == '/mesh.html':
            mesh_file = os.path.join(BASE_DIR, "mesh.html")
            if os.path.exists(mesh_file):
                with open(mesh_file, "rb") as f:
                    content = f.read()
                self._send_text(content, content_type='text/html; charset=utf-8')
                return
        elif clean_path == '/d3.v7.min.js':
            d3_file = os.path.join(BASE_DIR, "d3.v7.min.js")
            if os.path.exists(d3_file):
                with open(d3_file, "rb") as f:
                    content = f.read()
                self._send_text(content, content_type='application/javascript; charset=utf-8')
                return
        elif clean_path == '/api/graph':
            payload = dict(engine_service.latest_graph)
            payload["api_index_url"] = f"{base_url}/api"
            payload["all_nodes_url"] = f"{base_url}/api/nodes"
            payload["visual_mesh_url"] = f"{base_url}/mesh.html"
            self._send_json(payload)
            return
        elif clean_path == '/api/nodes':
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            all_nodes = list(engine_service.latest_graph.get("nodes", []))

            # Optional node ID filter via query param (?id=why)
            id_filter = query.get('id', [''])[0].lower().strip()
            if id_filter:
                node_match = next((n for n in all_nodes if n.get('id', '').lower() == id_filter), None)
                if node_match:
                    self._send_json({"node": node_match, "api_index_url": f"{base_url}/api"})
                    return

            # Optional search filter
            q_search = query.get('q', [''])[0].lower().strip()
            if q_search:
                all_nodes = [n for n in all_nodes if q_search in n.get('id', '').lower() or q_search in n.get('trigger_text', '').lower() or q_search in n.get('label', '').lower()]

            # Optional min_z filter
            min_z = float(query.get('min_z', [0.0])[0])
            if min_z > 0:
                all_nodes = [n for n in all_nodes if n.get('z_score', 0) >= min_z]

            # Optional sorting
            sort_by = query.get('sort', ['z'])[0]
            if sort_by == 'z':
                all_nodes.sort(key=lambda n: n.get('z_score', 0), reverse=True)
            elif sort_by == 'fresh':
                all_nodes.sort(key=lambda n: n.get('age_seconds', 999999))
            elif sort_by == 'hops':
                all_nodes.sort(key=lambda n: n.get('hops_to_xau', 999))
            elif sort_by == 'publishers':
                all_nodes.sort(key=lambda n: n.get('publisher_count', 0), reverse=True)

            # Optional limit (default to 50 if unspecified so web crawlers and ChatGPT don't choke on 500KB)
            total_matching = len(all_nodes)
            limit_val = 50
            if 'limit' in query:
                l_str = query['limit'][0].lower()
                if l_str in ['all', 'max', '0']:
                    limit_val = total_matching
                else:
                    limit_val = int(l_str)
            all_nodes = all_nodes[:limit_val]

            res_payload = {
                "timestamp": engine_service.latest_graph.get("timestamp", time.time()),
                "returned_nodes": len(all_nodes),
                "total_matching_nodes": total_matching,
                "api_index_url": f"{base_url}/api",
                "graph_url": f"{base_url}/api/graph",
                "visual_mesh_url": f"{base_url}/mesh.html",
                "nodes": all_nodes
            }
            self._send_json(res_payload)
            return
        elif clean_path == '/api/health':
            self._send_json(engine_service.collector.get_health_status())
            return
        elif clean_path.startswith('/api/telemetry'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            cluster = query.get('cluster', ['Sovereign & Central Banks'])[0]
            z = float(query.get('z', [3.0])[0])
            hops = int(query.get('hops', [2])[0])

            nodes = engine_service.latest_graph.get("nodes", [])
            wire_z = [n["z_score"] for n in nodes if not n.get("is_crowd") and not n.get("is_god")]
            crowd_z = [n["z_score"] for n in nodes if n.get("is_crowd") and not n.get("is_god")]

            res = engine_service.arbiter.evaluate_shock_telemetry(cluster, z, hops, wire_z, crowd_z)
            res["latest_decision"] = engine_service.latest_decision
            self._send_json(res)
            return
        return super().do_GET()

def start_server():
    # Start background ingestion loop in thread (runs cycle immediately and every 35s)
    t = threading.Thread(target=engine_service.run_loop, daemon=True)
    t.start()

    # Start multi-threaded HTTP server so concurrent requests and browser polling never block
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    http.server.ThreadingHTTPServer.daemon_threads = True
    while True:
        try:
            with http.server.ThreadingHTTPServer(("", PORT), MeshHTTPHandler) as httpd:
                print(f"Living Mesh UI Server running at http://localhost:{PORT}/mesh.html (Multi-Threaded)")
                httpd.serve_forever()
        except Exception as e:
            print(f"[SERVER EXCEPTION] {e}, restarting in 2 seconds...")
            time.sleep(2)

if __name__ == "__main__":
    start_server()
