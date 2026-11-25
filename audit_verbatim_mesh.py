import urllib.request
import json
import time
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

print("Waiting for Sovereign Mesh to ingest feeds and populate manifold...")
for attempt in range(30):
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8080/api/graph", timeout=5)
        data = json.loads(req.read().decode('utf-8'))
        nodes = data.get("nodes", [])
        if len(nodes) >= 50:
            print(f"Manifold populated with {len(nodes)} nodes and {len(data.get('links', []))} links!")
            break
        else:
            print(f"Ingesting... currently {len(nodes)} nodes (attempt {attempt+1}/30)")
    except Exception as e:
        print(f"Waiting for endpoint... ({e})")
    time.sleep(4)
else:
    print("Timeout waiting for nodes.")
    sys.exit(1)

# Now perform verbatim and wire dossier audit
req = urllib.request.urlopen("http://127.0.0.1:8080/api/graph", timeout=5)
data = json.loads(req.read().decode('utf-8'))
nodes = data.get("nodes", [])
links = data.get("links", [])

verbatim_counter = Counter()
nodes_with_history = 0
total_dossier_wires = 0
canonical_checks = ["imf", "international monetary fund", "ecb", "european central bank", "pboc", "people's bank of china"]
found_entities = {}

for n in nodes:
    txt = n.get("trigger_text") or "(No headline)"
    verbatim_counter[txt] += 1
    dossier = n.get("wire_history", []) or n.get("wire_dossier", [])
    if dossier:
        nodes_with_history += 1
        total_dossier_wires += len(dossier)
    nid = n.get("id", "").lower()
    for c in canonical_checks:
        if c in nid:
            found_entities[c] = n.get("id")

unique_verbatims = len(verbatim_counter)
total_nodes = len(nodes)
dup_nodes = sum(cnt for headline, cnt in verbatim_counter.items() if cnt > 1)
single_wire_nodes = sum(1 for headline, cnt in verbatim_counter.items() if cnt == 1)

print("\n" + "="*70)
print("--- SOVEREIGN MACRO MESH VERBATIM AUDIT REPORT ---")
print("="*70)
print(f"Total Active Nodes: {total_nodes}")
print(f"Total Structural Links: {len(links)}")
print(f"Unique Verbatim Headlines: {unique_verbatims}")
print(f"Uniqueness Ratio: {unique_verbatims / max(total_nodes, 1) * 100:.1f}%")
print(f"Nodes with strictly unique headline: {single_wire_nodes}")
print(f"Nodes with Corroborating Wire Dossiers: {nodes_with_history} / {total_nodes}")
print(f"Total Deep Corroborating Wires Stored: {total_dossier_wires}")
print(f"Average Wires per Node Buffer: {total_dossier_wires / max(nodes_with_history, 1):.2f}")

print("\n--- TOP 5 MOST ASSIGNED HEADLINES (Bipartite Distribution) ---")
for headline, count in verbatim_counter.most_common(5):
    print(f"[{count} nodes] -> {headline[:90]}...")

print("\n--- SAMPLE NODE DOSSIER EXPORTS ---")
sample_nodes = [n for n in nodes if (n.get("wire_history") or n.get("wire_dossier")) and len(n.get("wire_history", []) or n.get("wire_dossier", [])) > 1][:4]
for sn in sample_nodes:
    hist = sn.get("wire_history", []) or sn.get("wire_dossier", [])
    print(f"\nNode: [{sn.get('id')}] (Cluster: {sn.get('community_name', 'Unknown')})")
    print(f"  Primary Verbatim: {sn.get('trigger_text')}")
    print(f"  Wire Dossier ({len(hist)} corroborating streams):")
    for w in hist[:3]:
        print(f"    - [{w.get('publisher', 'WIRE')}] {w.get('title', '')[:85]}... ({w.get('age_str', '')})")

print("\n--- CANONICAL ALIAS RESOLUTION CHECK ---")
for c, eid in found_entities.items():
    print(f"Alias query '{c}' -> Resolved Node: '{eid}'")

print("="*70)
