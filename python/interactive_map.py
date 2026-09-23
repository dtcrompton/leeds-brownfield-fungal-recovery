"""
Interactive map of Leeds fungal recording locations
Shows spatial distribution of citizen science effort
Colour-coded by functional group
Styled to match GM Brownfield interactive map
"""
import pandas as pd
import folium
from folium import plugins

print("=" * 60)
print("Creating Interactive Fungal Biodiversity Map")
print("=" * 60)

# Load classified data
fungi = pd.read_csv('data/processed/fungi_classified.csv')
print(f"\nLoaded {len(fungi):,} records")
print(f"Date range: {fungi['year'].min():.0f}-{fungi['year'].max():.0f}")

# Remove records with missing coordinates
fungi_valid = fungi.dropna(subset=['decimalLatitude', 'decimalLongitude'])
print(f"Records with valid coordinates: {len(fungi_valid):,}")

# Colour scheme for functional groups
colour_map = {
    'Mycorrhizal': '#B794D9',
    'Saprotrophic': '#7FAD87',
    'Parasitic': '#D9947F',
    'Other/Unknown': '#CCCCCC'
}

# Count per group for the info panel
group_counts = fungi_valid['functional_group'].value_counts()

# Map centre
leeds_centre = [53.8, -1.55]

# Create base map — identical pattern to GM script
m = folium.Map(
    location=leeds_centre,
    zoom_start=11,
    tiles=None
)

folium.TileLayer(
    tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=cb1_3v0u_1_4c9d5c04c3cacfcff5b8cd1e",
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    name="CARTO Light"
).add_to(m)

# --- MeasureControl (top left) — exactly as GM script ---
scale = plugins.MeasureControl(
    position='topleft',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqkilometers',
    secondary_area_unit='sqmiles'
)
scale.add_to(m)

# --- Recentre button — exactly as GM script (top: 10px, left: 50px) ---
recentre_script = f"""
<div id="recentre-btn" style="
    position: fixed;
    top: 10px;
    left: 50px;
    z-index: 1000;
    background-color: white;
    border: 2px solid rgba(0,0,0,0.2);
    border-radius: 4px;
    padding: 8px 12px;
    cursor: pointer;
    font-family: Arial, sans-serif;
    font-size: 14px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.2);
">
    Recentre Map
</div>
<script>
setTimeout(function() {{
    var recentreBtn = document.getElementById('recentre-btn');
    if (recentreBtn) {{
        recentreBtn.onclick = function() {{
            var mapObj = window[Object.keys(window).filter(key => key.startsWith('map_'))[0]];
            if (mapObj) {{
                mapObj.setView([{leeds_centre[0]}, {leeds_centre[1]}], 11);
            }}
        }};
    }}
}}, 1000);
</script>
"""
m.get_root().html.add_child(folium.Element(recentre_script))

# --- Info panel (bottom right) — matches GM map style ---
title_html = f"""
<div style="
    position: fixed;
    bottom: 20px;
    right: 10px;
    width: 350px;
    background-color: white;
    border: 2px solid rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 15px;
    z-index: 1000;
    font-family: Arial, sans-serif;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
">
    <h3 style="margin: 0 0 10px 0; color: #2C3E50;">Leeds Fungal Biodiversity (2009-2025)</h3>
    <p style="margin: 0 0 8px 0; font-size: 13px; color: #555;">
        GBIF citizen science records (n={len(fungi_valid):,})
    </p>
    <div style="font-size: 12px; color: #666; line-height: 1.6;">
        <p style="margin: 10px 0 5px 0;"><strong>Functional Groups:</strong></p>
        <div style="margin-top: 5px;">
            <div><span style="color: #B794D9;">&#9679;</span> Mycorrhizal: {group_counts.get('Mycorrhizal', 0):,} records</div>
            <div><span style="color: #7FAD87;">&#9679;</span> Saprotrophic: {group_counts.get('Saprotrophic', 0):,} records</div>
            <div><span style="color: #D9947F;">&#9679;</span> Parasitic: {group_counts.get('Parasitic', 0):,} records</div>
            <div><span style="color: #CCCCCC;">&#9679;</span> Other/Unknown: {group_counts.get('Other/Unknown', 0):,} records</div>
        </div>
    </div>
    <p style="margin: 12px 0 0 0; font-size: 11px; color: #999; border-top: 1px solid #eee; padding-top: 8px;">
        Click markers for species details | Toggle layers to filter by group | Created by Daniel Crompton, 2026.
    </p>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# --- Feature groups — no clustering, individual coloured markers ---
feature_groups = {}
for group, colour in colour_map.items():
    feature_groups[group] = folium.FeatureGroup(name=group, show=True)
    m.add_child(feature_groups[group])

# Sample if too many markers for performance
MAX_MARKERS = 3000
if len(fungi_valid) > MAX_MARKERS:
    print(f"\nSampling {MAX_MARKERS} records for map performance...")
    fungi_sample = fungi_valid.sample(n=MAX_MARKERS, random_state=42)
else:
    fungi_sample = fungi_valid

print(f"Adding {len(fungi_sample):,} markers to map...")

for idx, row in fungi_sample.iterrows():
    group = row['functional_group']
    colour = colour_map.get(group, '#CCCCCC')

    popup_html = f"""
    <div style="font-family: Arial; width: 250px;">
        <h4 style="margin-bottom: 10px;">{row['scientificName']}</h4>
        <table style="width: 100%;">
            <tr><td><b>Functional group:</b></td><td>{group}</td></tr>
            <tr><td><b>Year:</b></td><td>{row['year']:.0f}</td></tr>
            <tr><td><b>Genus:</b></td><td>{row['genus']}</td></tr>
            <tr><td><b>Family:</b></td><td>{row.get('family', 'Unknown')}</td></tr>
        </table>
    </div>
    """

    folium.CircleMarker(
        location=[row['decimalLatitude'], row['decimalLongitude']],
        radius=6,
        popup=folium.Popup(popup_html, max_width=300),
        color=colour,
        fillColor=colour,
        fillOpacity=0.7,
        weight=2
    ).add_to(feature_groups[group])

# Layer control (top right) — exactly as GM script
folium.LayerControl(collapsed=False).add_to(m)

# Save map
output_file = 'outputs/maps/leeds_fungi_interactive.html'
m.save(output_file)

print(f"\nSaved: {output_file}")
print("\n" + "=" * 60)
print("Map creation complete!")
print("=" * 60)
print(f"\nOpen in browser: file://{output_file}")
