import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_FOLDER = "data"
INPUT_FILE = "f02d.xlsx"

# Load the Excel file and specify the sheet name
file_path = os.path.join(DATA_FOLDER, INPUT_FILE)  # Ensure this file is in the same directory or provide the full path
data = pd.read_excel(file_path, sheet_name='Data', skiprows=10)

# Rename columns for ease of use
data.columns = ['Date', '2_Year_Yield', '3_Year_Yield', '5_Year_Yield', '10_Year_Yield', 'Indexed_Bond']

# Convert 'Date' column to datetime format
data['Date'] = pd.to_datetime(data['Date'], format='%d-%b-%Y')

# Drop rows with missing values in '2_Year_Yield' and '10_Year_Yield' columns
data = data.dropna(subset=['2_Year_Yield', '10_Year_Yield'])

# Calculate the 10-2 spread
data['10_2_Spread'] = data['10_Year_Yield'] - data['2_Year_Yield']

# Plotting
plt.figure(figsize=(14, 8))

# Plot 10-year yield in red
plt.plot(data['Date'], data['10_Year_Yield'], color='red', label='10-Year Yield')

# Plot 2-year yield in blue
plt.plot(data['Date'], data['2_Year_Yield'], color='blue', label='2-Year Yield')

# Plot 10-2 spread in green
plt.plot(data['Date'], data['10_2_Spread'], color='green', label='10-2 Spread')

# Labels and title
plt.xlabel('Date')
plt.ylabel('Yield (%)')
plt.title('AU Treasury Yields and 10-2 Spread')

# Set x-axis to show only the start of each year
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Add grid lines
plt.grid(True, which='major', linestyle='--', linewidth=0.5)
plt.grid(True, which='minor', linestyle=':', linewidth=0.2)

# Adding legend
plt.legend()

# Save the plot as an image file (e.g., PNG format)
output_path = 'au_treasury_yields_plot.png'
plt.savefig(output_path)

print(f"Plot saved as {output_path}")
