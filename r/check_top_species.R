library(tidyverse)

fungi <- read_csv("data/processed/leeds_fungi_clean.csv")

# Top 30 species
top_species <- fungi %>%
  count(scientificName, genus) %>%
  arrange(desc(n)) %>%
  head(30)

print(top_species)