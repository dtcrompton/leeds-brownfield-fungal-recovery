"""
GBIF Data Cleaning
- Remove duplicates
- Filter to species-level identifications
- Classify by functional type (mycorrhizal vs saprotrophic)
- Aggregate for time-series analysis
"""

import pandas as pd
import numpy as np

print("=" * 60)
print("GBIF Data Cleaning - Leeds Fungi")
print("=" * 60)

# Load raw data
print("\nLoading raw GBIF data...")
df = pd.read_csv('../data/gbif/leeds_fungi_raw.csv')
print(f"Raw records: {len(df):,}")

# 1. Remove duplicates (same species, location, date)
# For biodiversity analysis, deduplicate by species + location + year
# (We don't care if same species was seen multiple times in one year)
print("\n1. Removing duplicates...")
initial_count = len(df)
df = df.drop_duplicates(subset=['scientificName', 'decimalLatitude', 'decimalLongitude', 'year'])
print(f"   Removed {initial_count - len(df):,} duplicates")
print(f"   Remaining: {len(df):,}")

# 2. Filter to species-level identifications
print("\n2. Filtering to species-level IDs...")
initial_count = len(df)

# Keep only records with species name (not just genus or family)
df_species = df[df['species'].notna()].copy()

print(f"   Removed {initial_count - len(df_species):,} genus/family-level records")
print(f"   Remaining: {len(df_species):,}")

# 3. Check year completeness
print("\n3. Year data completeness...")
print(f"   Records with year: {df_species['year'].notna().sum():,}")
print(f"   Missing year: {df_species['year'].isna().sum():,}")

# Drop records without year (can't do time-series)
df_clean = df_species[df_species['year'].notna()].copy()
print(f"   Remaining: {len(df_clean):,}")

# 4. Year range check
print("\n4. Year range:")
print(f"   Min year: {df_clean['year'].min():.0f}")
print(f"   Max year: {df_clean['year'].max():.0f}")

# Filter to 2009-2025 (remove any outliers)
df_clean = df_clean[(df_clean['year'] >= 2009) & (df_clean['year'] <= 2025)]
print(f"   After filtering to 2009-2025: {len(df_clean):,}")

# 5. Summary by year
print("\n5. Records by year:")
year_counts = df_clean['year'].value_counts().sort_index()
for year, count in year_counts.items():
    print(f"   {int(year)}: {count:>4} records")

# 6. Species richness
print("\n6. Species diversity:")
unique_species = df_clean['scientificName'].nunique()
print(f"   Unique species: {unique_species:,}")

# Top species
print("\n   Top 10 species:")
for i, (species, count) in enumerate(df_clean['scientificName'].value_counts().head(10).items(), 1):
    print(f"   {i:>2}. {species:<50} {count:>4}")

# 7. Save cleaned data
output_file = '../data/processed/leeds_fungi_clean.csv'
df_clean.to_csv(output_file, index=False)
print(f"\nSaved cleaned data: {output_file}")

# 8. Create annual summary (for time-series analysis)
annual_summary = df_clean.groupby('year').agg({
    'gbifID': 'count',  # Number of records
    'scientificName': 'nunique'  # Number of unique species (species richness)
}).reset_index()

annual_summary.columns = ['year', 'n_records', 'species_richness']

output_summary = '../data/processed/annual_species_richness.csv'
annual_summary.to_csv(output_summary, index=False)
print(f"Saved annual summary: {output_summary}")

print("\nAnnual species richness:")
print(annual_summary.to_string(index=False))

print("\n" + "=" * 60)
print("Cleaning complete!")
print("=" * 60)
print(f"Final dataset: {len(df_clean):,} records")
print(f"Species: {unique_species:,}")
print(f"Years: {int(df_clean['year'].min())}-{int(df_clean['year'].max())}")