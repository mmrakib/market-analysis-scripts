#
# This script plots the yields of 2-year and 10-year Treasury bonds and the spread between them.
#

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import xml.etree.ElementTree as ET
from datetime import datetime
from pprint import pprint

DATA_FOLDER = "data"
INPUT_FILE = "us_treasury_yield_data.xml"

def parse_xml(xml_data):
    root = ET.fromstring(xml_data)

    namespaces = {
        'ns0': 'http://www.w3.org/2005/Atom',
        'ns1': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
        'ns2': 'http://schemas.microsoft.com/ado/2007/08/dataservices'
    }

    values = []

    for entry in root.findall('.//ns0:entry', namespaces):
        date = entry.find('.//ns2:NEW_DATE', namespaces).text
        two_year_yield = entry.find('.//ns2:BC_2YEAR', namespaces)
        ten_year_yield = entry.find('.//ns2:BC_10YEAR', namespaces)

        if date and two_year_yield is not None and ten_year_yield is not None:
            value = {
                'date': datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"),
                'two_year_yield': float(two_year_yield.text),
                'ten_year_yield': float(ten_year_yield.text),
            }
            values.append(value)

    return values

def plot_yields_and_spread(values):
    # Extract dates, two-year yields, and ten-year yields from values
    dates = [item['date'] for item in values]
    two_year_yields = [item['two_year_yield'] for item in values]
    ten_year_yields = [item['ten_year_yield'] for item in values]
    
    # Calculate the yield spread (10-year yield - 2-year yield)
    yield_spread = [ten - two for ten, two in zip(ten_year_yields, two_year_yields)]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(dates, two_year_yields, label='2-Year Yield', color='red')
    plt.plot(dates, ten_year_yields, label='10-Year Yield', color='blue')
    plt.plot(dates, yield_spread, label='10-2 Yield Spread', color='green')
    plt.title('US Treasury Yields and 10-2 Spread')
    plt.xlabel('Date')
    plt.ylabel('Yield (%)')

    plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    plt.savefig("us_treasury_yields_plot.png", format="png", dpi=300)

input_path = os.path.join(DATA_FOLDER, INPUT_FILE)

with open(input_path, 'r', encoding='utf-8') as file:
    xml_data = file.read()

values = parse_xml(xml_data)

plot_yields_and_spread(values)
