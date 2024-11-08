#
# This script fetches the XML data of US Treasury bond yields from the home.treasury.gov
# (Only retrieves data for 2-year and 10-year Treasury bond yields)
#

import os
import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://home.treasury.gov"
XML_ENDPOINT = "/resource-center/data-chart-center/interest-rates/pages/xml"
DATA_FOLDER = "data"
OUTPUT_FILE = "us_treasury_yield_data.xml"

def fetch_all_xml_data():
    url = BASE_URL + XML_ENDPOINT
    page = 0
    all_entries = []

    while True:
        print(f"Fetching page {page}...")
        
        params = {
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": "all",
            "page": page
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        root = ET.fromstring(response.text)

        entries = root.findall('.//atom:entry', namespaces={
            'atom': 'http://www.w3.org/2005/Atom'
        })

        if not entries:
            print("No more entries found.")
            break

        all_entries.extend(entries)
        page += 1

    return all_entries

def save_to_xml(entries, filename):
    root = ET.Element("TreasuryYields")

    for entry in entries:
        root.append(entry)

    tree = ET.ElementTree(root)

    os.makedirs(DATA_FOLDER, exist_ok=True)
    output_path = os.path.join(DATA_FOLDER, filename)

    with open(output_path, "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True)

    print(f"XML data saved to {output_path}")

print("Fetching all US Treasury yield data...")
entries = fetch_all_xml_data()
print("Data fetched successfully.")

if entries:
    print("Saving to XML file...")
    save_to_xml(entries, OUTPUT_FILE)
else:
    print("No valid yield data found.")
    exit(1)
print(f"Saved to XML file successfully: {os.path.join(DATA_FOLDER, OUTPUT_FILE)}.")
