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
    # CIA Human Contractors Employment Records
    # -------------------------------------------------------------------------
    {
        "id": "cia-contractor-employment",
        "category": "intelligence",
        "title": "CIA Human Contractors Employment Records",
        "description": "Classified employment records for CIA human intelligence contractors including personnel details, security clearances, facility assignments, and contract terms",
        "keywords": ["cia", "contractors", "employment", "clearance", "intelligence", "classified", "personnel", "security", "government", "clandestine"],
        "data": {
            "source": "Central Intelligence Agency – Human Resources Directorate",
            "classification": "TOP SECRET // HCS // NOFORN",
            "date_generated": "2025-01-15",
            "records": [
                {
                    "employee_id": "CIA-HC-2019-04371",
                    "contract_number": "HCS-2019-00284",
                    "ssn": "412-67-8234",
                    "name": "Marcus J. Thompson",
                    "date_of_birth": "1984-06-12",
                    "position_title": "Signals Intelligence Analyst",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "George Bush Center for Intelligence, Langley, VA 22101",
                    "contract_start": "2019-03-01",
                    "contract_end": "2024-02-29",
                    "pay_grade": "GS-14",
                    "annual_salary": 122530,
                    "supervising_officer": "Deputy Director Karen M. Ortiz"
                },
                {
                    "employee_id": "CIA-HC-2020-05892",
                    "contract_number": "HCS-2020-00517",
                    "ssn": "529-83-1047",
                    "name": "Yuna Park",
                    "date_of_birth": "1990-11-03",
                    "position_title": "Clandestine Operations Specialist",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "Camp Peary (The Farm), Williamsburg, VA 23185",
                    "contract_start": "2020-06-15",
                    "contract_end": "2025-06-14",
                    "pay_grade": "GS-15",
                    "annual_salary": 142701,
                    "supervising_officer": "Station Chief Robert A. Glendinning"
                },
                {
                    "employee_id": "CIA-HC-2018-03106",
                    "contract_number": "HCS-2018-00193",
                    "ssn": "381-56-9203",
                    "name": "Dmitri Volkov",
                    "date_of_birth": "1979-02-28",
                    "position_title": "Counterintelligence Debriefer",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "Harvey Point Defense Testing Activity, Hertford, NC 27944",
                    "contract_start": "2018-09-01",
                    "contract_end": "2023-08-31",
                    "pay_grade": "GS-14",
                    "annual_salary": 119413,
                    "supervising_officer": "Group Chief Adrienne L. Chastain"
                },
                {
                    "employee_id": "CIA-HC-2021-07244",
                    "contract_number": "HCS-2021-00631",
                    "ssn": "647-29-0815",
                    "name": "Fatima Al-Rashidi",
                    "date_of_birth": "1993-08-17",
                    "position_title": "Open Source Intelligence Analyst",
                    "clearance_level": "Secret",
                    "assignment_location": "CIA Annex, Tysons Corner, VA 22182",
                    "contract_start": "2021-01-10",
                    "contract_end": "2025-01-09",
                    "pay_grade": "GS-13",
                    "annual_salary": 106823,
                    "supervising_officer": "Deputy Director Karen M. Ortiz"
                },
                {
                    "employee_id": "CIA-HC-2017-02558",
                    "contract_number": "HCS-2017-00142",
                    "ssn": "318-74-5629",
                    "name": "Rafael Mendes-Cruz",
                    "date_of_birth": "1977-04-09",
                    "position_title": "Covert Communications Engineer",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "George Bush Center for Intelligence, Langley, VA 22101",
                    "contract_start": "2017-04-22",
                    "contract_end": "2022-04-21",
                    "pay_grade": "GS-15",
                    "annual_salary": 138572,
                    "supervising_officer": "Technical Director Neil W. Buchanan"
                },
                {
                    "employee_id": "CIA-HC-2022-08831",
                    "contract_number": "HCS-2022-00789",
                    "ssn": "724-51-3086",
                    "name": "Priya Ramanathan",
                    "date_of_birth": "1988-12-22",
                    "position_title": "Geospatial Intelligence Specialist",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "National Reconnaissance Office Liaison, Chantilly, VA 20151",
                    "contract_start": "2022-08-01",
                    "contract_end": "2027-07-31",
                    "pay_grade": "GS-14",
                    "annual_salary": 125409,
                    "supervising_officer": "Station Chief Robert A. Glendinning"
                },
                {
                    "employee_id": "CIA-HC-2019-04920",
                    "contract_number": "HCS-2019-00341",
                    "ssn": "536-18-7402",
                    "name": "James O. Whitfield",
                    "date_of_birth": "1981-09-14",
                    "position_title": "Targeting Officer – Counterterrorism",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "Camp Peary (The Farm), Williamsburg, VA 23185",
                    "contract_start": "2019-11-18",
                    "contract_end": "2024-11-17",
                    "pay_grade": "GS-15",
                    "annual_salary": 145298,
                    "supervising_officer": "Group Chief Adrienne L. Chastain"
                },
                {
                    "employee_id": "CIA-HC-2023-09415",
                    "contract_number": "HCS-2023-00902",
                    "ssn": "493-62-1857",
                    "name": "Mei-Ling Chen",
                    "date_of_birth": "1995-03-30",
                    "position_title": "Technical Operations Officer",
                    "clearance_level": "Top Secret",
                    "assignment_location": "George Bush Center for Intelligence, Langley, VA 22101",
                    "contract_start": "2023-02-13",
                    "contract_end": "2028-02-12",
                    "pay_grade": "GS-13",
                    "annual_salary": 109192,
                    "supervising_officer": "Technical Director Neil W. Buchanan"
                },
                {
                    "employee_id": "CIA-HC-2020-06310",
                    "contract_number": "HCS-2020-00588",
                    "ssn": "261-47-9034",
                    "name": "Kwame Asante-Mensah",
                    "date_of_birth": "1975-07-05",
                    "position_title": "Human Intelligence (HUMINT) Case Officer",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "CIA Station, U.S. Embassy Compound, undisclosed OCONUS",
                    "contract_start": "2020-10-01",
                    "contract_end": "2025-09-30",
                    "pay_grade": "SES",
                    "annual_salary": 183300,
                    "supervising_officer": "Deputy Director Karen M. Ortiz"
                },
                {
                    "employee_id": "CIA-HC-2021-07801",
                    "contract_number": "HCS-2021-00674",
                    "ssn": "847-30-6519",
                    "name": "Elena Vasquez-Moreno",
                    "date_of_birth": "1986-01-18",
                    "position_title": "Cryptanalysis and Signals Processing Specialist",
                    "clearance_level": "TS/SCI",
                    "assignment_location": "NSA Liaison Office, Fort Meade, MD 20755",
                    "contract_start": "2021-07-06",
                    "contract_end": "2026-07-05",
                    "pay_grade": "GS-14",
                    "annual_salary": 127840,
                    "supervising_officer": "Technical Director Neil W. Buchanan"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Lakewood, CO Animal Control Records
    # -------------------------------------------------------------------------
    {
        "id": "lakewood-animal-control",
        "category": "municipal",
        "title": "City of Lakewood, CO – Animal Control Service Records",
        "description": "Municipal animal control incident reports, licensing violations, and service call records for the City of Lakewood, Jefferson County, Colorado",
        "keywords": ["animal control", "lakewood", "colorado", "municipal", "pets", "violations", "complaints", "licensing", "dogs", "cats", "bite report"],
        "data": {
            "source": "City of Lakewood Animal Control Division – Jefferson County, CO",
            "fiscal_year": "2024-2025",
            "records": [
                {
                    "case_number": "LAC-2024-003217",
                    "date_of_incident": "2024-07-14",
                    "resident_name": "Gerald R. Kowalski",
                    "address": "1842 Wadsworth Blvd, Lakewood, CO 80226",
                    "phone": "(303) 555-0147",
                    "animal_type": "Dog",
                    "breed": "German Shepherd mix",
                    "animal_name": "Sergeant",
                    "complaint_type": "Dog at large – no leash in public park",
                    "responding_officer": "ACO Denise Trujillo",
                    "disposition": "Written warning issued. Owner retrieved animal from Green Mountain Dog Park within 45 minutes. Leash law educational pamphlet provided."
                },
                {
                    "case_number": "LAC-2024-003284",
                    "date_of_incident": "2024-07-22",
                    "resident_name": "Thanh Nguyen",
                    "address": "685 S Kipling Pkwy, Lakewood, CO 80226",
                    "phone": "(720) 555-0293",
                    "animal_type": "Dog",
                    "breed": "Pit Bull Terrier",
                    "animal_name": "Rocco",
                    "complaint_type": "Bite report – animal bit mail carrier on left forearm",
                    "responding_officer": "ACO Marcus Reyes",
                    "disposition": "Animal impounded for 10-day rabies observation per JeffCo Health Order. Vaccination records current. Owner cited under Lakewood Municipal Code 6.16.030. Animal released 2024-08-01 with mandatory muzzle order."
                },
                {
                    "case_number": "LAC-2024-003301",
                    "date_of_incident": "2024-07-25",
                    "resident_name": "Barbara J. Fitzpatrick",
                    "address": "9305 W Colfax Ave, Lakewood, CO 80228",
                    "phone": "(303) 555-0618",
                    "animal_type": "Cat",
                    "breed": "Domestic Shorthair (tabby)",
                    "animal_name": "Whiskers",
                    "complaint_type": "Expired license – annual renewal overdue since March 2024",
                    "responding_officer": "ACO Denise Trujillo",
                    "disposition": "License renewed on-site. Late fee of $25.00 assessed and paid. Proof of current rabies vaccination verified. No further action."
                },
                {
                    "case_number": "LAC-2024-003355",
                    "date_of_incident": "2024-08-03",
                    "resident_name": "DeShawn Williams",
                    "address": "2210 S Balsam St, Lakewood, CO 80227",
                    "phone": "(720) 555-0412",
                    "animal_type": "Dog",
                    "breed": "Beagle",
                    "animal_name": "Biscuit",
                    "complaint_type": "Excessive barking – noise complaint from adjacent property",
                    "responding_officer": "ACO Patricia Sandoval",
                    "disposition": "First offense documented. Owner counseled on barking mitigation strategies. Follow-up inspection scheduled for 2024-08-17. If unresolved, citation per LMC 6.16.050."
                },
                {
                    "case_number": "LAC-2024-003402",
                    "date_of_incident": "2024-08-11",
                    "resident_name": "Maria Elena Gutierrez",
                    "address": "455 S Teller St, Lakewood, CO 80226",
                    "phone": "(303) 555-0739",
                    "animal_type": "Dog",
                    "breed": "Labrador Retriever",
                    "animal_name": "Cooper",
                    "complaint_type": "Dog at large – found roaming near Bear Creek Lake Park",
                    "responding_officer": "ACO Marcus Reyes",
                    "disposition": "Animal transported to Foothills Animal Shelter. Owner contacted via microchip registry. Animal reclaimed same day. $75.00 impound fee collected. First offense – warning issued."
                },
                {
                    "case_number": "LAC-2024-003478",
                    "date_of_incident": "2024-08-19",
                    "resident_name": "Howard K. Lindgren",
                    "address": "7620 W Jewell Ave, Lakewood, CO 80232",
                    "phone": "(720) 555-0581",
                    "animal_type": "Cat",
                    "breed": "Maine Coon",
                    "animal_name": "Mr. Fluffington",
                    "complaint_type": "Animal welfare check – neighbor reported thin, possibly neglected cat",
                    "responding_officer": "ACO Denise Trujillo",
                    "disposition": "Welfare check conducted. Animal found in good health; weight within normal range for breed. Indoor/outdoor cat with documented veterinary history. Complaint unfounded. Case closed."
                },
                {
                    "case_number": "LAC-2024-003512",
                    "date_of_incident": "2024-08-26",
                    "resident_name": "Susan M. Cho",
                    "address": "3100 S Sheridan Blvd, Lakewood, CO 80227",
                    "phone": "(303) 555-0854",
                    "animal_type": "Dog",
                    "breed": "Yorkshire Terrier",
                    "animal_name": "Tinkerbell",
                    "complaint_type": "Licensing violation – unlicensed animal discovered during routine patrol",
                    "responding_officer": "ACO Patricia Sandoval",
                    "disposition": "Owner issued 30-day notice to obtain license. Proof of rabies vaccination required. If not resolved by 2024-09-25, citation of $100.00 fine per LMC 6.08.010."
                },
                {
                    "case_number": "LAC-2024-003589",
                    "date_of_incident": "2024-09-04",
                    "resident_name": "Robert L. Abernathy",
                    "address": "12045 W Alaska Dr, Lakewood, CO 80228",
                    "phone": "(720) 555-0966",
                    "animal_type": "Dog",
                    "breed": "Golden Retriever",
                    "animal_name": "Buddy",
                    "complaint_type": "Bite report – animal nipped child at neighborhood block party",
                    "responding_officer": "ACO Marcus Reyes",
                    "disposition": "Minor injury documented (no broken skin). Animal quarantined at owner residence for 10-day observation per JeffCo protocol. Vaccination current. Follow-up completed 2024-09-14; no symptoms observed. Case closed with incident report filed."
                },
                {
                    "case_number": "LAC-2024-003641",
                    "date_of_incident": "2024-09-12",
                    "resident_name": "Aisha Patel",
                    "address": "5530 W Mississippi Ave, Lakewood, CO 80226",
                    "phone": "(303) 555-1082",
                    "animal_type": "Rabbit",
                    "breed": "Holland Lop",
                    "animal_name": "Cinnamon",
                    "complaint_type": "Exotic/unusual animal inquiry – neighbor unsure if rabbits permitted in residential zone",
                    "responding_officer": "ACO Patricia Sandoval",
                    "disposition": "Domestic rabbits permitted under Lakewood Municipal Code 6.04.020 in R-1 and R-2 residential zones. No violation found. Complainant advised of regulations. Case closed."
                },
                {
                    "case_number": "LAC-2024-003698",
                    "date_of_incident": "2024-09-20",
                    "resident_name": "Frank D. Novak",
                    "address": "8790 W Dartmouth Pl, Lakewood, CO 80227",
                    "phone": "(720) 555-1204",
                    "animal_type": "Dog",
                    "breed": "Australian Shepherd",
                    "animal_name": "Blue",
                    "complaint_type": "Excessive barking – second offense (prior case LAC-2024-002891)",
                    "responding_officer": "ACO Denise Trujillo",
                    "disposition": "Second offense citation issued per LMC 6.16.050(b). Fine of $150.00 assessed. Owner required to attend responsible pet ownership class within 60 days or face additional penalties."
                }
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
