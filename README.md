# Adams Reunion Locations

Tools and data for analyzing past Adams family reunion sites and evaluating candidate locations for future reunions.

## Background

The Adams family reunion has taken place roughly every three years since 1962, spanning locations across the United States — from South Dakota and Minnesota to Colorado, Oregon, and Hawaii. With 21 reunions and counting, choosing the next site involves balancing travel accessibility, climate, venue type, region variety, and family preferences.

This project was created to:

1. **Catalog** all past reunion locations with coordinates, region, and venue type.
2. **Enrich** each site with travel and climate data — nearest airports (major and regional) with distances, and average July temperature and humidity.
3. **Visualize** trends across reunion history — which regions and states have been visited, how accessible sites are by air, and what the summer climate looks like.
4. **Compare** candidate locations against the historical data to support an informed group decision.

## Repository Structure

```
reunion_viz_with_map.py       # Main script: reads CSV, enriches, generates charts + KML
data/
  inputs/
    reunions.csv              # Base data: Year, Location, State, Region, Lat/Lon, VenueType
    airports.csv              # Cached OurAirports dataset (downloaded on first run)
  outputs/
    reunions_extended.csv     # Enriched output: adds airport distances + July climate
    reunions.kml              # KML export for Google Earth / Google Maps
    *.jpg                     # Generated visualization charts
```

## Scripts

### `reunion_viz.py`

A simple, self-contained script with reunion data embedded directly in the code. Generates basic charts without any external data fetches.

**Outputs:** `reunions.csv`, `map_scatter.jpg`, `hist_by_region.jpg`, `hist_by_state.jpg`, `venue_type_hist.jpg`, `count_by_year.jpg`

**Requirements:** `pandas`, `matplotlib`

```bash
python reunion_viz.py
```

### `reunion_viz_with_map.py`

The main enrichment and visualization script. Reads `data/inputs/reunions.csv`, enriches each site with airport and climate data, and outputs an extended CSV, KML file, and charts to `data/outputs/`.

**What it does:**

1. Reads `data/inputs/reunions.csv` (base data with coordinates).
2. If `data/outputs/reunions_extended.csv` already exists, loads the cached version and skips enrichment (delete the file to force a rebuild).
3. Otherwise, for each site:
   - Finds the **nearest major airport** (from an embedded list of ~24 top U.S. hubs including HNL) and computes the distance in km.
   - Downloads the [OurAirports](https://ourairports.com/data/) dataset (cached locally as `data/inputs/airports.csv`) and finds the **nearest regional airport** with distance.
   - Queries [Meteostat](https://meteostat.net/) for **July climate data**: average high/low temperature (°F) from climate normals (with a Monthly fallback over the last 15 years), and average humidity sampled from hourly data on July 1st midday (18:00 UTC) over the last 5 complete years.
4. Saves `data/outputs/reunions_extended.csv` with the enriched columns.
5. Exports `data/outputs/reunions.kml` with placemarks grouped by coordinates — sites visited multiple times show comma-separated years as the label (e.g., `1992, 1995`).
6. Generates visualization JPGs in `data/outputs/`.

**Requirements:** `pandas`, `matplotlib`, `numpy`, `geopy`, `meteostat`, `requests`

Optional: `cartopy` (for a US basemap underlay on the scatter map)

```bash
pip install pandas matplotlib numpy geopy meteostat requests
python reunion_viz_with_map.py
```

## Inputs

### `reunions.csv`

The base dataset with one row per reunion (`data/inputs/reunions.csv`). To add candidate locations for a future reunion, append rows to this file and delete `data/outputs/reunions_extended.csv` before re-running.

| Column    | Description                                          |
|-----------|------------------------------------------------------|
| Year      | Reunion year                                         |
| Location  | Venue name                                           |
| State     | Two-letter U.S. state abbreviation                   |
| Region    | U.S. Census region (Midwest, South, West, Northeast, Hawaii) |
| Latitude  | Approximate latitude of the venue                    |
| Longitude | Approximate longitude of the venue                   |
| VenueType | Lodge, Resort, State Park, Cottages, etc.            |

## Outputs

### `reunions_extended.csv`

Adds the following columns to the base data:

| Column               | Description                                              |
|----------------------|----------------------------------------------------------|
| NearestMajorAirport  | IATA code and name of the closest major U.S. airport     |
| DistMajorKm          | Great-circle distance to that airport (km)               |
| NearestRegionalAirport | Identifier and name of the closest small/medium airport |
| DistRegionalKm       | Great-circle distance to that airport (km)               |
| AvgHighJulyF         | Average July high temperature (°F)                       |
| AvgLowJulyF          | Average July low temperature (°F)                        |
| AvgHumidityJuly      | Average July 1 midday relative humidity (%)              |

### `reunions.kml`

A KML file for use in Google Earth or Google Maps. Each placemark shows:
- **Name:** comma-separated reunion years at that location
- **Description:** venue name, state, venue type, and region

### Generated Charts (JPGs)

| File                              | Description                                           |
|-----------------------------------|-------------------------------------------------------|
| `hist_by_region.jpg`              | Bar chart of reunion count by U.S. region             |
| `hist_by_state.jpg`              | Bar chart of reunion count by state                    |
| `avg_temp_highs.jpg`             | Bar chart of average July high temp (°F) per location  |
| `temp_vs_humidity.jpg`           | Scatter of humidity (%) vs July high temp (°F) per site |
| `dist_major_airports.jpg`        | Histogram of distances to nearest major airport (km)   |
| `dist_regional_airports.jpg`     | Histogram of distances to nearest regional airport (km)|
| `airport_distances_miles.jpg`    | Horizontal bar chart comparing major vs regional airport distance (miles) per site |

## Data Sources

- **Airport locations:** [OurAirports](https://ourairports.com/data/) (via GitHub mirror)
- **Climate data:** [Meteostat](https://meteostat.net/) — climate normals, monthly summaries, and hourly observations
- **Distance calculations:** [geopy](https://pypi.org/project/geopy/) geodesic (WGS-84)

