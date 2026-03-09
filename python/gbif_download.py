"""
GBIF Fungal Occurrence Data Download
Query GBIF for all fungal records in Leeds bounding box (2000-2025)
"""

import pandas as pd
from pygbif import occurrences as occ
from pygbif import species
import time
import json

# Leeds bounding box (same as brownfield filter)
LEEDS_BBOX = {
    'decimalLatitude': '53.7,53.9',
    'decimalLongitude': '-1.8,-1.3'
}

# Date range
YEAR_START = 2000
YEAR_END = 2025

# GBIF kingdom code for Fungi
FUNGI_KINGDOM_KEY = 5  # Fungi kingdom in GBIF taxonomy

print("=" * 60)
print("GBIF Fungal Occurrence Download - Leeds")
print("=" * 60)

# Query GBIF for fungal records
print(f"\nQuerying GBIF for fungi in Leeds ({YEAR_START}-{YEAR_END})...")
print(f"Bounding box: {LEEDS_BBOX}")

# First, get a count
search_params = {
    'kingdomKey': FUNGI_KINGDOM_KEY,
    'decimalLatitude': LEEDS_BBOX['decimalLatitude'],
    'decimalLongitude': LEEDS_BBOX['decimalLongitude'],
    'year': f"{YEAR_START},{YEAR_END}",
    'hasCoordinate': True,
    'hasGeospatialIssue': False,
    'limit': 0  # Just get count
}

result = occ.search(**search_params)
total_records = result['count']

print(f"\nTotal fungal records found: {total_records:,}")

if total_records == 0:
    print("No records found. Exiting.")
    exit()

# Download records in batches (GBIF limit: 300 per request)
BATCH_SIZE = 300
all_records = []

print(f"\nDownloading in batches of {BATCH_SIZE}...")

for offset in range(0, min(total_records, 10000), BATCH_SIZE):  # Cap at 10,000 for now
    print(f"  Batch {offset//BATCH_SIZE + 1}: offset {offset}...", end='')
    
    search_params['limit'] = BATCH_SIZE
    search_params['offset'] = offset
    
    try:
        batch = occ.search(**search_params)
        
        if 'results' in batch and batch['results']:
            all_records.extend(batch['results'])
            print(f" {len(batch['results'])} records")
        else:
            print(" No results")
            break
            
    except Exception as e:
        print(f" Error: {e}")
        break
    
    # Be nice to GBIF servers
    time.sleep(0.5)

print(f"\nTotal records downloaded: {len(all_records):,}")

# Convert to DataFrame
df = pd.DataFrame(all_records)

print(f"\nDataFrame shape: {df.shape}")
print(f"Columns: {len(df.columns)}")

# Extract key fields
key_fields = [
    'gbifID',
    'scientificName',
    'species',
    'genus',
    'family',
    'order',
    'decimalLatitude',
    'decimalLongitude',
    'year',
    'month',
    'day',
    'eventDate',
    'recordedBy',
    'basisOfRecord',
    'occurrenceStatus',
    'coordinateUncertaintyInMeters'
]

# Keep only fields that exist
available_fields = [f for f in key_fields if f in df.columns]
df_filtered = df[available_fields].copy()

print(f"\nFiltered to {len(available_fields)} key fields")
print("\nSample records:")
print(df_filtered.head(10))

# Save raw data
output_file = '../data/gbif/leeds_fungi_raw.csv'
df_filtered.to_csv(output_file, index=False)
print(f"\nSaved to: {output_file}")

# Summary statistics
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total records: {len(df_filtered):,}")
print(f"Unique species: {df_filtered['scientificName'].nunique():,}")
print(f"Year range: {df_filtered['year'].min():.0f} - {df_filtered['year'].max():.0f}")
print(f"Coordinate uncertainty (median): {df_filtered['coordinateUncertaintyInMeters'].median():.0f}m")

print("\nTop 10 most recorded species:")
print(df_filtered['scientificName'].value_counts().head(10))

print("\nRecords by year:")
print(df_filtered['year'].value_counts().sort_index())

print("\n" + "=" * 60)
print("Download complete!")
print("=" * 60)