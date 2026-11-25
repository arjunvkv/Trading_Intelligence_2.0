import urllib.request
import json
from collections import Counter

resp = urllib.request.urlopen("http://localhost:8080/api/graph", timeout=10)
data = json.loads(resp.read())

nodes = data.get("nodes", [])
links = data.get("links", [])
communities = data.get("communities", [])
clues = data.get("precursor_clues", [])
driver = data.get("primary_driver", {})

print(f"=== LIVE MANIFOLD AUDIT SNAPSHOT ===")
print(f"Total Nodes: {len(nodes)}")
print(f"Total Links: {len(links)}")
print(f"Total Communities: {len(communities)}")
print(f"Total Precursor Clues: {len(clues)}")
print(f"Primary Driver: {driver.get('headline')}")

# Category breakdown
categories = Counter(n.get("category", "UNKNOWN") for n in nodes)
print("\n--- Node Category Distribution ---")
for cat, count in categories.most_common():
    print(f"  • {cat}: {count} ({count/len(nodes)*100:.1f}%)")

# Freshness Distribution
ages = Counter(n.get("freshness_regime", "UNKNOWN") for n in nodes)
print("\n--- Freshness Distribution ---")
for age, count in ages.most_common():
    print(f"  • {age}: {count} ({count/len(nodes)*100:.1f}%)")

# Top 25 Central Entities
print("\n--- Top 25 Central Entities (Degree & Z-Score) ---")
sorted_nodes = sorted(nodes, key=lambda x: (x.get("degree", 0), x.get("z_score", 0)), reverse=True)
for n in sorted_nodes[:25]:
    c_name = n.get("community_name", "")[:35]
    print(f"  • {n['label']} [{n.get('category')}] - Deg: {n.get('degree')}, Z: {n.get('z_score')}, C#{n.get('cluster')} ({c_name})")

# Precursor Clue Stages
print("\n--- Precursor Clues Audit ---")
for c in clues[:12]:
    print(f"  [{c.get('stage')}] {c.get('title')} | Hawkes: {c.get('hawkes_badge')} | Maturation: {c.get('maturation_minutes')}m | Pubs: {c.get('publisher_count')}")

# Sample Verbatim Headlines
print("\n--- Sample Verbatim Headlines Ingested ---")
for n in sorted_nodes[:15]:
    hl = n.get("trigger_text", "")
    src = n.get("trigger_source", "Unknown")
    safe_hl = hl.encode('ascii', 'replace').decode()
    safe_lbl = n['label'].encode('ascii', 'replace').decode()
    print(f"  * [{safe_lbl}] ({src}):\n    \"{safe_hl}\"\n")

