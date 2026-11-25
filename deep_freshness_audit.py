import urllib.request
import json
import time
import sys
import datetime
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

# 1. Fetch live API data from running daemon
try:
    req = urllib.request.urlopen('http://127.0.0.1:8080/api/graph', timeout=5)
    data = json.loads(req.read().decode('utf-8'))
except Exception as e:
    print(f"Error querying manifold API: {e}")
    sys.exit(1)

nodes = data.get('nodes', [])
links = data.get('links', [])
comms = data.get('communities', [])
clues = data.get('precursor_clues', [])
age_dist = data.get('age_distribution', {})
primary_driver = data.get('primary_driver', {})

print("="*75)
print("             SOVEREIGN MACRO MESH - FULL ECOSYSTEM AUDIT")
print("="*75)

print("\n--- SECTION 1: MANIFOLD SCALE & CONNECTIVITY ---")
print(f"Total Active Nodes: {len(nodes)}")
print(f"Total Topological Links: {len(links)}")
print(f"Average Node Connectivity (Degree): {len(links) * 2 / max(1, len(nodes)):.1f} links/node")
print(f"Total Discovered Communities: {len(comms)}")
print(f"Active Precursor Clues: {len(clues)}")

print("\n--- SECTION 2: TOPOLOGICAL AGE & FRESHNESS OF NODES IN RAM ---")
now = time.time()
node_ages = [n.get('age_seconds', 0) for n in nodes]
node_last_seen = [n.get('last_seen_seconds_ago', 0) for n in nodes]
if node_ages:
    print(f"Ingested In RAM: Min age: {min(node_ages):.1f}s | Median age: {sorted(node_ages)[len(node_ages)//2]/60:.1f}m | Max age: {max(node_ages)/60:.1f}m")
    print(f"Last Refreshed In RAM: Min: {min(node_last_seen):.1f}s ago | Max: {max(node_last_seen)/60:.1f}m ago")

regimes = Counter(n.get('freshness_regime') for n in nodes)
for r, cnt in regimes.items():
    print(f"  * {r}: {cnt} nodes ({cnt/len(nodes)*100:.1f}%)")

print("\n--- SECTION 3: REAL-WORLD DOCUMENT PUBLISH DATES AUDIT ---")
# Now let's audit the actual raw collector feeds: what dates are the external wires publishing?
print("Auditing raw collector feeds for real-world timestamps & lag...")

from topological_macro_mesh_v3.collectors.sovereign_wires import SovereignWiresCollector
from topological_macro_mesh_v3.collectors.geopolitical_wires import GeopoliticalWiresCollector
from topological_macro_mesh_v3.collectors.intermarket_flows import IntermarketFlowsCollector
from topological_macro_mesh_v3.collectors.crowd_divergence import CrowdDivergenceCollector

sov_col = SovereignWiresCollector()
geo_col = GeopoliticalWiresCollector()
flow_col = IntermarketFlowsCollector()
crowd_col = CrowdDivergenceCollector()

# Let's inspect raw documents from each collector
sov_docs = sov_col.fetch_wires()
geo_docs = geo_col.fetch_wires()
flow_docs = flow_col.fetch_flows()
crowd_docs = crowd_col.fetch_crowd_divergences()

all_raw = [
    ("SOVEREIGN CENTRAL BANKS & TREASURIES", sov_docs),
    ("GEOPOLITICAL & KINETIC CHOKEPOINTS", geo_docs),
    ("INTERMARKET FLOWS & YIELDS", flow_docs),
    ("CROWD ATTENTION DIVERGENCE", crowd_docs)
]

feed_timestamp_audit = []

for category_name, docs in all_raw:
    print(f"\n[{category_name}] Fetched: {len(docs)} documents")
    pub_times = []
    has_parseable_dates = 0
    today_count = 0
    past_24h_count = 0
    older_count = 0
    no_date_count = 0

    current_utc = datetime.datetime.now(datetime.timezone.utc)

    for d in docs:
        pub_raw = d.get("published", "")
        # Try parsing date
        parsed_dt = None
        if pub_raw:
            # Common RSS date formats
            import email.utils
            try:
                parsed_tuple = email.utils.parsedate_to_datetime(pub_raw)
                if parsed_tuple:
                    parsed_dt = parsed_tuple
            except Exception:
                try:
                    # ISO 8601
                    parsed_dt = datetime.datetime.fromisoformat(pub_raw.replace('Z', '+00:00'))
                except Exception:
                    pass

        if parsed_dt:
            has_parseable_dates += 1
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=datetime.timezone.utc)
            delta = current_utc - parsed_dt
            hours_old = delta.total_seconds() / 3600.0
            pub_times.append((hours_old, d.get("title", ""), d.get("publisher", "")))
            if hours_old <= 24:
                past_24h_count += 1
            else:
                older_count += 1
        else:
            no_date_count += 1

    print(f"  Parseable timestamps: {has_parseable_dates}/{len(docs)} (No explicit date: {no_date_count})")
    print(f"  Within last 24 Hours: {past_24h_count} ({(past_24h_count/max(1, has_parseable_dates))*100:.1f}% of dated)")
    print(f"  Older than 24 Hours:  {older_count} ({(older_count/max(1, has_parseable_dates))*100:.1f}% of dated)")

    if pub_times:
        pub_times.sort(key=lambda x: x[0])
        freshest = pub_times[0]
        oldest = pub_times[-1]
        median_hrs = pub_times[len(pub_times)//2][0]
        print(f"  Freshest Wire: {freshest[0]:.1f}h ago -> [{freshest[2]}] {freshest[1][:75]}...")
        print(f"  Median Wire Age: {median_hrs:.1f}h ago")
        print(f"  Oldest Retained in Feed: {oldest[0]/24:.1f} days ago -> [{oldest[2]}] {oldest[1][:75]}...")

print("\n--- SECTION 4: SPEED & EARLY CLUE EVALUATION (ARE CLUES FASTER?) ---")
# Check how fast the precursor clues are generated vs mainstream headline awareness
print("Evaluating Precursor Clue Engine Mechanics:")
print(f"1. Total Live Precursor Clues Generated: {len(clues)}")
for idx, c in enumerate(clues[:6]):
    print(f"   [{idx+1}] Phrase: '{c.get('phrase')}'")
    print(f"       Lifecycle Stage: {c.get('stage')}")
    print(f"       Hawkes Anomaly Badge: {c.get('hawkes_badge')}")
    print(f"       Lead Quality: {c.get('lead_badge')}")
    print(f"       Maturation Age: {c.get('maturation_minutes')} minutes")
    print(f"       Network Shock (Z-Score): +{c.get('z_score')}σ")
    print(f"       Newsrooms / Publishers: {c.get('publisher_count')} ({', '.join(c.get('publishers', [])[:3])})")
    print(f"       Headline: \"{c.get('sample_headline')[:85]}...\"")

print("\n--- SECTION 5: PRIMARY DRIVER DISCOVERY ---")
print(f"Active Primary Outlier: {primary_driver.get('active')}")
print(f"Clue Phrase: {primary_driver.get('clue_phrase')}")
print(f"Headline: {primary_driver.get('headline')}")
print(f"Z-Velocity: +{primary_driver.get('z_velocity')}σ | Sources: {primary_driver.get('source_count')}")

print("="*75)
