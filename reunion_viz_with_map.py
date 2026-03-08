#!/usr/bin/env python3
"""
reunion_viz_with_map.py
-----------------------
Reads reunion sites from reunions.csv, enriches them with:
  - Nearest major airport + distance
  - Nearest regional airport + distance
  - Average July high/low temp & humidity (via Meteostat, with Monthly fallback)

Outputs:
  - reunions_extended.csv
  - reunion charts (JPGs)
  - reunions.kml
"""

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import requests
import numpy as np

# Try Cartopy for basemap (optional)
USE_CARTOPY = True
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except Exception:
    USE_CARTOPY = False

# Meteostat
from meteostat import Stations, Normals, Monthly, Hourly

# -----------------------------
# Major airports list (IATA, Name, Lat, Lon)
# -----------------------------
MAJOR_AIRPORTS = [
    ("ATL", "Atlanta Hartsfield-Jackson", 33.6407, -84.4277),
    ("LAX", "Los Angeles Intl", 33.9416, -118.4085),
    ("ORD", "Chicago O'Hare", 41.9742, -87.9073),
    ("DFW", "Dallas/Fort Worth Intl", 32.8998, -97.0403),
    ("DEN", "Denver Intl", 39.8561, -104.6737),
    ("JFK", "New York JFK", 40.6413, -73.7781),
    ("SFO", "San Francisco Intl", 37.6213, -122.3790),
    ("SEA", "Seattle-Tacoma Intl", 47.4502, -122.3088),
    ("LAS", "Las Vegas McCarran", 36.0840, -115.1537),
    ("MCO", "Orlando Intl", 28.4312, -81.3081),
    ("MIA", "Miami Intl", 25.7959, -80.2870),
    ("BOS", "Boston Logan", 42.3656, -71.0096),
    ("PHX", "Phoenix Sky Harbor", 33.4350, -112.0000),
    ("CLT", "Charlotte Douglas", 35.2140, -80.9431),
    ("IAH", "Houston Intercontinental", 29.9902, -95.3368),
    ("MSP", "Minneapolis-St. Paul", 44.8848, -93.2223),
    ("DTW", "Detroit Metro", 42.2124, -83.3534),
    ("PHL", "Philadelphia Intl", 39.8744, -75.2424),
    ("SAN", "San Diego Intl", 32.7338, -117.1933),
    ("SLC", "Salt Lake City Intl", 40.7899, -111.9791),
    ("PDX", "Portland Intl", 45.5898, -122.5951),
    ("BWI", "Baltimore/Washington", 39.1754, -76.6684),
    ("TPA", "Tampa Intl", 27.9755, -82.5332),
    ("HNL", "Honolulu Daniel K. Inouye Intl", 21.3187, -157.9220),
]

# -----------------------------
# Download OurAirports dataset (regional airports)
# -----------------------------
AIRPORTS_CSV = Path("data/inputs/airports.csv")

def load_regional_airports():
    if not AIRPORTS_CSV.exists():
        url = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        AIRPORTS_CSV.write_text(r.text, encoding="utf-8")

    df = pd.read_csv(AIRPORTS_CSV)
    # Filter: only small/medium airports in US
    df = df[(df["iso_country"] == "US") & (df["type"].isin(["medium_airport", "small_airport"]))]
    return df[["ident", "name", "latitude_deg", "longitude_deg"]]

# -----------------------------
# Enrichment functions
# -----------------------------
def nearest_major_airport(lat, lon):
    pt = (lat, lon)
    best = None
    bestd = 1e9
    for code, name, alat, alon in MAJOR_AIRPORTS:
        d = geodesic(pt, (alat, alon)).km
        if d < bestd:
            bestd = d
            best = f"{code} ({name})"
    return best, round(bestd, 1)

def nearest_regional_airport(lat, lon, regional_df):
    pt = (lat, lon)
    dists = regional_df.apply(
        lambda r: geodesic(pt, (r["latitude_deg"], r["longitude_deg"])).km, axis=1
    )
    idx = dists.idxmin()
    row = regional_df.loc[idx]
    return f"{row['ident']} ({row['name']})", round(dists.min(), 1)

def c_to_f(c):
    return round((c * 9/5) + 32, 1) if c is not None else None

def july_climate(lat, lon):
    """
    Return (AvgHighJulyF, AvgLowJulyF, AvgHumidityJuly) for a given lat/lon.
    Adds debug prints for humidity fetching.
    """
    stations = Stations().nearby(lat, lon)
    stn = stations.fetch(1)
    if stn.empty:
        print(f"No station found for ({lat},{lon})")
        return None, None, None
    sid = stn.index[0]
    print(f"Using station {sid} for ({lat},{lon})")

    hi_f = lo_f = None
    try:
        normals = Normals(sid).fetch()
        if not normals.empty and 7 in normals.index:
            row = normals.loc[7]
            tmax = row.get("tmax")
            tmin = row.get("tmin")
            hi_f = c_to_f(tmax) if tmax is not None else None
            lo_f = c_to_f(tmin) if tmin is not None else None
            print(f"Normals temps for {sid}: hi={hi_f}, lo={lo_f}")
    except Exception as e:
        print(f"Normals error for {sid}: {e}")

    if hi_f is None or lo_f is None:
        try:
            end = pd.Timestamp.today().normalize()
            start = end - pd.DateOffset(years=15)
            m = Monthly(sid, start, end).fetch()
            if not m.empty:
                m_july = m[m.index.month == 7]
                if not m_july.empty:
                    tmax = m_july["tmax"].mean() if "tmax" in m_july.columns else None
                    tmin = m_july["tmin"].mean() if "tmin" in m_july.columns else None
                    if tmax is not None:
                        hi_f = c_to_f(float(tmax))
                    if tmin is not None:
                        lo_f = c_to_f(float(tmin))
                    print(f"Monthly temps for {sid}: hi={hi_f}, lo={lo_f}")
        except Exception as e:
            print(f"Monthly error for {sid}: {e}")

    rh_vals = []
    try:
        import datetime as _dt
        current_year = pd.Timestamp.today().year
        years = [current_year - i - 1 for i in range(5)]  # last 5 *complete* years
        for y in years:
            try:
                # Use naive datetimes interpreted as UTC by Meteostat
                target = _dt.datetime(y, 7, 1, 18, 0, 0)  # 18:00 UTC (approx midday US)
                win_start = _dt.datetime(y, 7, 1, 15, 0, 0)
                win_end   = _dt.datetime(y, 7, 1, 21, 0, 0)

                # Half-open window: [start, end+1h) to include 21:00
                h = Hourly(sid, win_start, win_end + pd.Timedelta(hours=1)).fetch()
                tzinfo = getattr(h.index, 'tz', None)
                print(f"Year {y}: fetched {len(h)} hourly rows, index tz={tzinfo}")
                if h.empty or 'rhum' not in h.columns:
                    print(f"{y}: hourly empty or no rhum column")
                    continue

                # Normalize index to *naive UTC* so comparisons with naive targets are valid
                if tzinfo is not None:
                    h.index = h.index.tz_convert('UTC').tz_localize(None)

                # Cast humidity to numeric
                rh = pd.to_numeric(h['rhum'], errors='coerce')

                if target in h.index and pd.notnull(rh.loc[target]):
                    val = float(rh.loc[target])
                    rh_vals.append(val)
                    print(f"{y}: exact 18UTC rh={val}")
                else:
                    mask = (h.index >= win_start) & (h.index <= win_end)
                    window_vals = rh.loc[mask].dropna()
                    if not window_vals.empty:
                        mean_val = float(window_vals.mean())
                        rh_vals.append(mean_val)
                        print(f"{y}: avg window rh={mean_val} from {len(window_vals)} obs")
                    else:
                        print(f"{y}: no rhum values in window")
            except Exception as e:
                print(f"Error year {y} for {sid}: {e}")
                continue
        avg_rh = round(float(pd.Series(rh_vals).mean()), 1) if rh_vals else None
    except Exception as e:
        print(f"Humidity error for {sid}: {e}")
        avg_rh = None

    return hi_f, lo_f, avg_rh

# -----------------------------
# KML Export
# -----------------------------
from xml.sax.saxutils import escape

def grouped_by_coord_with_meta(df: pd.DataFrame, ndigits: int = 3) -> pd.DataFrame:
    tmp = df.copy()
    tmp["LonR"] = tmp["Longitude"].round(ndigits)
    tmp["LatR"] = tmp["Latitude"].round(ndigits)
    grouped = (
        tmp.groupby(["LonR", "LatR"], as_index=False)
           .agg(Years=("Year", lambda s: ", ".join(map(str, sorted(s)))),
                Location=("Location", "first"),
                State=("State", "first"),
                Region=("Region", "first"),
                VenueType=("VenueType", "first"))
    )
    return grouped

def export_kml(df: pd.DataFrame, out_path: Path, ndigits: int = 3):
    g = grouped_by_coord_with_meta(df, ndigits=ndigits)
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    parts.append('  <Document>')
    parts.append('    <name>Family Reunion Sites</name>')
    for _, r in g.iterrows():
        name = escape(str(r["Years"]))
        desc = escape(f'{r["Location"]}, {r["State"]} ({r["VenueType"]}, {r["Region"]})')
        lon = float(r["LonR"])
        lat = float(r["LatR"])
        parts.append('    <Placemark>')
        parts.append(f'      <name>{name}</name>')
        parts.append(f'      <description>{desc}</description>')
        parts.append('      <Point>')
        parts.append(f'        <coordinates>{lon:.6f},{lat:.6f},0</coordinates>')
        parts.append('      </Point>')
        parts.append('    </Placemark>')
    parts.append('  </Document>')
    parts.append('</kml>')
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote KML: {out_path.resolve()}")

# -----------------------------
# Visualization
# -----------------------------
def make_visuals(df: pd.DataFrame, out_dir: Path):
    # Ensure numeric types
    for col in ["AvgHighJulyF", "AvgLowJulyF", "AvgHumidityJuly", "DistMajorKm", "DistRegionalKm"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Label for scatter: "Year - Location, State"
    if {"Year", "Location", "State"}.issubset(df.columns):
        df["Label"] = (
            df["Year"].astype(str)
            + " - "
            + df["Location"].astype(str)
            + ", "
            + df["State"].astype(str)
        )
    elif {"Year", "Location"}.issubset(df.columns):
        df["Label"] = df["Year"].astype(str) + " - " + df["Location"].astype(str)

    # Map-like scatter (Longitude vs Latitude)
    dfs = df.sort_values("Year")
    plt.figure(figsize=(10,6))
    plt.scatter(dfs["Longitude"], dfs["Latitude"])
    for _, r in dfs.iterrows():
        plt.annotate(str(r["Year"]), (r["Longitude"], r["Latitude"]), xytext=(3,3), textcoords="offset points", fontsize=8)
    plt.title("Family Reunion Locations (Longitude vs Latitude)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True, linestyle=":")
    min_lon = min(dfs["Longitude"].min()-5, -170)
    max_lon = max(dfs["Longitude"].max()+5, -65)
    min_lat = min(dfs["Latitude"].min()-5, 15)
    max_lat = max(dfs["Latitude"].max()+5, 50)
    plt.xlim(min_lon, max_lon)
    plt.ylim(min_lat, max_lat)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig(out_dir / "map_scatter.jpg", dpi=200)
    plt.close()

    # Region histogram
    plt.figure(figsize=(9,5))
    df.groupby("Region")["Year"].count().sort_values(ascending=False).plot(kind="bar")
    plt.title("Reunions by Region")
    plt.tight_layout()
    plt.savefig(out_dir / "hist_by_region.jpg", dpi=200)
    plt.close()

    # State histogram
    plt.figure(figsize=(10,5))
    df.groupby("State")["Year"].count().sort_values(ascending=False).plot(kind="bar")
    plt.title("Reunions by State")
    plt.tight_layout()
    plt.savefig(out_dir / "hist_by_state.jpg", dpi=200)
    plt.close()

    # Venue type histogram
    plt.figure(figsize=(10,5))
    df.groupby("VenueType")["Year"].count().sort_values(ascending=False).plot(kind="bar")
    plt.title("Reunions by Venue Type")
    plt.xlabel("Venue Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(out_dir / "venue_type_hist.jpg", dpi=200)
    plt.close()

    # Reunion years bar
    dfs = df.sort_values("Year")
    plt.figure(figsize=(12,4))
    plt.bar(dfs["Year"].astype(str), [1]*len(dfs))
    plt.title("Reunion Years")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_dir / "count_by_year.jpg", dpi=200)
    plt.close()

    # Average high temps
    s = df.set_index("Location")["AvgHighJulyF"].dropna()
    if not s.empty:
        plt.figure(figsize=(10,5))
        s.plot(kind="bar")
        plt.title("Average July High Temp (°F)")
        plt.tight_layout()
        plt.savefig(out_dir / "avg_temp_highs.jpg", dpi=200)
        plt.close()

    # Temp vs Humidity
    xy = df[["Label", "AvgHighJulyF", "AvgHumidityJuly"]].dropna()
    if not xy.empty:
        plt.figure(figsize=(6,6))
        plt.scatter(xy["AvgHumidityJuly"], xy["AvgHighJulyF"])
        for _, r in xy.iterrows():
            plt.annotate(r["Label"], (r["AvgHumidityJuly"], r["AvgHighJulyF"]), fontsize=7)
        plt.xlabel("Avg July Humidity (%)")
        plt.ylabel("Avg July High (°F)")
        plt.title("Humidity vs Temp (July)")
        plt.tight_layout()
        plt.savefig(out_dir / "temp_vs_humidity.jpg", dpi=200)
        plt.close()

    # Major airport distances
    s = df["DistMajorKm"].dropna()
    if not s.empty:
        plt.figure(figsize=(8,5))
        s.plot(kind="hist", bins=10)
        plt.title("Distance to Nearest Major Airport (km)")
        plt.xlabel("Km")
        plt.tight_layout()
        plt.savefig(out_dir / "dist_major_airports.jpg", dpi=200)
        plt.close()

    # Regional airport distances
    s = df["DistRegionalKm"].dropna()
    if not s.empty:
        plt.figure(figsize=(8,5))
        s.plot(kind="hist", bins=10)
        plt.title("Distance to Nearest Regional Airport (km)")
        plt.xlabel("Km")
        plt.tight_layout()
        plt.savefig(out_dir / "dist_regional_airports.jpg", dpi=200)
        plt.close()

    # Horizontal bar chart of distances by site (miles), side-by-side major vs regional
    if {"Label", "DistMajorKm", "DistRegionalKm"}.issubset(df.columns):
        bars = df[["Label", "DistMajorKm", "DistRegionalKm"]].copy()
        # Keep rows with at least one distance
        bars = bars[(~bars["DistMajorKm"].isna()) | (~bars["DistRegionalKm"].isna())]
        if not bars.empty:
            KM_TO_MI = 0.621371
            bars["MajorMi"] = bars["DistMajorKm"].astype(float) * KM_TO_MI
            bars["RegionalMi"] = bars["DistRegionalKm"].astype(float) * KM_TO_MI
            # Replace NaN with 0 for plotting, but keep original for sorting
            major_sort = bars["MajorMi"].fillna(0)
            # Sort by major distance descending (fallback to regional if major missing)
            sort_key = np.where(major_sort.values == 0, bars["RegionalMi"].fillna(0).values, major_sort.values)
            order = np.argsort(-sort_key)
            bars = bars.iloc[order]

            idx = np.arange(len(bars))
            h = 0.4
            plt.figure(figsize=(12, max(6, 0.35*len(bars))))
            plt.barh(idx + h/2, bars["MajorMi"].fillna(0), height=h, label="Major (mi)")
            plt.barh(idx - h/2, bars["RegionalMi"].fillna(0), height=h, label="Regional (mi)")
            plt.yticks(idx, bars["Label"].tolist())
            plt.xlabel("Distance (miles)")
            plt.title("Distance to Nearest Airports by Site (miles)")
            plt.grid(axis="x", linestyle=":", alpha=0.6)
            plt.legend()
            plt.tight_layout()
            plt.savefig(out_dir / "airport_distances_miles.jpg", dpi=200)
            plt.close()

# -----------------------------
# Main
# -----------------------------
def main():
    base_csv = Path("data/inputs/reunions.csv")
    out_csv = Path("data/outputs/reunions_extended.csv")
    out_dir = Path("data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    if out_csv.exists():
        print(f"Found existing {out_csv.name}; loading cached enrichment.")
        df = pd.read_csv(out_csv)
        export_kml(df, out_dir / "reunions.kml")
        make_visuals(df, out_dir)
        return
    df = pd.read_csv(base_csv)
    regional_df = load_regional_airports()

    majors, majors_d, regionals, regionals_d = [], [], [], []
    highs, lows, hums = [], [], []

    for _, r in df.iterrows():
        lat, lon = r["Latitude"], r["Longitude"]

        maj, majd = nearest_major_airport(lat, lon)
        majors.append(maj)
        majors_d.append(majd)

        reg, regd = nearest_regional_airport(lat, lon, regional_df)
        regionals.append(reg)
        regionals_d.append(regd)

        hi, lo, hu = july_climate(lat, lon)
        highs.append(hi)
        lows.append(lo)
        hums.append(hu)

    df["NearestMajorAirport"] = majors
    df["DistMajorKm"] = majors_d
    df["NearestRegionalAirport"] = regionals
    df["DistRegionalKm"] = regionals_d
    df["AvgHighJulyF"] = highs
    df["AvgLowJulyF"] = lows
    df["AvgHumidityJuly"] = hums

    df.to_csv(out_csv, index=False)
    print(f"Wrote extended CSV: {out_csv.resolve()}")

    export_kml(df, out_dir / "reunions.kml")
    make_visuals(df, out_dir)

if __name__ == "__main__":
    main()
