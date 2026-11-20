
"""
BharatScheme AI - Government Source Registry

Official sources are prioritised.
Secondary sources are used only for discovery,
never as final eligibility evidence.
"""

SOURCE_REGISTRY = [
    # National government portals
    {
        "name": "National Portal of India - Schemes",
        "url": "https://www.india.gov.in/my-government/schemes",
        "level": "Central",
        "type": "official",
        "priority": 1,
    },
    {
        "name": "myScheme",
        "url": "https://www.myscheme.gov.in/",
        "level": "Central",
        "type": "official",
        "priority": 1,
    },
    {
        "name": "India Government Directory (IGOD)",
        "url": "https://igod.gov.in/",
        "level": "Central",
        "type": "official",
        "priority": 1,
    },
    {
        "name": "Open Government Data Platform",
        "url": "https://data.gov.in/",
        "level": "Central",
        "type": "official",
        "priority": 1,
    },
    {
        "name": "Press Information Bureau",
        "url": "https://pib.gov.in/",
        "level": "Central",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "e-Gazette of India",
        "url": "https://egazette.gov.in/",
        "level": "Central",
        "type": "official",
        "priority": 1,
    },

    # Tamil Nadu
    {
        "name": "Tamil Nadu Government Schemes",
        "url": "https://www.tn.gov.in/schemes.php",
        "level": "State",
        "state": "Tamil Nadu",
        "type": "official",
        "priority": 1,
    },
    {
        "name": "Tamil Nadu Government Portal",
        "url": "https://www.tn.gov.in/",
        "level": "State",
        "state": "Tamil Nadu",
        "type": "official",
        "priority": 1,
    },

    # Other State government portals
    {
        "name": "Andhra Pradesh Government",
        "url": "https://www.ap.gov.in/",
        "level": "State",
        "state": "Andhra Pradesh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Arunachal Pradesh Government",
        "url": "https://arunachalpradesh.gov.in/",
        "level": "State",
        "state": "Arunachal Pradesh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Assam Government",
        "url": "https://assam.gov.in/",
        "level": "State",
        "state": "Assam",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Bihar Government",
        "url": "https://state.bihar.gov.in/",
        "level": "State",
        "state": "Bihar",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Chhattisgarh Government",
        "url": "https://cgstate.gov.in/",
        "level": "State",
        "state": "Chhattisgarh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Goa Government",
        "url": "https://www.goa.gov.in/",
        "level": "State",
        "state": "Goa",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Gujarat Government",
        "url": "https://gujaratindia.gov.in/",
        "level": "State",
        "state": "Gujarat",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Haryana Government",
        "url": "https://haryana.gov.in/",
        "level": "State",
        "state": "Haryana",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Himachal Pradesh Government",
        "url": "https://himachal.nic.in/",
        "level": "State",
        "state": "Himachal Pradesh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Jharkhand Government",
        "url": "https://www.jharkhand.gov.in/",
        "level": "State",
        "state": "Jharkhand",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Karnataka Government",
        "url": "https://www.karnataka.gov.in/",
        "level": "State",
        "state": "Karnataka",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Kerala Government",
        "url": "https://kerala.gov.in/",
        "level": "State",
        "state": "Kerala",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Madhya Pradesh Government",
        "url": "https://mp.gov.in/",
        "level": "State",
        "state": "Madhya Pradesh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Maharashtra Government",
        "url": "https://www.maharashtra.gov.in/",
        "level": "State",
        "state": "Maharashtra",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Manipur Government",
        "url": "https://manipur.gov.in/",
        "level": "State",
        "state": "Manipur",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Meghalaya Government",
        "url": "https://meghalaya.gov.in/",
        "level": "State",
        "state": "Meghalaya",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Mizoram Government",
        "url": "https://mizoram.gov.in/",
        "level": "State",
        "state": "Mizoram",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Nagaland Government",
        "url": "https://nagaland.gov.in/",
        "level": "State",
        "state": "Nagaland",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Odisha Government",
        "url": "https://odisha.gov.in/",
        "level": "State",
        "state": "Odisha",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Punjab Government",
        "url": "https://punjab.gov.in/",
        "level": "State",
        "state": "Punjab",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Rajasthan Government",
        "url": "https://rajasthan.gov.in/",
        "level": "State",
        "state": "Rajasthan",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Sikkim Government",
        "url": "https://sikkim.gov.in/",
        "level": "State",
        "state": "Sikkim",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Telangana Government",
        "url": "https://www.telangana.gov.in/",
        "level": "State",
        "state": "Telangana",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Tripura Government",
        "url": "https://tripura.gov.in/",
        "level": "State",
        "state": "Tripura",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Uttar Pradesh Government",
        "url": "https://up.gov.in/",
        "level": "State",
        "state": "Uttar Pradesh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Uttarakhand Government",
        "url": "https://uk.gov.in/",
        "level": "State",
        "state": "Uttarakhand",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "West Bengal Government",
        "url": "https://wb.gov.in/",
        "level": "State",
        "state": "West Bengal",
        "type": "official",
        "priority": 2,
    },

    # Union Territories
    {
        "name": "Andaman and Nicobar Islands",
        "url": "https://andaman.gov.in/",
        "level": "UT",
        "state": "Andaman and Nicobar Islands",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Chandigarh Administration",
        "url": "https://chandigarh.gov.in/",
        "level": "UT",
        "state": "Chandigarh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Dadra and Nagar Haveli and Daman and Diu",
        "url": "https://ddd.gov.in/",
        "level": "UT",
        "state": "Dadra and Nagar Haveli and Daman and Diu",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Delhi Government",
        "url": "https://delhi.gov.in/",
        "level": "UT",
        "state": "Delhi",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Jammu and Kashmir Government",
        "url": "https://jk.gov.in/",
        "level": "UT",
        "state": "Jammu and Kashmir",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Ladakh Administration",
        "url": "https://ladakh.gov.in/",
        "level": "UT",
        "state": "Ladakh",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Lakshadweep Administration",
        "url": "https://lakshadweep.gov.in/",
        "level": "UT",
        "state": "Lakshadweep",
        "type": "official",
        "priority": 2,
    },
    {
        "name": "Puducherry Government",
        "url": "https://py.gov.in/",
        "level": "UT",
        "state": "Puducherry",
        "type": "official",
        "priority": 2,
    },

    # Secondary discovery only - not an official government authority
    {
        "name": "CGScheme - Secondary Scheme Directory",
        "url": "https://www.cgscheme.com/government-schemes/",
        "level": "Secondary",
        "type": "secondary",
        "priority": 3,
    },
]


def get_official_sources():
    """Return official government sources only."""
    return [
        source for source in SOURCE_REGISTRY
        if source["type"] == "official"
    ]


def get_sources_by_state(state_name):
    """Return official sources for a selected State or UT."""
    return [
        source for source in SOURCE_REGISTRY
        if source.get("state", "").lower() == state_name.lower()
        and source["type"] == "official"
    ]


def get_secondary_sources():
    """Return secondary sources for discovery, not verification."""
    return [
        source for source in SOURCE_REGISTRY
        if source["type"] == "secondary"
    ]
