# Leeds Fungal Biodiversity - Temporal Analysis
# Phase 3: Time-series analysis, recording effort correction, trend testing

library(tidyverse)
library(vegan)      # For rarefaction and diversity indices
library(mgcv)       # For GAM models
library(ggplot2)

# Set working directory (adjust if running from different location)
# setwd("~/Documents/Learning/GIS/Projects/leeds-brownfield-fungal-recovery")

# Load cleaned data
fungi <- read_csv("data/processed/leeds_fungi_clean.csv")
annual <- read_csv("data/processed/annual_species_richness.csv")

cat("Loaded", nrow(fungi), "fungal records\n")
cat("Year range:", min(fungi$year), "-", max(fungi$year), "\n\n")

# ============================================================
# 1. BASIC TEMPORAL TRENDS
# ============================================================

cat("=== ANNUAL SPECIES RICHNESS ===\n")
print(annual)

# Plot raw species richness over time
p1 <- ggplot(annual, aes(x = year, y = species_richness)) +
  geom_line(color = "#B794D9", size = 1.2) +
  geom_point(color = "#7FAD87", size = 3) +
  geom_smooth(method = "lm", se = TRUE, color = "#6B8E71", linetype = "dashed") +
  labs(
    title = "Fungal Species Richness in Leeds (2009-2025)",
    subtitle = "Annual unique species counts from GBIF citizen science records",
    x = "Year",
    y = "Species Richness",
    caption = "Data: GBIF | Analysis: Daniel Crompton"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 11, color = "grey30"),
    axis.title = element_text(size = 12, face = "bold")
  )

ggsave("outputs/figures/species_richness_trend.png", p1, width = 10, height = 6, dpi = 300)
cat("Saved: outputs/figures/species_richness_trend.png\n\n")

# Linear regression (simple trend test)
lm_model <- lm(species_richness ~ year, data = annual)
cat("=== LINEAR TREND TEST ===\n")
summary(lm_model)

# ============================================================
# 2. RECORDING EFFORT CORRECTION (RAREFACTION)
# ============================================================

cat("\n=== RAREFACTION ANALYSIS ===\n")
cat("Problem: More observers in 2020 = more species found (bias)\n")
cat("Solution: Rarefy to equal sample sizes\n\n")

# Create species-by-year matrix (needed for rarefaction)
# Each row = year, each column = species, values = occurrence count

species_matrix <- fungi %>%
  count(year, scientificName) %>%
  pivot_wider(names_from = scientificName, values_from = n, values_fill = 0) %>%
  column_to_rownames("year")

cat("Species matrix dimensions:", nrow(species_matrix), "years x", ncol(species_matrix), "species\n")

# Find minimum sample size (smallest number of records in any year)
min_sample <- min(annual$n_records)
cat("Minimum annual sample size:", min_sample, "records\n")

# Rarefy each year to this minimum (equalises sampling effort)
rarefied <- as.data.frame(t(apply(species_matrix, 1, function(row) {
  if (sum(row) >= min_sample) {
    vegan::rrarefy(row, min_sample)  # Randomly subsample to min_sample
  } else {
    row  # Keep as-is if below minimum
  }
})))

# Calculate rarefied species richness (after effort correction)
rarefied_richness <- data.frame(
  year = as.numeric(rownames(rarefied)),
  rarefied_richness = rowSums(rarefied > 0),  # Count species present
  original_richness = annual$species_richness
)

cat("\nRarefied richness:\n")
print(rarefied_richness)

# Plot original vs rarefied
p2 <- rarefied_richness %>%
  pivot_longer(cols = c(rarefied_richness, original_richness), 
               names_to = "type", values_to = "richness") %>%
  ggplot(aes(x = year, y = richness, color = type, linetype = type)) +
  geom_line(size = 1.1) +
  geom_point(size = 2.5) +
  scale_color_manual(
    values = c("rarefied_richness" = "#B794D9", "original_richness" = "#7FAD87"),
    labels = c("Original", "Rarefied (effort-corrected)")
  ) +
  scale_linetype_manual(
    values = c("rarefied_richness" = "solid", "original_richness" = "dashed"),
    labels = c("Original", "Rarefied (effort-corrected)")
  ) +
  labs(
    title = "Species Richness: Original vs. Recording Effort Corrected",
    subtitle = "Rarefaction adjusts for unequal sampling (e.g., COVID-2020 spike)",
    x = "Year",
    y = "Species Richness",
    color = NULL,
    linetype = NULL
  ) +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 16, face = "bold")
  )

ggsave("outputs/figures/rarefaction_comparison.png", p2, width = 10, height = 6, dpi = 300)
cat("Saved: outputs/figures/rarefaction_comparison.png\n\n")

# ============================================================
# 3. SHANNON DIVERSITY INDEX
# ============================================================

cat("=== SHANNON DIVERSITY INDEX ===\n")
cat("Accounts for both richness AND evenness (not just species count)\n\n")

# Calculate Shannon index for each year
shannon_by_year <- data.frame(
  year = as.numeric(rownames(species_matrix)),
  shannon = diversity(species_matrix, index = "shannon")
)

cat("Shannon diversity:\n")
print(shannon_by_year)

# Plot Shannon over time
p3 <- ggplot(shannon_by_year, aes(x = year, y = shannon)) +
  geom_line(color = "#B794D9", size = 1.2) +
  geom_point(color = "#7FAD87", size = 3) +
  geom_smooth(method = "loess", se = TRUE, color = "#6B8E71") +
  labs(
    title = "Shannon Diversity Index Over Time",
    subtitle = "Combines species richness and evenness",
    x = "Year",
    y = "Shannon Diversity Index",
    caption = "Higher values = more diverse fungal communities"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(size = 16, face = "bold"))

ggsave("outputs/figures/shannon_diversity.png", p3, width = 10, height = 6, dpi = 300)
cat("Saved: outputs/figures/shannon_diversity.png\n\n")

# ============================================================
# 4. GAM (GENERALIZED ADDITIVE MODEL) - NON-LINEAR TRENDS
# ============================================================

cat("=== GAM (NON-LINEAR TREND FITTING) ===\n")
cat("Allows for curved trends (better than straight line)\n\n")

# Fit GAM to rarefied richness
gam_model <- gam(rarefied_richness ~ s(year, k = 5), data = rarefied_richness)
summary(gam_model)

# Generate predictions
gam_predictions <- data.frame(
  year = rarefied_richness$year,
  fitted = fitted(gam_model)
)

# Plot GAM fit
p4 <- ggplot(rarefied_richness, aes(x = year, y = rarefied_richness)) +
  geom_point(color = "#7FAD87", size = 3, alpha = 0.7) +
  geom_line(data = gam_predictions, aes(y = fitted), 
            color = "#B794D9", size = 1.3) +
  labs(
    title = "GAM Trend: Rarefied Species Richness",
    subtitle = "Smooth curve shows non-linear biodiversity trend",
    x = "Year",
    y = "Rarefied Species Richness"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(size = 16, face = "bold"))

ggsave("outputs/figures/gam_trend.png", p4, width = 10, height = 6, dpi = 300)
cat("Saved: outputs/figures/gam_trend.png\n\n")

# ============================================================
# 5. EXCLUDE 2024-2025 (INCOMPLETE DATA)
# ============================================================

cat("=== EXCLUDING INCOMPLETE YEARS (2024-2025) ===\n")

# Filter to complete years (2009-2023)
complete_years <- rarefied_richness %>%
  filter(year <= 2023)

# Refit linear model
lm_complete <- lm(rarefied_richness ~ year, data = complete_years)
cat("\nLinear trend (2009-2023 only):\n")
summary(lm_complete)

# ============================================================
# SAVE PROCESSED DATA
# ============================================================

write_csv(rarefied_richness, "data/processed/rarefied_richness.csv")
write_csv(shannon_by_year, "data/processed/shannon_diversity.csv")

cat("\n=== ANALYSIS COMPLETE ===\n")
cat("Outputs saved to outputs/figures/\n")
cat("Processed data saved to data/processed/\n")