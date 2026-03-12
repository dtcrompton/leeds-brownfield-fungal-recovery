# Leeds Fungal Biodiversity Analysis

Time-series analysis of fungal biodiversity trends in Leeds (2009–2025) and correlation with urban tree planting programmes.

**Live project:** [dtcrompton.github.io/projects/fungi](https://dtcrompton.github.io/projects/fungi/index.html)
**Interactive map:** [dtcrompton.github.io/projects/fungi/map.html](https://dtcrompton.github.io/projects/fungi/map.html)

---

## Finding

Fungal diversity declined after the major Leeds tree planting schemes of 2020–2022, not increased. Rarefied species richness peaked around 2015–2017 and has fallen sharply since 2020. The functional composition shift — mycorrhizal proportion declining, saprotrophic proportion rising — is consistent with short-term mycorrhizal network disruption caused by soil disturbance during planting.

This challenges a common assumption in restoration ecology: that tree planting straightforwardly supports fungal biodiversity recovery. The data suggests a 5–10 year disruption window before networks can begin to re-establish, with significant implications for how carbon offsetting schemes account for below-ground ecosystem impacts.

---

## Project Evolution

This project began with a different scope and adapted based on data quality findings.

**Original plan:** Site-level analysis comparing fungal biodiversity at restored vs. unrestored brownfield sites.

**Why the scope changed:** Data quality assessment revealed that 86% of GBIF fungal records have coordinate uncertainty >1km, preventing reliable spatial matching to individual brownfield sites (mean area ~1 hectare). Only 10.4% of records met the <100m precision threshold required for site-level analysis.

**Revised approach:** Citywide temporal analysis examining Leeds-wide fungal biodiversity trends and their correlation with restoration timeline events — using the full dataset rather than discarding 90% of records.

**Key lesson:** Citizen science data is valuable for broad temporal and regional trends but unsuitable for fine-scale spatial analysis without quality filtering. Future site-level studies would require systematic plot surveys with <50m GPS precision.

---

## Project Structure

```
leeds-brownfield-fungal-recovery/
│
├── data/
│   ├── raw/
│   │   ├── leeds_brownfield.csv          # 878 brownfield sites
│   │   └── leeds_fungi_raw.csv           # 10,200 GBIF occurrence records
│   └── processed/
│       ├── leeds_fungi_clean.csv         # 8,548 cleaned records
│       ├── annual_species_richness.csv   # Species richness 2009–2025
│       └── fungi_classified.csv          # Records with functional group labels
│
├── scripts/
│   ├── 01_gbif_download.py               # GBIF API query
│   ├── 02_gbif_clean.py                  # Cleaning and deduplication
│   ├── 03_temporal_analysis.R            # Rarefaction, GAM, Shannon index
│   ├── 04_functional_composition.R       # Functional group analysis
│   ├── 05_restoration_correlation.R      # Tree planting overlay
│   └── 06_create_map.py                  # Folium interactive map
│
├── outputs/
│   ├── figures/
│   │   ├── species_richness_trend.png
│   │   ├── rarefaction_comparison.png
│   │   ├── gam_trend.png
│   │   ├── shannon_diversity.png
│   │   ├── functional_composition.png
│   │   └── restoration_correlation.png
│   └── maps/
│       └── leeds_fungi_interactive.html
│
└── README.md
```

---

## Methodology

### Phase 1 — Data Collection ✅
- Downloaded Leeds brownfield register (878 sites)
- Queried GBIF API for fungal occurrence records in Leeds (10,200 records, 1,107 species, 2009–2025)
- Assessed data quality — 86% of records have coordinate uncertainty >1km

### Phase 2 — Data Cleaning ✅
- Removed duplicates (same species, location, year)
- Filtered to species-level identifications
- Created cleaned annual time-series dataset (8,548 records)

### Phase 3 — Temporal Analysis ✅
- Rarefied species richness to correct for unequal recording effort
- Calculated Shannon Diversity Index annually
- Fitted GAM (mgcv) to identify non-linear temporal trend
- COVID-2020 recording spike identified and corrected by rarefaction

### Phase 4 — Restoration Timeline Correlation ✅
- Compiled Leeds tree planting data: Broughton Sanctuary (160ha, December 2020), South Leeds (62,500 trees, 2021–2022)
- Overlaid planting volumes against rarefied species richness on dual-axis chart
- Post-2020 diversity decline coincides with planting activity

### Phase 5 — Functional Composition Analysis ✅
- Classified species by ecological function (Mycorrhizal, Saprotrophic, Parasitic, Other/Unknown) via trait database lookup
- Mycorrhizal proportion declined from ~25–30% (2009) to ~10–15% (2023–2025)
- Saprotrophic proportion increased — consistent with disturbed soil conditions

### Phase 6 — Final Outputs ✅
- Interactive Folium map (colour-coded by functional group, individual markers)
- Technical write-up (portfolio page)
- Stakeholder explainer (portfolio page)
- README updated

---

## Data Sources

- **GBIF** — citizen science fungal occurrence records for Leeds
- **Leeds City Council** — tree planting data 2020–2025

---

## Tools & Technologies

| Tool | Use |
|------|-----|
| Python (pandas, Folium, requests) | Data acquisition, interactive mapping |
| R (vegan, mgcv, ggplot2, dplyr) | Statistical analysis, visualisation |
| GBIF API | Biodiversity data download |

---

## Limitations

- Citizen science records reflect recording effort as well as actual species presence — rarefaction corrects partially but not fully
- Data ends 2025, only 3–5 years post-planting — too early to observe recovery
- No soil sampling or DNA metabarcoding — functional group shifts are inferred from occurrence records, not direct measurement
- Spatial resolution: Leeds treated as a single unit — site-level analysis around planting locations would provide stronger causal evidence

---

*Analysis by Daniel Crompton, 2026 | [dtcrompton.github.io](https://dtcrompton.github.io)*
