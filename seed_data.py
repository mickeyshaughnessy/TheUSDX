"""
Seed federal datasets into DO Spaces for Acme Redactors / TheUSDX.

Run once to populate the usdx/data/ and usdx/metadata/ prefixes in the
mithril-media bucket.  After seeding, collect_data() in handlers.py will
find real datasets instead of falling back to _get_sample_data().

Usage:
    python seed_data.py
"""
import json
import boto3
import config

DATASETS = [
    # -------------------------------------------------------------------------
    # Census & Demographics
    # -------------------------------------------------------------------------
    {
        "id": "census-pop-2023",
        "category": "census",
        "title": "US Population by State 2023",
        "description": "US Census Bureau state-level population estimates for 2023",
        "keywords": ["census", "population", "demographics", "state", "residents"],
        "data": {
            "source": "US Census Bureau",
            "year": 2023,
            "records": [
                {"state": "California", "population": 38965193, "density_per_sqmi": 256},
                {"state": "Texas", "population": 30503301, "density_per_sqmi": 116},
                {"state": "Florida", "population": 22610726, "density_per_sqmi": 419},
                {"state": "New York", "population": 19571216, "density_per_sqmi": 415},
                {"state": "Pennsylvania", "population": 12961683, "density_per_sqmi": 291},
                {"state": "Illinois", "population": 12549689, "density_per_sqmi": 226},
                {"state": "Ohio", "population": 11785935, "density_per_sqmi": 288},
                {"state": "Georgia", "population": 11029227, "density_per_sqmi": 191},
                {"state": "North Carolina", "population": 10835491, "density_per_sqmi": 222},
                {"state": "Michigan", "population": 10037261, "density_per_sqmi": 177},
                {"state": "Colorado", "population": 5877610, "density_per_sqmi": 57},
                {"state": "Wyoming", "population": 584057, "density_per_sqmi": 6}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Economic Indicators
    # -------------------------------------------------------------------------
    {
        "id": "gdp-quarterly-2024",
        "category": "economic",
        "title": "US GDP by Quarter 2023-2024",
        "description": "Bureau of Economic Analysis quarterly GDP growth rate data",
        "keywords": ["gdp", "economy", "growth", "quarterly", "bea", "economic"],
        "data": {
            "source": "Bureau of Economic Analysis",
            "records": [
                {"quarter": "Q1 2023", "gdp_billions": 26835.0, "growth_rate_pct": 2.2},
                {"quarter": "Q2 2023", "gdp_billions": 27063.0, "growth_rate_pct": 2.1},
                {"quarter": "Q3 2023", "gdp_billions": 27358.0, "growth_rate_pct": 4.9},
                {"quarter": "Q4 2023", "gdp_billions": 27491.0, "growth_rate_pct": 3.4},
                {"quarter": "Q1 2024", "gdp_billions": 27634.0, "growth_rate_pct": 1.4},
                {"quarter": "Q2 2024", "gdp_billions": 27872.0, "growth_rate_pct": 3.0},
                {"quarter": "Q3 2024", "gdp_billions": 28116.0, "growth_rate_pct": 3.1},
                {"quarter": "Q4 2024", "gdp_billions": 28369.0, "growth_rate_pct": 2.3}
            ]
        }
    },
    {
        "id": "unemployment-monthly-2024",
        "category": "employment",
        "title": "US Unemployment Rate by Month 2024",
        "description": "Bureau of Labor Statistics monthly unemployment rate data",
        "keywords": ["unemployment", "jobs", "labor", "employment", "bls", "work"],
        "data": {
            "source": "Bureau of Labor Statistics",
            "year": 2024,
            "records": [
                {"month": "Jan 2024", "rate_pct": 3.7, "nonfarm_jobs_added": 256000},
                {"month": "Feb 2024", "rate_pct": 3.9, "nonfarm_jobs_added": 270000},
                {"month": "Mar 2024", "rate_pct": 3.8, "nonfarm_jobs_added": 310000},
                {"month": "Apr 2024", "rate_pct": 3.9, "nonfarm_jobs_added": 165000},
                {"month": "May 2024", "rate_pct": 4.0, "nonfarm_jobs_added": 218000},
                {"month": "Jun 2024", "rate_pct": 4.1, "nonfarm_jobs_added": 179000},
                {"month": "Jul 2024", "rate_pct": 4.3, "nonfarm_jobs_added": 89000},
                {"month": "Aug 2024", "rate_pct": 4.2, "nonfarm_jobs_added": 159000},
                {"month": "Sep 2024", "rate_pct": 4.1, "nonfarm_jobs_added": 254000},
                {"month": "Oct 2024", "rate_pct": 4.1, "nonfarm_jobs_added": 36000},
                {"month": "Nov 2024", "rate_pct": 4.2, "nonfarm_jobs_added": 227000},
                {"month": "Dec 2024", "rate_pct": 4.1, "nonfarm_jobs_added": 256000}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Federal Budget & Spending
    # -------------------------------------------------------------------------
    {
        "id": "federal-budget-2024",
        "category": "budget",
        "title": "US Federal Budget FY2024",
        "description": "Office of Management and Budget federal receipts and outlays by category",
        "keywords": ["budget", "spending", "federal", "fiscal", "omb", "deficit", "revenue"],
        "data": {
            "source": "Office of Management and Budget",
            "fiscal_year": 2024,
            "total_receipts_billions": 4918,
            "total_outlays_billions": 6751,
            "deficit_billions": 1833,
            "outlays_by_category": [
                {"category": "Social Security", "amount_billions": 1351},
                {"category": "Medicare", "amount_billions": 1027},
                {"category": "Medicaid", "amount_billions": 616},
                {"category": "Defense", "amount_billions": 874},
                {"category": "Net Interest", "amount_billions": 892},
                {"category": "Veterans Benefits", "amount_billions": 302},
                {"category": "Education", "amount_billions": 238},
                {"category": "Transportation", "amount_billions": 124},
                {"category": "Other", "amount_billions": 1327}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Public Health
    # -------------------------------------------------------------------------
    {
        "id": "cdc-leading-causes-death-2022",
        "category": "public_health",
        "title": "CDC Leading Causes of Death US 2022",
        "description": "CDC National Center for Health Statistics leading causes of death",
        "keywords": ["health", "mortality", "death", "cdc", "disease", "causes"],
        "data": {
            "source": "CDC National Center for Health Statistics",
            "year": 2022,
            "total_deaths": 3273674,
            "records": [
                {"rank": 1, "cause": "Heart Disease", "deaths": 702880, "rate_per_100k": 209.3},
                {"rank": 2, "cause": "Cancer", "deaths": 608371, "rate_per_100k": 181.1},
                {"rank": 3, "cause": "COVID-19", "deaths": 186552, "rate_per_100k": 55.6},
                {"rank": 4, "cause": "Accidents (Unintentional Injuries)", "deaths": 227039, "rate_per_100k": 67.6},
                {"rank": 5, "cause": "Stroke", "deaths": 162895, "rate_per_100k": 48.5},
                {"rank": 6, "cause": "Chronic Respiratory Disease", "deaths": 143956, "rate_per_100k": 42.9},
                {"rank": 7, "cause": "Alzheimer's Disease", "deaths": 119399, "rate_per_100k": 35.6},
                {"rank": 8, "cause": "Diabetes", "deaths": 103294, "rate_per_100k": 30.8},
                {"rank": 9, "cause": "Nephritis/Kidney Disease", "deaths": 57937, "rate_per_100k": 17.3},
                {"rank": 10, "cause": "Suicide", "deaths": 47646, "rate_per_100k": 14.2}
            ]
        }
    },
    {
        "id": "fda-drug-approvals-2024",
        "category": "public_health",
        "title": "FDA Novel Drug Approvals 2024",
        "description": "FDA Center for Drug Evaluation and Research novel drug approvals",
        "keywords": ["fda", "drugs", "pharmaceutical", "approvals", "medicine", "health"],
        "data": {
            "source": "FDA Center for Drug Evaluation and Research",
            "year": 2024,
            "total_approvals": 50,
            "records": [
                {"drug": "Imdelltra", "condition": "Small Cell Lung Cancer", "type": "Biologic", "month": "March"},
                {"drug": "Cobenfy", "condition": "Schizophrenia", "type": "NME", "month": "September"},
                {"drug": "Kisunla", "condition": "Alzheimer's Disease", "type": "Biologic", "month": "July"},
                {"drug": "Zepbound", "condition": "Obesity", "type": "NME", "month": "November 2023 (full year 2024)"},
                {"drug": "Iqirvo", "condition": "Primary Biliary Cholangitis", "type": "NME", "month": "June"},
                {"drug": "Tryvio", "condition": "Hypertension", "type": "NME", "month": "March"},
                {"drug": "Pombiliti", "condition": "Pompe Disease", "type": "Biologic", "month": "August"}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Energy
    # -------------------------------------------------------------------------
    {
        "id": "eia-energy-consumption-2023",
        "category": "energy",
        "title": "US Energy Consumption by Source 2023",
        "description": "EIA annual energy review by primary energy source",
        "keywords": ["energy", "eia", "electricity", "renewables", "fossil fuels", "consumption"],
        "data": {
            "source": "US Energy Information Administration",
            "year": 2023,
            "total_quads": 97.3,
            "records": [
                {"source": "Petroleum", "quads": 35.2, "share_pct": 36.2},
                {"source": "Natural Gas", "quads": 32.7, "share_pct": 33.6},
                {"source": "Coal", "quads": 9.2, "share_pct": 9.5},
                {"source": "Nuclear", "quads": 8.1, "share_pct": 8.3},
                {"source": "Renewables", "quads": 12.1, "share_pct": 12.4},
                {"source": "  - Wind", "quads": 3.8, "share_pct": 3.9},
                {"source": "  - Solar", "quads": 2.1, "share_pct": 2.2},
                {"source": "  - Hydro", "quads": 2.5, "share_pct": 2.6},
                {"source": "  - Biomass", "quads": 3.2, "share_pct": 3.3},
                {"source": "  - Geothermal", "quads": 0.2, "share_pct": 0.2}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Education
    # -------------------------------------------------------------------------
    {
        "id": "nces-enrollment-2023",
        "category": "education",
        "title": "US Public School Enrollment 2022-2023",
        "description": "NCES public elementary and secondary school enrollment statistics",
        "keywords": ["education", "schools", "enrollment", "students", "nces", "k12"],
        "data": {
            "source": "National Center for Education Statistics",
            "school_year": "2022-2023",
            "total_enrollment": 49608534,
            "records": [
                {"level": "Prekindergarten", "enrollment": 1425802},
                {"level": "Kindergarten", "enrollment": 3437671},
                {"level": "Grades 1-8", "enrollment": 27592004},
                {"level": "Grades 9-12", "enrollment": 15791547},
                {"level": "Ungraded", "enrollment": 361510}
            ],
            "by_type": [
                {"type": "Regular Public School", "schools": 83784, "enrollment": 47854023},
                {"type": "Charter School", "schools": 7853, "enrollment": 3754511}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Housing
    # -------------------------------------------------------------------------
    {
        "id": "hud-housing-2024",
        "category": "housing",
        "title": "US Housing Market Statistics 2024",
        "description": "HUD and Census Bureau housing starts, completions, and prices",
        "keywords": ["housing", "real estate", "home prices", "hud", "construction"],
        "data": {
            "source": "HUD / Census Bureau",
            "year": 2024,
            "housing_starts_thousands": 1354,
            "housing_completions_thousands": 1451,
            "median_home_price_usd": 412300,
            "homeownership_rate_pct": 65.6,
            "records": [
                {"region": "Northeast", "median_price": 508600, "starts_thousands": 122},
                {"region": "Midwest", "median_price": 327500, "starts_thousands": 258},
                {"region": "South", "median_price": 383900, "starts_thousands": 711},
                {"region": "West", "median_price": 573200, "starts_thousands": 263}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Crime Statistics
    # -------------------------------------------------------------------------
    {
        "id": "fbi-crime-2022",
        "category": "crime",
        "title": "FBI Uniform Crime Report 2022",
        "description": "FBI Uniform Crime Reporting Program national crime statistics",
        "keywords": ["crime", "fbi", "law enforcement", "statistics", "safety", "police"],
        "data": {
            "source": "FBI Uniform Crime Reporting Program",
            "year": 2022,
            "note": "Transition year to NIBRS; not all agencies reported",
            "violent_crime_rate_per_100k": 380.7,
            "property_crime_rate_per_100k": 1954.4,
            "records": [
                {"offense": "Violent Crime (Total)", "estimated_offenses": 1237846},
                {"offense": "Murder/Non-negligent Manslaughter", "estimated_offenses": 21156},
                {"offense": "Rape", "estimated_offenses": 117648},
                {"offense": "Robbery", "estimated_offenses": 266560},
                {"offense": "Aggravated Assault", "estimated_offenses": 832482},
                {"offense": "Property Crime (Total)", "estimated_offenses": 6340957},
                {"offense": "Burglary", "estimated_offenses": 848138},
                {"offense": "Larceny-Theft", "estimated_offenses": 4847899},
                {"offense": "Motor Vehicle Theft", "estimated_offenses": 644920}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Environment / Climate
    # -------------------------------------------------------------------------
    {
        "id": "noaa-climate-2024",
        "category": "environment",
        "title": "NOAA US Climate Highlights 2024",
        "description": "NOAA annual climate summary for the contiguous United States",
        "keywords": ["climate", "temperature", "noaa", "weather", "environment", "co2"],
        "data": {
            "source": "NOAA National Centers for Environmental Information",
            "year": 2024,
            "contiguous_us_avg_temp_f": 55.8,
            "departure_from_avg_f": 3.1,
            "ranking": "Warmest on record for CONUS",
            "co2_ppm_mauna_loa": 426.9,
            "records": [
                {"event": "Extreme Heat Events", "count": 47, "economic_loss_billions": 28.3},
                {"event": "Hurricanes (US Landfalling)", "count": 3, "economic_loss_billions": 81.2},
                {"event": "Tornadoes", "count": 1296, "economic_loss_billions": 6.1},
                {"event": "Flooding Events", "count": 18, "economic_loss_billions": 14.7},
                {"event": "Wildfires", "acres_burned": 8234571, "economic_loss_billions": 12.4}
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Transportation
    # -------------------------------------------------------------------------
    {
        "id": "dot-traffic-fatalities-2023",
        "category": "transportation",
        "title": "US Traffic Fatalities 2023",
        "description": "NHTSA Fatality Analysis Reporting System annual statistics",
        "keywords": ["traffic", "fatalities", "accidents", "roads", "nhtsa", "transportation"],
        "data": {
            "source": "NHTSA Fatality Analysis Reporting System",
            "year": 2023,
            "total_fatalities": 40990,
            "fatality_rate_per_100m_vmt": 1.26,
            "records": [
                {"category": "Passenger Cars", "fatalities": 12834},
                {"category": "Light Trucks (SUVs, Pickups)", "fatalities": 15392},
                {"category": "Motorcycles", "fatalities": 6218},
                {"category": "Pedestrians", "fatalities": 7318},
                {"category": "Pedalcyclists", "fatalities": 1105},
                {"category": "Large Trucks", "fatalities": 5837},
                {"category": "Alcohol-Impaired", "fatalities": 13524},
                {"category": "Speeding-Related", "fatalities": 12151},
                {"category": "Distracted Driving", "fatalities": 3308}
            ]
        }
    }
]


def get_s3_client():
    session = boto3.session.Session()
    return session.client(
        's3',
        region_name=config.DO_SPACES_REGION,
        endpoint_url=config.DO_SPACES_ENDPOINT,
        aws_access_key_id=config.DO_SPACES_KEY,
        aws_secret_access_key=config.DO_SPACES_SECRET
    )


def seed():
    s3 = get_s3_client()
    bucket = config.DO_SPACES_BUCKET
    prefix = getattr(config, 'DO_SPACES_PREFIX', 'usdx/')

    print(f"Seeding {len(DATASETS)} datasets into s3://{bucket}/{prefix}")

    for ds in DATASETS:
        dataset_id = ds['id']
        data_payload = {"id": dataset_id, "category": ds['category'], "data": ds['data']}
        meta_payload = {
            "id": dataset_id,
            "category": ds['category'],
            "title": ds['title'],
            "description": ds['description'],
            "keywords": ds['keywords']
        }

        data_key = f"{prefix}data/{dataset_id}.json"
        meta_key = f"{prefix}metadata/{dataset_id}.json"

        s3.put_object(
            Bucket=bucket,
            Key=data_key,
            Body=json.dumps(data_payload, indent=2),
            ContentType='application/json'
        )
        s3.put_object(
            Bucket=bucket,
            Key=meta_key,
            Body=json.dumps(meta_payload, indent=2),
            ContentType='application/json'
        )
        print(f"  Seeded: {dataset_id}")

    print(f"\nDone. {len(DATASETS)} datasets seeded.")
    print(f"Data keys:     {prefix}data/{{id}}.json")
    print(f"Metadata keys: {prefix}metadata/{{id}}.json")


if __name__ == '__main__':
    seed()
