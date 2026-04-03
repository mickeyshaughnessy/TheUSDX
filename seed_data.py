"""
Seed federal datasets into DO Spaces for TheUSDX.

Run once (or after adding datasets) to populate usdx/data/ and usdx/metadata/.
After seeding, collect_data() in handlers.py will match real datasets.

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
        "keywords": ["cia", "contractors", "employment", "clearance", "intelligence", "classified", "personnel", "security", "clandestine", "humint"],
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
                    "disposition": "First offense documented. Owner counseled on barking mitigation strategies. Follow-up inspection scheduled for 2024-08-17."
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
                    "disposition": "Second offense citation issued per LMC 6.16.050(b). Fine of $150.00 assessed. Owner required to attend responsible pet ownership class within 60 days."
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # NSA SIGINT Foreign Target Surveillance Records
    # -------------------------------------------------------------------------
    {
        "id": "nsa-sigint-foreign-surveillance",
        "category": "intelligence",
        "title": "NSA SIGINT Foreign Target Surveillance Records",
        "description": "National Security Agency signals intelligence collection records for designated foreign intelligence targets under FISA Section 702 and Executive Order 12333",
        "keywords": ["NSA", "SIGINT", "surveillance", "foreign intelligence", "FISA", "intercept", "EO 12333", "wiretap", "collection", "comms", "foreign nationals"],
        "data": {
            "source": "National Security Agency – Special Source Operations Directorate",
            "classification": "TOP SECRET // COMINT // NOFORN",
            "legal_authority": "50 U.S.C. § 1881a (FISA § 702); Executive Order 12333",
            "date_generated": "2025-03-01",
            "records": [
                {
                    "target_id": "NSA-TGT-2024-00412",
                    "collection_program": "PRISM",
                    "target_name": "Aleksandr Nikolaevich Petrov",
                    "target_nationality": "Russian Federation",
                    "target_affiliation": "Federal Security Service (FSB), 16th Directorate",
                    "selector": "+7-495-638-4421",
                    "intercept_date": "2024-09-14",
                    "collection_facility": "BLARNEY",
                    "content_summary": "Subject communicated with designated contact regarding financial routing through Cyprus-based shell entities. Cryptonym CARDINAL referenced as intermediary.",
                    "analyst_id": "SSG-4417",
                    "classification_reason": "1.4(c) intelligence activities, sources and methods"
                },
                {
                    "target_id": "NSA-TGT-2024-00589",
                    "collection_program": "MUSCULAR",
                    "target_name": "Wei Jianming",
                    "target_nationality": "People's Republic of China",
                    "target_affiliation": "Ministry of State Security (MSS), Technical Reconnaissance Bureau",
                    "selector": "wei.jm.tech@protonmail.com",
                    "intercept_date": "2024-10-02",
                    "collection_facility": "STORMBREW",
                    "content_summary": "Encrypted communication referencing semiconductor acquisition network operating through front companies in Taiwan and Singapore. Specific targets include defense contractor supply chains.",
                    "analyst_id": "SSG-3802",
                    "classification_reason": "1.4(c) intelligence activities; 1.4(d) foreign relations"
                },
                {
                    "target_id": "NSA-TGT-2024-00631",
                    "collection_program": "UPSTREAM",
                    "target_name": "Hamza al-Tunisi",
                    "target_nationality": "Tunisia",
                    "target_affiliation": "Designated Foreign Terrorist Organization – associate network",
                    "selector": "+216-71-443-887",
                    "intercept_date": "2024-10-18",
                    "collection_facility": "FAIRVIEW",
                    "content_summary": "Communications with known facilitation network in Western Europe regarding logistics coordination. References to travel documents and financial transfers flagged by TECS.",
                    "analyst_id": "SSG-5119",
                    "classification_reason": "1.4(c) intelligence activities; 1.4(a) military plans"
                },
                {
                    "target_id": "NSA-TGT-2024-00704",
                    "collection_program": "PRISM",
                    "target_name": "Irina Voloshyn",
                    "target_nationality": "Ukraine (GRU-affiliated)",
                    "target_affiliation": "Russian Military Intelligence (GRU), Unit 26165",
                    "selector": "ivoloshyn84@yandex.ru",
                    "intercept_date": "2024-11-05",
                    "collection_facility": "BLARNEY",
                    "content_summary": "Email traffic indicating coordination on influence operation targeting upcoming European parliamentary elections. References to social media persona management infrastructure.",
                    "analyst_id": "SSG-4417",
                    "classification_reason": "1.4(c) intelligence activities; 1.4(d) foreign relations"
                },
                {
                    "target_id": "NSA-TGT-2024-00812",
                    "collection_program": "MUSCULAR",
                    "target_name": "Reza Mohammadi-Tabriz",
                    "target_nationality": "Islamic Republic of Iran",
                    "target_affiliation": "Islamic Revolutionary Guard Corps (IRGC) – Quds Force, Finance Directorate",
                    "selector": "+98-21-8847-3391",
                    "intercept_date": "2024-11-22",
                    "collection_facility": "STORMBREW",
                    "content_summary": "Financial coordination traffic referencing petroleum-for-weapons barter arrangement. Named intermediary institution subject to pending OFAC designation.",
                    "analyst_id": "SSG-3802",
                    "classification_reason": "1.4(c) intelligence activities; 1.4(b) weapons of mass destruction"
                },
                {
                    "target_id": "NSA-TGT-2024-00901",
                    "collection_program": "UPSTREAM",
                    "target_name": "Pyotr Sorokin",
                    "target_nationality": "Russian Federation",
                    "target_affiliation": "SVR RF (Foreign Intelligence Service), North American Division",
                    "selector": "+1-571-304-8847",
                    "intercept_date": "2024-12-09",
                    "collection_facility": "FAIRVIEW",
                    "content_summary": "VOIP communication with undisclosed domestic contact. Discussion of technology transfer opportunity at Northern Virginia defense firm. Case referred to FBI Counterintelligence Division.",
                    "analyst_id": "SSG-5119",
                    "classification_reason": "1.4(c) intelligence activities; 1.4(d) foreign relations"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # US Army 82nd Airborne Division Deployment Orders
    # -------------------------------------------------------------------------
    {
        "id": "army-82nd-airborne-deployment",
        "category": "military",
        "title": "US Army 82nd Airborne Division – Personnel Deployment Orders",
        "description": "Individual deployment orders and personnel records for 82nd Airborne Division soldiers assigned to overseas contingency operations",
        "keywords": ["army", "military", "deployment", "82nd airborne", "soldiers", "overseas", "contingency", "orders", "personnel", "combat"],
        "data": {
            "source": "Department of the Army – G-1 Personnel Directorate, XVIII Airborne Corps",
            "classification": "SECRET // NOFORN",
            "date_generated": "2025-02-10",
            "records": [
                {
                    "service_record_number": "AR-82ABN-2024-10041",
                    "ssn": "287-54-6103",
                    "name": "Staff Sergeant Leon D. Hargrove",
                    "date_of_birth": "1993-04-17",
                    "home_address": "4412 Bragg Blvd, Fayetteville, NC 28303",
                    "rank": "E-6 (Staff Sergeant)",
                    "mos": "11B – Infantryman",
                    "unit": "1st Brigade Combat Team, 82nd Airborne Division",
                    "deployment_destination": "CENTCOM AOR – classified forward operating location",
                    "deployment_start": "2024-09-01",
                    "deployment_end": "2025-03-01",
                    "mission_type": "Classified contingency operation",
                    "security_clearance": "Secret",
                    "emergency_contact": "Patricia Hargrove, (910) 555-0284"
                },
                {
                    "service_record_number": "AR-82ABN-2024-10078",
                    "ssn": "349-61-8820",
                    "name": "Captain Aaliyah M. Washington",
                    "date_of_birth": "1988-11-30",
                    "home_address": "218 Longstreet Ave, Fayetteville, NC 28301",
                    "rank": "O-3 (Captain)",
                    "mos": "13A – Field Artillery Officer",
                    "unit": "2nd Brigade Combat Team, 82nd Airborne Division",
                    "deployment_destination": "EUCOM AOR – classified forward staging area",
                    "deployment_start": "2024-10-15",
                    "deployment_end": "2025-04-14",
                    "mission_type": "Classified contingency operation",
                    "security_clearance": "Top Secret",
                    "emergency_contact": "Marcus Washington, (910) 555-0619"
                },
                {
                    "service_record_number": "AR-82ABN-2024-10112",
                    "ssn": "512-78-3047",
                    "name": "Specialist Diego Ramirez-Vega",
                    "date_of_birth": "1999-07-04",
                    "home_address": "831 Owen Dr, Fayetteville, NC 28304",
                    "rank": "E-4 (Specialist)",
                    "mos": "68W – Combat Medic",
                    "unit": "407th Brigade Support Battalion, 82nd Airborne Division",
                    "deployment_destination": "AFRICOM AOR – classified forward operating location",
                    "deployment_start": "2024-11-01",
                    "deployment_end": "2025-05-01",
                    "mission_type": "Classified contingency operation",
                    "security_clearance": "Secret",
                    "emergency_contact": "Carmen Vega, (910) 555-0833"
                },
                {
                    "service_record_number": "AR-82ABN-2024-10155",
                    "ssn": "683-29-5174",
                    "name": "Sergeant First Class James T. Okafor",
                    "date_of_birth": "1985-02-22",
                    "home_address": "1709 Cliffdale Rd, Fayetteville, NC 28314",
                    "rank": "E-7 (Sergeant First Class)",
                    "mos": "18C – Special Forces Engineer Sergeant",
                    "unit": "3rd Special Forces Group (Airborne)",
                    "deployment_destination": "SOCOM – compartmented assignment location",
                    "deployment_start": "2024-08-15",
                    "deployment_end": "2025-02-14",
                    "mission_type": "Classified special operations",
                    "security_clearance": "TS/SCI",
                    "emergency_contact": "Ngozi Okafor, (910) 555-0447"
                },
                {
                    "service_record_number": "AR-82ABN-2024-10198",
                    "ssn": "431-85-2069",
                    "name": "Private First Class Mei-Shan Liu",
                    "date_of_birth": "2001-09-11",
                    "home_address": "5521 Yadkin Rd, Fayetteville, NC 28303",
                    "rank": "E-3 (Private First Class)",
                    "mos": "25U – Signal Support Systems Specialist",
                    "unit": "82nd Combat Aviation Brigade",
                    "deployment_destination": "INDOPACOM AOR – classified forward operating location",
                    "deployment_start": "2025-01-10",
                    "deployment_end": "2025-07-09",
                    "mission_type": "Classified contingency operation",
                    "security_clearance": "Secret",
                    "emergency_contact": "Lin Liu, (910) 555-0972"
                },
                {
                    "service_record_number": "AR-82ABN-2024-10241",
                    "ssn": "594-37-8813",
                    "name": "Sergeant Tomasz Kowalczyk",
                    "date_of_birth": "1991-05-08",
                    "home_address": "342 Reilly Rd, Fayetteville, NC 28304",
                    "rank": "E-5 (Sergeant)",
                    "mos": "35F – Intelligence Analyst",
                    "unit": "82nd Airborne Division Artillery (DIVARTY)",
                    "deployment_destination": "EUCOM AOR – classified forward staging area",
                    "deployment_start": "2024-10-15",
                    "deployment_end": "2025-04-14",
                    "mission_type": "Classified intelligence support",
                    "security_clearance": "Top Secret",
                    "emergency_contact": "Anna Kowalczyk, (910) 555-0381"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # ICE Immigration Detention Records
    # -------------------------------------------------------------------------
    {
        "id": "ice-immigration-detention",
        "category": "immigration",
        "title": "ICE Enforcement and Removal Operations – Detention Records",
        "description": "U.S. Immigration and Customs Enforcement detention and removal records for individuals in immigration proceedings, including charges, facility assignments, and case status",
        "keywords": ["ICE", "immigration", "detention", "deportation", "removal", "alien", "ERO", "illegal entry", "asylum", "visa overstay", "CBP"],
        "data": {
            "source": "U.S. Immigration and Customs Enforcement – Enforcement and Removal Operations (ERO)",
            "fiscal_year": "2024",
            "records": [
                {
                    "case_number": "ERO-2024-ATL-04821",
                    "alien_registration_number": "A094-218-731",
                    "name": "Jose Luis Hernandez-Morales",
                    "country_of_origin": "Guatemala",
                    "date_of_birth": "1987-03-14",
                    "home_address_us": "2241 Buford Hwy NE, Apt 4B, Atlanta, GA 30329",
                    "phone": "(404) 555-0391",
                    "detention_facility": "Stewart Detention Center, Lumpkin, GA",
                    "detention_start": "2024-06-18",
                    "charges": "8 U.S.C. § 1325 – Improper Entry; prior removal order 2019",
                    "case_status": "Final order of removal issued; appeal pending 11th Circuit",
                    "immigration_judge": "IJ Carlos Restrepo, Atlanta Immigration Court",
                    "attorney_of_record": "Legal Aid Atlanta – pro bono representation"
                },
                {
                    "case_number": "ERO-2024-LAX-07334",
                    "alien_registration_number": "A107-554-890",
                    "name": "Amara Diallo",
                    "country_of_origin": "Guinea",
                    "date_of_birth": "1995-08-22",
                    "home_address_us": "8814 Vermont Ave, Los Angeles, CA 90044",
                    "phone": "(323) 555-0748",
                    "detention_facility": "Adelanto ICE Processing Center, Adelanto, CA",
                    "detention_start": "2024-07-03",
                    "charges": "8 U.S.C. § 1227(a)(1)(B) – Visa overstay (F-1 student visa expired 2022)",
                    "case_status": "Removal hearing scheduled 2025-02-14",
                    "immigration_judge": "IJ Sandra Park, Los Angeles Immigration Court",
                    "attorney_of_record": "ACLU Foundation of Southern California"
                },
                {
                    "case_number": "ERO-2024-ORD-02917",
                    "alien_registration_number": "A088-673-412",
                    "name": "Mykola Petrenko",
                    "country_of_origin": "Ukraine",
                    "date_of_birth": "1979-11-05",
                    "home_address_us": "1144 N Western Ave, Chicago, IL 60622",
                    "phone": "(773) 555-0512",
                    "detention_facility": "Dodge County Detention Facility (ICE contract), Juneau, WI",
                    "detention_start": "2024-08-14",
                    "charges": "8 U.S.C. § 1227(a)(2)(A)(iii) – Aggravated felony conviction (identity fraud, 2023)",
                    "case_status": "Order of removal issued; humanitarian stay request filed",
                    "immigration_judge": "IJ Michael Torres, Chicago Immigration Court",
                    "attorney_of_record": "National Immigrant Justice Center"
                },
                {
                    "case_number": "ERO-2024-MIA-11002",
                    "alien_registration_number": "A119-341-068",
                    "name": "Yordany Castillo-Reyes",
                    "country_of_origin": "Cuba",
                    "date_of_birth": "1991-04-30",
                    "home_address_us": "7201 SW 8th St, Miami, FL 33144",
                    "phone": "(305) 555-0867",
                    "detention_facility": "Krome North Service Processing Center, Miami, FL",
                    "detention_start": "2024-09-01",
                    "charges": "Credible fear screening passed; affirmative asylum application pending",
                    "case_status": "Asylum interview scheduled; parole request under review",
                    "immigration_judge": "IJ Natalie Chen, Miami Immigration Court",
                    "attorney_of_record": "Florida Immigrant Advocacy Center"
                },
                {
                    "case_number": "ERO-2024-HOU-08441",
                    "alien_registration_number": "A076-892-215",
                    "name": "Phuong Tran Nguyen",
                    "country_of_origin": "Vietnam",
                    "date_of_birth": "1968-12-17",
                    "home_address_us": "5432 Gulfton St, Houston, TX 77081",
                    "phone": "(713) 555-0234",
                    "detention_facility": "Port Isabel Detention Center, Los Fresnos, TX",
                    "detention_start": "2024-10-22",
                    "charges": "8 U.S.C. § 1227(a)(2)(B) – Controlled substance conviction (2022, Texas)",
                    "case_status": "Removal order issued; Vietnam repatriation agreement in process",
                    "immigration_judge": "IJ David Kim, Houston Immigration Court",
                    "attorney_of_record": "Lone Star Legal Aid"
                },
                {
                    "case_number": "ERO-2024-NYC-05589",
                    "alien_registration_number": "A131-047-833",
                    "name": "Blessing Okonkwo",
                    "country_of_origin": "Nigeria",
                    "date_of_birth": "1984-06-09",
                    "home_address_us": "2804 Bronx Park East, Bronx, NY 10467",
                    "phone": "(718) 555-0619",
                    "detention_facility": "Bergen County Jail (ICE contract), Hackensack, NJ",
                    "detention_start": "2024-11-08",
                    "charges": "8 U.S.C. § 1227(a)(1)(A) – Inadmissible at entry; fraudulent visa documents",
                    "case_status": "Expedited removal proceedings initiated",
                    "immigration_judge": "IJ Rachel Goldstein, New York Immigration Court",
                    "attorney_of_record": "UnLocal Inc. – pro bono"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Federal Bureau of Prisons – Inmate Management Records
    # -------------------------------------------------------------------------
    {
        "id": "bop-federal-inmate-management",
        "category": "corrections",
        "title": "Federal Bureau of Prisons – Inmate Management Records",
        "description": "Federal inmate records including offense, sentence, security classification, housing, and programming status for individuals in Bureau of Prisons custody",
        "keywords": ["BOP", "federal prison", "inmates", "corrections", "incarceration", "sentence", "offense", "security", "custody", "rehabilitation"],
        "data": {
            "source": "Federal Bureau of Prisons – Inmate Management System",
            "date_generated": "2025-01-20",
            "records": [
                {
                    "register_number": "84712-083",
                    "name": "Antoine D. Brooks",
                    "date_of_birth": "1982-07-19",
                    "offense": "21 U.S.C. § 841 – Distribution of controlled substances (heroin), conspiracy",
                    "sentence_imposed": "188 months",
                    "sentence_date": "2018-03-14",
                    "projected_release": "2030-11-22",
                    "facility": "USP Lewisburg, Lewisburg, PA",
                    "security_classification": "HIGH",
                    "housing_unit": "H-Block, Cell 214",
                    "gang_affiliation": "Bloods (documented)",
                    "program_participation": "GED program enrolled; substance abuse treatment – Phase 2",
                    "medical_conditions": "Hypertension, Type 2 diabetes – insulin dependent"
                },
                {
                    "register_number": "62391-177",
                    "name": "Sergei A. Morozov",
                    "date_of_birth": "1971-03-02",
                    "offense": "18 U.S.C. § 1030 – Computer fraud; 18 U.S.C. § 1343 – Wire fraud (financial institutions)",
                    "sentence_imposed": "96 months",
                    "sentence_date": "2022-07-28",
                    "projected_release": "2028-10-04",
                    "facility": "FCI Cumberland, Cumberland, MD",
                    "security_classification": "MEDIUM",
                    "housing_unit": "C-Unit, Room 118",
                    "gang_affiliation": "None documented",
                    "program_participation": "UNICOR factory assignment; financial literacy course",
                    "medical_conditions": "None reported"
                },
                {
                    "register_number": "91048-034",
                    "name": "Darnell J. Washington",
                    "date_of_birth": "1976-11-28",
                    "offense": "18 U.S.C. § 922(g) – Felon in possession of firearm; 21 U.S.C. § 846 – Drug trafficking conspiracy",
                    "sentence_imposed": "240 months",
                    "sentence_date": "2015-09-11",
                    "projected_release": "2033-07-19",
                    "facility": "USP Atlanta, Atlanta, GA",
                    "security_classification": "HIGH",
                    "housing_unit": "B-Block, Cell 309",
                    "gang_affiliation": "Crips (documented)",
                    "program_participation": "Welding vocational training; declined substance abuse program",
                    "medical_conditions": "Hepatitis C (treatment completed 2022); lower back injury"
                },
                {
                    "register_number": "45820-509",
                    "name": "Michelle R. Fontaine",
                    "date_of_birth": "1988-09-05",
                    "offense": "18 U.S.C. § 1344 – Bank fraud; 18 U.S.C. § 1956 – Money laundering",
                    "sentence_imposed": "60 months",
                    "sentence_date": "2023-04-17",
                    "projected_release": "2027-08-31",
                    "facility": "FPC Alderson, Alderson, WV",
                    "security_classification": "MINIMUM",
                    "housing_unit": "Cottage 7, Room 22",
                    "gang_affiliation": "None",
                    "program_participation": "Paralegal studies; victim impact panel facilitator",
                    "medical_conditions": "Anxiety disorder (medication managed)"
                },
                {
                    "register_number": "73304-285",
                    "name": "Carlos Ibarra-Fuentes",
                    "date_of_birth": "1968-01-14",
                    "offense": "21 U.S.C. § 960 – International drug trafficking (methamphetamine, >500g)",
                    "sentence_imposed": "360 months",
                    "sentence_date": "2010-06-23",
                    "projected_release": "2038-04-15",
                    "facility": "USP Florence ADMAX, Florence, CO",
                    "security_classification": "HIGH / ADMINISTRATIVE MAX",
                    "housing_unit": "Special Housing Unit (SHU) – classified cell assignment",
                    "gang_affiliation": "Sureños/MS-13 (documented)",
                    "program_participation": "Limited programming – SHU restrictions apply",
                    "medical_conditions": "Chronic kidney disease – stage 3; dialysis 3x/week"
                },
                {
                    "register_number": "28517-649",
                    "name": "Tameika L. Simmons",
                    "date_of_birth": "1994-04-22",
                    "offense": "18 U.S.C. § 1347 – Healthcare fraud; 42 U.S.C. § 1320a-7b – Anti-kickback statute",
                    "sentence_imposed": "48 months",
                    "sentence_date": "2024-01-09",
                    "projected_release": "2027-07-28",
                    "facility": "FCI Tallahassee, Tallahassee, FL",
                    "security_classification": "LOW",
                    "housing_unit": "D-Unit, Room 44",
                    "gang_affiliation": "None",
                    "program_participation": "RDAP (Residential Drug Abuse Program); cosmetology certification",
                    "medical_conditions": "Depression (treatment ongoing); pregnancy – due 2025-03-10"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # USDA Farm Service Agency – Commodity Support Payment Records
    # -------------------------------------------------------------------------
    {
        "id": "usda-farm-subsidy-payments",
        "category": "agriculture",
        "title": "USDA Farm Service Agency – Commodity Support and Conservation Payment Records",
        "description": "USDA Farm Service Agency payment records for agricultural commodity support programs, conservation programs, and disaster assistance for individual producers",
        "keywords": ["USDA", "farm subsidy", "agriculture", "FSA", "commodity support", "conservation", "crop insurance", "producer", "farm payments", "ARC", "PLC"],
        "data": {
            "source": "USDA Farm Service Agency – Agricultural Program Payments Database",
            "fiscal_year": "2024",
            "records": [
                {
                    "farm_serial_number": "FSN-CO-08-1447",
                    "producer_name": "Harold W. Brinkman",
                    "producer_ssn_tin": "478-62-9103",
                    "mailing_address": "14882 County Rd 49, Eaton, CO 80615",
                    "phone": "(970) 555-0347",
                    "county": "Weld County, Colorado",
                    "state": "Colorado",
                    "farm_acres": 1840,
                    "primary_commodity": "Winter Wheat, Corn",
                    "program": "Agriculture Risk Coverage – County (ARC-CO)",
                    "payment_amount": 48720.00,
                    "payment_date": "2024-11-15",
                    "bank_routing": "102001017",
                    "bank_account": "4471-0038-8821"
                },
                {
                    "farm_serial_number": "FSN-IA-32-0882",
                    "producer_name": "Patricia A. Johansson",
                    "producer_ssn_tin": "319-87-5540",
                    "mailing_address": "9204 Prairie Wind Rd, Ames, IA 50010",
                    "phone": "(515) 555-0819",
                    "county": "Story County, Iowa",
                    "state": "Iowa",
                    "farm_acres": 720,
                    "primary_commodity": "Corn, Soybeans",
                    "program": "Price Loss Coverage (PLC) – Corn and Soy",
                    "payment_amount": 31440.00,
                    "payment_date": "2024-10-28",
                    "bank_routing": "073972181",
                    "bank_account": "8831-4402-7734"
                },
                {
                    "farm_serial_number": "FSN-TX-14-2391",
                    "producer_name": "Roberto J. Garza-Villarreal",
                    "producer_ssn_tin": "87-2314409",
                    "mailing_address": "RR 3, Box 214, Laredo, TX 78044",
                    "phone": "(956) 555-0224",
                    "county": "Webb County, Texas",
                    "state": "Texas",
                    "farm_acres": 3120,
                    "primary_commodity": "Sorghum, Cotton",
                    "program": "Environmental Quality Incentives Program (EQIP) – Water conservation",
                    "payment_amount": 87350.00,
                    "payment_date": "2024-09-30",
                    "bank_routing": "114900547",
                    "bank_account": "2209-6617-0041"
                },
                {
                    "farm_serial_number": "FSN-MN-19-0441",
                    "producer_name": "Lars E. Bergstrom",
                    "producer_ssn_tin": "469-31-7788",
                    "mailing_address": "47210 400th St, Willmar, MN 56201",
                    "phone": "(320) 555-0613",
                    "county": "Kandiyohi County, Minnesota",
                    "state": "Minnesota",
                    "farm_acres": 2200,
                    "primary_commodity": "Soybeans, Sugar Beets",
                    "program": "ARC-County + Conservation Reserve Program (CRP)",
                    "payment_amount": 62180.00,
                    "payment_date": "2024-11-01",
                    "bank_routing": "091215927",
                    "bank_account": "5502-3318-9904"
                },
                {
                    "farm_serial_number": "FSN-GA-07-1803",
                    "producer_name": "Dorothy Mae Tillman",
                    "producer_ssn_tin": "264-58-3311",
                    "mailing_address": "2847 Old Courthouse Rd, Valdosta, GA 31601",
                    "phone": "(229) 555-0481",
                    "county": "Lowndes County, Georgia",
                    "state": "Georgia",
                    "farm_acres": 540,
                    "primary_commodity": "Peanuts, Cotton",
                    "program": "Livestock Assistance Program (ELAP) + PLC",
                    "payment_amount": 24930.00,
                    "payment_date": "2024-10-14",
                    "bank_routing": "061000104",
                    "bank_account": "7743-9901-2280"
                },
                {
                    "farm_serial_number": "FSN-CA-38-0729",
                    "producer_name": "Mei Lin Zhao",
                    "producer_ssn_tin": "571-44-8829",
                    "mailing_address": "18430 Avenue 24, Chowchilla, CA 93610",
                    "phone": "(559) 555-0737",
                    "county": "Madera County, California",
                    "state": "California",
                    "farm_acres": 880,
                    "primary_commodity": "Almonds, Grapes (wine)",
                    "program": "EQIP – Micro-irrigation upgrade; Specialty Crop Block Grant",
                    "payment_amount": 41780.00,
                    "payment_date": "2024-09-15",
                    "bank_routing": "121042882",
                    "bank_account": "3308-7724-5519"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # NIH NIAID Clinical Trial Participant Records
    # -------------------------------------------------------------------------
    {
        "id": "nih-clinical-trial-participants",
        "category": "medical",
        "title": "NIH NIAID Clinical Trial – Participant Enrollment and Outcome Records",
        "description": "National Institutes of Health clinical trial enrollment records, treatment assignments, and safety monitoring data for participants in an NIAID-sponsored infectious disease research study",
        "keywords": ["NIH", "NIAID", "clinical trial", "medical research", "participants", "treatment", "adverse events", "vaccine", "drug trial", "placebo", "IRB"],
        "data": {
            "source": "National Institute of Allergy and Infectious Diseases (NIAID) – Division of Clinical Research",
            "trial_id": "NCT-2024-NIAID-0847",
            "trial_title": "Phase III Efficacy and Safety Trial of mRNA-Based Tuberculosis Vaccine (TBMV-04)",
            "irb_approval": "NIH IRB #24-IN-0103",
            "date_generated": "2025-01-15",
            "records": [
                {
                    "participant_id": "TBMV04-001-ATL",
                    "name": "Sandra R. Okonkwo",
                    "date_of_birth": "1972-08-14",
                    "ssn": "412-77-3920",
                    "home_address": "1844 Peachtree Rd NE, Atlanta, GA 30309",
                    "phone": "(404) 555-0291",
                    "enrollment_date": "2024-03-12",
                    "trial_site": "Emory University School of Medicine, Atlanta, GA",
                    "treatment_arm": "Active vaccine – 2-dose regimen (100μg)",
                    "tuberculin_skin_test_baseline": "Negative",
                    "adverse_events": "Grade 1 injection site reaction (Day 2, resolved Day 5); Grade 1 fatigue (Day 3, resolved)",
                    "twelve_month_tb_status": "Negative",
                    "primary_care_physician": "Dr. Anita Subramaniam, Emory Internal Medicine"
                },
                {
                    "participant_id": "TBMV04-002-SEA",
                    "name": "William J. Nakamura",
                    "date_of_birth": "1958-01-29",
                    "ssn": "538-49-7014",
                    "home_address": "4421 NE 55th St, Seattle, WA 98105",
                    "phone": "(206) 555-0844",
                    "enrollment_date": "2024-03-28",
                    "trial_site": "University of Washington Medical Center, Seattle, WA",
                    "treatment_arm": "Placebo control",
                    "tuberculin_skin_test_baseline": "Negative",
                    "adverse_events": "None reported",
                    "twelve_month_tb_status": "Negative",
                    "primary_care_physician": "Dr. James Whitmore, UW General Internal Medicine"
                },
                {
                    "participant_id": "TBMV04-003-CHI",
                    "name": "Fatou Diallo-Ndoye",
                    "date_of_birth": "1988-05-17",
                    "ssn": "367-81-5533",
                    "home_address": "7230 S Cottage Grove Ave, Chicago, IL 60619",
                    "phone": "(312) 555-0618",
                    "enrollment_date": "2024-04-10",
                    "trial_site": "Rush University Medical Center, Chicago, IL",
                    "treatment_arm": "Active vaccine – 2-dose regimen (100μg)",
                    "tuberculin_skin_test_baseline": "Borderline (8mm)",
                    "adverse_events": "Grade 2 systemic reaction (Day 14, fever 38.8°C, resolved Day 16); Grade 1 myalgia",
                    "twelve_month_tb_status": "Negative – per protocol monitoring",
                    "primary_care_physician": "Dr. Kemi Adeyemi, Rush Family Medicine"
                },
                {
                    "participant_id": "TBMV04-004-HOU",
                    "name": "Miguel A. Santos-Delgado",
                    "date_of_birth": "1964-11-02",
                    "ssn": "624-38-1047",
                    "home_address": "9811 Bissonnet St, Houston, TX 77036",
                    "phone": "(713) 555-0377",
                    "enrollment_date": "2024-04-22",
                    "trial_site": "Baylor College of Medicine, Houston, TX",
                    "treatment_arm": "Placebo control",
                    "tuberculin_skin_test_baseline": "Negative",
                    "adverse_events": "None reported",
                    "twelve_month_tb_status": "Positive – converted at Month 9; referred for LTBI treatment",
                    "primary_care_physician": "Dr. Rosa Menendez, Baylor Internal Medicine Clinic"
                },
                {
                    "participant_id": "TBMV04-005-NYC",
                    "name": "Priya V. Krishnaswamy",
                    "date_of_birth": "1993-07-30",
                    "ssn": "489-22-6701",
                    "home_address": "82-14 Roosevelt Ave, Jackson Heights, NY 11372",
                    "phone": "(718) 555-0942",
                    "enrollment_date": "2024-05-07",
                    "trial_site": "Bellevue Hospital Center, New York, NY",
                    "treatment_arm": "Active vaccine – 2-dose regimen (100μg)",
                    "tuberculin_skin_test_baseline": "Negative",
                    "adverse_events": "Grade 1 headache (Days 1–3, resolved); Grade 1 injection site erythema",
                    "twelve_month_tb_status": "Negative",
                    "primary_care_physician": "Dr. Arun Gupta, NYC Health + Hospitals"
                },
                {
                    "participant_id": "TBMV04-006-DEN",
                    "name": "Tobias F. Mueller",
                    "date_of_birth": "1947-03-18",
                    "ssn": "301-64-8849",
                    "home_address": "1201 York St, Denver, CO 80206",
                    "phone": "(303) 555-0511",
                    "enrollment_date": "2024-05-19",
                    "trial_site": "University of Colorado Anschutz Medical Campus, Aurora, CO",
                    "treatment_arm": "Active vaccine – 2-dose regimen (50μg – lower dose cohort)",
                    "tuberculin_skin_test_baseline": "Negative",
                    "adverse_events": "Grade 3 cardiac event (Day 8) – hospitalized 48h; Data Safety Monitoring Board review completed; causality assessment: unlikely related",
                    "twelve_month_tb_status": "Negative",
                    "primary_care_physician": "Dr. Helen Fischer, UCHealth Internal Medicine"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # SSA Social Security Disability Insurance Beneficiary Records
    # -------------------------------------------------------------------------
    {
        "id": "ssa-ssdi-beneficiary-records",
        "category": "social_benefits",
        "title": "Social Security Administration – SSDI Beneficiary Records",
        "description": "Social Security Disability Insurance beneficiary records including disability determinations, monthly benefit amounts, and payment information",
        "keywords": ["SSA", "SSDI", "disability", "social security", "benefits", "beneficiary", "disability insurance", "DI", "impairment", "monthly benefit"],
        "data": {
            "source": "Social Security Administration – Office of Disability Programs",
            "date_generated": "2025-01-10",
            "records": [
                {
                    "beneficiary_id": "SSA-DI-2024-411-8827",
                    "name": "Linda M. Perkowski",
                    "ssn": "384-51-9207",
                    "date_of_birth": "1963-09-08",
                    "mailing_address": "2214 Elm Grove Rd, Pittsburgh, PA 15217",
                    "phone": "(412) 555-0394",
                    "disability_category": "Musculoskeletal disorders – degenerative disc disease, lumbar spine",
                    "onset_date": "2021-04-15",
                    "award_date": "2022-11-01",
                    "monthly_benefit": 1847.00,
                    "payment_method": "Direct deposit",
                    "bank_routing": "043000096",
                    "bank_account": "8841-7723-0019",
                    "medicare_enrolled": True,
                    "representative_payee": "None – self-managed"
                },
                {
                    "beneficiary_id": "SSA-DI-2024-382-4401",
                    "name": "James T. Okafor",
                    "ssn": "517-28-6340",
                    "date_of_birth": "1971-02-11",
                    "mailing_address": "8833 MLK Jr Blvd, Cleveland, OH 44108",
                    "phone": "(216) 555-0781",
                    "disability_category": "Mental health disorders – treatment-resistant major depressive disorder, PTSD (combat-related)",
                    "onset_date": "2018-07-01",
                    "award_date": "2019-03-15",
                    "monthly_benefit": 2314.00,
                    "payment_method": "Direct deposit",
                    "bank_routing": "041001039",
                    "bank_account": "3307-9940-1147",
                    "medicare_enrolled": True,
                    "representative_payee": "None – self-managed"
                },
                {
                    "beneficiary_id": "SSA-DI-2024-399-7712",
                    "name": "Rosa Elena Fuentes",
                    "ssn": "443-67-2088",
                    "date_of_birth": "1958-12-23",
                    "mailing_address": "1730 Cesar Chavez St, San Antonio, TX 78207",
                    "phone": "(210) 555-0553",
                    "disability_category": "Cardiovascular disorders – congestive heart failure, Class III",
                    "onset_date": "2020-02-28",
                    "award_date": "2021-06-01",
                    "monthly_benefit": 1492.00,
                    "payment_method": "Direct deposit",
                    "bank_routing": "114924742",
                    "bank_account": "5519-2231-8840",
                    "medicare_enrolled": True,
                    "representative_payee": "Maria Fuentes (adult daughter)"
                },
                {
                    "beneficiary_id": "SSA-DI-2024-407-3394",
                    "name": "DeAndre M. Collins",
                    "ssn": "229-84-5513",
                    "date_of_birth": "1986-05-30",
                    "mailing_address": "4421 Troost Ave, Kansas City, MO 64110",
                    "phone": "(816) 555-0248",
                    "disability_category": "Neurological disorders – traumatic brain injury (TBI), seizure disorder",
                    "onset_date": "2022-09-14",
                    "award_date": "2023-08-22",
                    "monthly_benefit": 1729.00,
                    "payment_method": "Direct deposit",
                    "bank_routing": "101000187",
                    "bank_account": "6612-4408-3377",
                    "medicare_enrolled": False,
                    "representative_payee": "None – self-managed"
                },
                {
                    "beneficiary_id": "SSA-DI-2024-415-0083",
                    "name": "Ingrid H. Sorensen",
                    "ssn": "612-39-7741",
                    "date_of_birth": "1954-08-14",
                    "mailing_address": "9330 Lyndale Ave S, Minneapolis, MN 55420",
                    "phone": "(612) 555-0837",
                    "disability_category": "Immune system disorders – systemic lupus erythematosus (SLE) with renal involvement",
                    "onset_date": "2019-11-10",
                    "award_date": "2020-09-30",
                    "monthly_benefit": 2081.00,
                    "payment_method": "Paper check",
                    "bank_routing": "N/A",
                    "bank_account": "N/A",
                    "medicare_enrolled": True,
                    "representative_payee": "None – self-managed"
                },
                {
                    "beneficiary_id": "SSA-DI-2024-423-6618",
                    "name": "Tyrell B. Jackson",
                    "ssn": "331-74-8902",
                    "date_of_birth": "1978-03-27",
                    "mailing_address": "5512 Crenshaw Blvd, Los Angeles, CA 90043",
                    "phone": "(323) 555-0964",
                    "disability_category": "Visual impairment – bilateral retinal detachment, legally blind",
                    "onset_date": "2023-01-05",
                    "award_date": "2024-02-14",
                    "monthly_benefit": 1963.00,
                    "payment_method": "Direct deposit",
                    "bank_routing": "322271627",
                    "bank_account": "9901-5537-2240",
                    "medicare_enrolled": False,
                    "representative_payee": "None – self-managed"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Chicago PD Arrest and Booking Records
    # -------------------------------------------------------------------------
    {
        "id": "chicago-pd-arrest-records",
        "category": "law_enforcement",
        "title": "Chicago Police Department – Arrest and Booking Records",
        "description": "Chicago Police Department arrest and booking records including charges, case disposition, and arrestee information for Fiscal Year 2024",
        "keywords": ["Chicago", "police", "CPD", "arrest", "booking", "charges", "criminal", "law enforcement", "detention", "municipal", "felony", "misdemeanor"],
        "data": {
            "source": "Chicago Police Department – Records and Identification Section",
            "fiscal_year": "2024",
            "records": [
                {
                    "arrest_number": "CPD-AR-2024-0184421",
                    "booking_number": "CPD-BK-2024-0184421",
                    "name": "Terrence A. Hollis",
                    "date_of_birth": "1990-06-14",
                    "home_address": "7441 S Racine Ave, Chicago, IL 60636",
                    "phone": "(773) 555-0382",
                    "arrest_date": "2024-08-03",
                    "arrest_district": "District 6 – Gresham",
                    "arresting_officer": "Officer M. Ruiz, Badge #14882",
                    "charges": "720 ILCS 5/16-1 – Retail theft (felony, >$500); 720 ILCS 5/12-3.2 – Domestic battery",
                    "bond_amount": 5000.00,
                    "case_status": "Indicted – Cook County Circuit Court, Case 2024-CR-041882; trial scheduled 2025-03-15"
                },
                {
                    "arrest_number": "CPD-AR-2024-0197334",
                    "booking_number": "CPD-BK-2024-0197334",
                    "name": "Guadalupe Martinez-Ochoa",
                    "date_of_birth": "1984-11-19",
                    "home_address": "2314 N Pulaski Rd, Chicago, IL 60639",
                    "phone": "(312) 555-0719",
                    "arrest_date": "2024-08-22",
                    "arrest_district": "District 14 – Shakespeare",
                    "arresting_officer": "Officer T. Williams, Badge #22041",
                    "charges": "625 ILCS 5/11-501 – DUI (alcohol); 625 ILCS 5/6-101 – Driving without valid license",
                    "bond_amount": 2500.00,
                    "case_status": "Pled guilty – supervision 12 months, license suspended 6 months"
                },
                {
                    "arrest_number": "CPD-AR-2024-0208817",
                    "booking_number": "CPD-BK-2024-0208817",
                    "name": "Darius L. Freeman",
                    "date_of_birth": "1997-03-07",
                    "home_address": "5830 W Chicago Ave, Chicago, IL 60651",
                    "phone": "(708) 555-0547",
                    "arrest_date": "2024-09-11",
                    "arrest_district": "District 11 – Harrison",
                    "arresting_officer": "Officer K. Johnson, Badge #18274",
                    "charges": "720 ILCS 5/24-1.1 – Unlawful possession of firearm by felon; 720 ILCS 570/402 – Possession of controlled substance (Class 1)",
                    "bond_amount": 50000.00,
                    "case_status": "Held without bail – Cook County Jail; preliminary hearing 2024-10-04"
                },
                {
                    "arrest_number": "CPD-AR-2024-0221099",
                    "booking_number": "CPD-BK-2024-0221099",
                    "name": "Brianna K. Thompson",
                    "date_of_birth": "1992-08-23",
                    "home_address": "1104 E 71st St, Chicago, IL 60619",
                    "phone": "(773) 555-0831",
                    "arrest_date": "2024-09-29",
                    "arrest_district": "District 3 – Grand Crossing",
                    "arresting_officer": "Officer P. Washington, Badge #31147",
                    "charges": "720 ILCS 5/17-3 – Forgery; 720 ILCS 5/17-1 – Deceptive practices (identity theft)",
                    "bond_amount": 10000.00,
                    "case_status": "Nolle prosequi – state declined to prosecute; charges dismissed 2024-11-14"
                },
                {
                    "arrest_number": "CPD-AR-2024-0238504",
                    "booking_number": "CPD-BK-2024-0238504",
                    "name": "Kevin R. O'Brien",
                    "date_of_birth": "1968-01-31",
                    "home_address": "4401 N Sheridan Rd, Chicago, IL 60640",
                    "phone": "(773) 555-0218",
                    "arrest_date": "2024-10-17",
                    "arrest_district": "District 19 – Town Hall",
                    "arresting_officer": "Officer S. Garcia, Badge #27803",
                    "charges": "720 ILCS 5/12-3 – Simple battery; 720 ILCS 5/26-1 – Disorderly conduct",
                    "bond_amount": 1000.00,
                    "case_status": "Pled guilty – 12 months conditional discharge, anger management program"
                },
                {
                    "arrest_number": "CPD-AR-2024-0251788",
                    "booking_number": "CPD-BK-2024-0251788",
                    "name": "Aisha N. Patel",
                    "date_of_birth": "1985-07-12",
                    "home_address": "1831 W Devon Ave, Chicago, IL 60660",
                    "phone": "(312) 555-0644",
                    "arrest_date": "2024-11-04",
                    "arrest_district": "District 24 – Rogers Park",
                    "arresting_officer": "Officer D. Lee, Badge #39021",
                    "charges": "720 ILCS 5/16-3 – Theft of services (transit fraud, repeated); 625 ILCS 5/11-1414 – Reckless driving",
                    "bond_amount": 500.00,
                    "case_status": "Diversion program – community service 80 hours, restitution $347.00"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # Colorado DMV Driver Records (DPPA-Protected)
    # -------------------------------------------------------------------------
    {
        "id": "colorado-dmv-driver-records",
        "category": "state_records",
        "title": "Colorado DMV – Driver License and Vehicle Registration Records",
        "description": "Colorado Division of Motor Vehicles driver license and vehicle registration records. All personal data protected under the Driver's Privacy Protection Act (18 U.S.C. § 2721)",
        "keywords": ["DMV", "Colorado", "driver license", "vehicle registration", "motor vehicle", "DPPA", "state records", "license plate", "VIN", "driving record"],
        "data": {
            "source": "Colorado Department of Revenue – Division of Motor Vehicles",
            "date_generated": "2025-01-08",
            "dppa_protection": "All personal information protected under Driver's Privacy Protection Act, 18 U.S.C. § 2721 et seq.",
            "records": [
                {
                    "record_id": "CO-DMV-DL-2024-0841293",
                    "driver_license_number": "CO-841293-47",
                    "name": "Patricia Lynn Hendricks",
                    "date_of_birth": "1975-04-22",
                    "home_address": "3821 Quivas St, Denver, CO 80211",
                    "phone": "(303) 555-0473",
                    "license_class": "Class R (Regular)",
                    "license_expiration": "2029-04-22",
                    "violations_points": 3,
                    "vin": "1FTFW1ET4DFC10312",
                    "license_plate": "CO-ABR-4471",
                    "vehicle_make_model": "2013 Ford F-150 XLT",
                    "registration_expiration": "2025-02-28",
                    "insurance_carrier": "GEICO – Policy #CO-874-2241"
                },
                {
                    "record_id": "CO-DMV-DL-2024-0779041",
                    "driver_license_number": "CO-779041-83",
                    "name": "Marcus T. Jefferson",
                    "date_of_birth": "1988-09-17",
                    "home_address": "8844 E Colfax Ave, Aurora, CO 80010",
                    "phone": "(720) 555-0824",
                    "license_class": "Class R",
                    "license_expiration": "2028-09-17",
                    "violations_points": 8,
                    "vin": "2T3RFREV5JW712084",
                    "license_plate": "CO-ZKL-7839",
                    "vehicle_make_model": "2018 Toyota RAV4 LE",
                    "registration_expiration": "2025-07-31",
                    "insurance_carrier": "State Farm – Policy #CO-211-8847"
                },
                {
                    "record_id": "CO-DMV-DL-2024-0912487",
                    "driver_license_number": "CO-912487-61",
                    "name": "Sunita Rao-Krishnan",
                    "date_of_birth": "1992-01-03",
                    "home_address": "421 Mapleton Ave, Boulder, CO 80304",
                    "phone": "(303) 555-0182",
                    "license_class": "Class R",
                    "license_expiration": "2026-01-03",
                    "violations_points": 0,
                    "vin": "5YJ3E1EA5KF419022",
                    "license_plate": "CO-ELK-1184",
                    "vehicle_make_model": "2019 Tesla Model 3 Standard Range",
                    "registration_expiration": "2025-01-31",
                    "insurance_carrier": "Progressive – Policy #CO-558-3310"
                },
                {
                    "record_id": "CO-DMV-DL-2024-0648819",
                    "driver_license_number": "CO-648819-29",
                    "name": "Earl R. Cunningham",
                    "date_of_birth": "1951-06-30",
                    "home_address": "14870 W 64th Ave, Arvada, CO 80004",
                    "phone": "(720) 555-0638",
                    "license_class": "Class R – Restricted (daytime only, corrective lenses required)",
                    "license_expiration": "2026-06-30",
                    "violations_points": 2,
                    "vin": "1G1ZD5ST9JF104728",
                    "license_plate": "CO-MTN-8831",
                    "vehicle_make_model": "2018 Chevrolet Malibu LT",
                    "registration_expiration": "2025-04-30",
                    "insurance_carrier": "Farmers – Policy #CO-774-6628"
                },
                {
                    "record_id": "CO-DMV-DL-2024-0837724",
                    "driver_license_number": "CO-837724-55",
                    "name": "Xiomara Delgado-Vásquez",
                    "date_of_birth": "1999-12-08",
                    "home_address": "2204 W Alameda Ave, Denver, CO 80219",
                    "phone": "(303) 555-0914",
                    "license_class": "Class R",
                    "license_expiration": "2027-12-08",
                    "violations_points": 4,
                    "vin": "3FA6P0H76JR127854",
                    "license_plate": "CO-RVR-2247",
                    "vehicle_make_model": "2018 Ford Fusion SE",
                    "registration_expiration": "2025-03-31",
                    "insurance_carrier": "USAA – Policy #CO-331-9901"
                },
                {
                    "record_id": "CO-DMV-CDL-2024-0504133",
                    "driver_license_number": "CO-504133-CDL",
                    "name": "Robert W. Kowalski",
                    "date_of_birth": "1967-08-14",
                    "home_address": "5930 Vine St, Commerce City, CO 80022",
                    "phone": "(303) 555-0771",
                    "license_class": "Class A CDL – Hazmat endorsement (H); Tanker endorsement (N)",
                    "license_expiration": "2029-08-14",
                    "violations_points": 0,
                    "vin": "1FUJGEDV8CLBF8831",
                    "license_plate": "CO-COM-4418",
                    "vehicle_make_model": "2012 Freightliner Cascadia (semi-truck)",
                    "registration_expiration": "2025-12-31",
                    "insurance_carrier": "Old Republic – Policy #CO-CDL-7741"
                }
            ]
        }
    },
    # -------------------------------------------------------------------------
    # FDA Adverse Event Reporting System (FAERS) Records
    # -------------------------------------------------------------------------
    {
        "id": "fda-adverse-event-reports",
        "category": "pharmaceutical",
        "title": "FDA Adverse Event Reporting System (FAERS) – Individual Safety Reports",
        "description": "U.S. Food and Drug Administration adverse drug event reports submitted by healthcare providers and consumers, including drug name, reaction, and outcome data",
        "keywords": ["FDA", "adverse event", "FAERS", "drug safety", "pharmacovigilance", "medication", "side effects", "MedWatch", "pharmaceutical", "reaction"],
        "data": {
            "source": "U.S. Food and Drug Administration – Center for Drug Evaluation and Research (CDER), FAERS Database",
            "quarter": "Q3 2024",
            "records": [
                {
                    "report_id": "FAERS-2024-Q3-8814422",
                    "reporter_name": "Dr. Karen Ostrowski",
                    "reporter_type": "Healthcare professional (physician)",
                    "reporter_institution": "Mayo Clinic, Rochester, MN",
                    "reporter_phone": "(507) 555-0281",
                    "patient_age": 67,
                    "patient_sex": "Female",
                    "suspect_drug": "Rivaroxaban (Xarelto) 20mg",
                    "indication": "Atrial fibrillation – stroke prophylaxis",
                    "adverse_event": "Severe gastrointestinal hemorrhage requiring hospitalization; hemoglobin drop from 12.4 to 7.1 g/dL",
                    "onset_date": "2024-07-14",
                    "outcome": "Hospitalized – 5-day inpatient stay; drug discontinued; recovered",
                    "manufacturer": "Janssen Pharmaceuticals / Bayer AG",
                    "submitted_to_fda": "2024-08-02"
                },
                {
                    "report_id": "FAERS-2024-Q3-8829017",
                    "reporter_name": "Michael D. Fontaine",
                    "reporter_type": "Consumer/patient",
                    "reporter_institution": "N/A (self-report)",
                    "reporter_phone": "(617) 555-0844",
                    "patient_age": 54,
                    "patient_sex": "Male",
                    "suspect_drug": "Semaglutide (Ozempic) 1mg/week injection",
                    "indication": "Type 2 diabetes management",
                    "adverse_event": "Severe nausea, vomiting, and rapid weight loss (18 lbs in 6 weeks); pancreatitis suspected",
                    "onset_date": "2024-07-28",
                    "outcome": "Emergency department visit; pancreatitis confirmed via lipase 847 U/L; drug discontinued; recovered",
                    "manufacturer": "Novo Nordisk A/S",
                    "submitted_to_fda": "2024-08-19"
                },
                {
                    "report_id": "FAERS-2024-Q3-8841398",
                    "reporter_name": "Dr. Aisha Nwosu",
                    "reporter_type": "Healthcare professional (pharmacist)",
                    "reporter_institution": "Walgreens Pharmacy #4472, Detroit, MI",
                    "reporter_phone": "(313) 555-0619",
                    "patient_age": 34,
                    "patient_sex": "Female",
                    "suspect_drug": "Isotretinoin (Accutane) 40mg daily",
                    "indication": "Severe nodular acne",
                    "adverse_event": "Severe depression, suicidal ideation; patient voluntarily hospitalized",
                    "onset_date": "2024-08-07",
                    "outcome": "Psychiatric inpatient admission 14 days; drug discontinued; iPLEDGE system flagged; recovered with ongoing psychiatric care",
                    "manufacturer": "Roche Laboratories",
                    "submitted_to_fda": "2024-08-25"
                },
                {
                    "report_id": "FAERS-2024-Q3-8857744",
                    "reporter_name": "Consuela Morales-Reyes",
                    "reporter_type": "Consumer/patient caregiver",
                    "reporter_institution": "N/A (self-report, caregiver)",
                    "reporter_phone": "(915) 555-0337",
                    "patient_age": 82,
                    "patient_sex": "Male",
                    "suspect_drug": "Metformin 1000mg BID + Lisinopril 10mg",
                    "indication": "Type 2 diabetes; hypertension",
                    "adverse_event": "Lactic acidosis following contrast CT scan; acute kidney injury (AKI)",
                    "onset_date": "2024-08-19",
                    "outcome": "ICU admission 72 hours; hemodialysis x2 sessions; metformin held permanently; partial renal recovery",
                    "manufacturer": "Multiple generic manufacturers",
                    "submitted_to_fda": "2024-09-10"
                },
                {
                    "report_id": "FAERS-2024-Q3-8872031",
                    "reporter_name": "Dr. James R. Whitmore",
                    "reporter_type": "Healthcare professional (specialist – oncologist)",
                    "reporter_institution": "Johns Hopkins Sidney Kimmel Comprehensive Cancer Center, Baltimore, MD",
                    "reporter_phone": "(410) 555-0482",
                    "patient_age": 58,
                    "patient_sex": "Female",
                    "suspect_drug": "Pembrolizumab (Keytruda) 200mg IV q3w",
                    "indication": "Stage IIIA non-small cell lung cancer (NSCLC)",
                    "adverse_event": "Immune-mediated pneumonitis, Grade 3; bilateral infiltrates on CT; O2 saturation 88% on room air",
                    "onset_date": "2024-09-04",
                    "outcome": "Hospitalized; high-dose corticosteroids initiated; drug held pending resolution; partial improvement at 30-day follow-up",
                    "manufacturer": "Merck & Co., Inc.",
                    "submitted_to_fda": "2024-09-22"
                },
                {
                    "report_id": "FAERS-2024-Q3-8889210",
                    "reporter_name": "Stephanie L. Park",
                    "reporter_type": "Consumer/patient",
                    "reporter_institution": "N/A (self-report)",
                    "reporter_phone": "(206) 555-0783",
                    "patient_age": 28,
                    "patient_sex": "Female",
                    "suspect_drug": "Combined oral contraceptive (ethinyl estradiol/norgestimate)",
                    "indication": "Contraception",
                    "adverse_event": "Deep vein thrombosis (DVT) right leg; confirmed by duplex ultrasound",
                    "onset_date": "2024-09-17",
                    "outcome": "Anticoagulation therapy initiated (apixaban); drug discontinued; full resolution at 90-day imaging follow-up",
                    "manufacturer": "Ortho-McNeil-Janssen Pharmaceuticals",
                    "submitted_to_fda": "2024-10-01"
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


if __name__ == '__main__':
    seed()
