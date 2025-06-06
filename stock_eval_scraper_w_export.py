import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

headers = {"User-Agent": "Mozilla/5.0"}
api_key = "14d9e55888524b43a3da05c004f6946f"
# Stock Price
symbol = input("Input the ticker of the stock: ")
url = f"https://www.macrotrends.net/stocks/charts/{symbol}/-/stock-price-history"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")


sub = soup.find("span", {"style": "color:#444; line-height: 1.8;"})
stock = sub.find_all("strong")[0].text.strip()


# Market Cap
url = f"https://www.macrotrends.net/stocks/charts/{symbol}/-/market-cap"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

sub = soup.find("span", {"style": "color:#444; line-height: 1.8;"})
latest_market_cap = sub.find_all("strong")[0].text.strip()
latest_market_cap = latest_market_cap.replace('$', '').replace('B', '').strip()

# Free Cash Flow (CAGR Calculation)
url = f"https://www.macrotrends.net/stocks/charts/{symbol}/-/free-cash-flow"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find("table", {"class": "historical_data_table table"})
rows = table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

years_count = data_rows[:11]

start_value = (float(years_count[-1].find_all("td")[1].text.replace(",", "")) + float(years_count[-2].find_all("td")[1].text.replace(",", ""))) / 2
end_value = (float(years_count[0].find_all("td")[1].text.replace(",", "")) + float(years_count[1].find_all("td")[1].text.replace(",", ""))) / 2
years_actual = len(years_count)

cagr = ((pow(end_value / start_value, 1/years_actual) - 1) * 100)
cagr_rounded = round(cagr, 2)

free_cash_flow_points = []
for row in years_count:
    cols = [col.text.strip() for col in row.find_all("td")]
    free_cash_flow_points.append(cols)

# Cash on Hand
url = f"https://www.macrotrends.net/stocks/charts/{symbol}/-/cash-on-hand"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find_all("div", {"class": "col-xs-6"})
sub = soup.find_all("div", {"class": "sub_main_content_container"})
quarterly_table = table[1]
rows = quarterly_table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

latest_cash_on_hand = None
if len(data_rows) > 0:
    latest_cash_on_hand = [col.text.strip() for col in data_rows[0].find_all("td")]

# Total Liabilities
url = f"https://www.macrotrends.net/stocks/charts/{symbol}/-/total-liabilities"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find_all("div", {"class": "col-xs-6"})
sub = soup.find_all("div", {"class": "sub_main_content_container"})
quarterly_table = table[1]
rows = quarterly_table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

latest_total_liabilities = None
if len(data_rows) > 0:
    latest_total_liabilities = [col.text.strip() for col in data_rows[0].find_all("td")]



cleaned_fcf = []
cleaned_coh = []
cleaned_tl = []

for year, value in free_cash_flow_points:
    # Remove commas and convert to float
    value_clean = float(value.replace(",", ""))
    cleaned_fcf.append([int(year), value_clean])

date, value = latest_cash_on_hand
value_clean = float(value.replace("$", "").replace(",", ""))
cleaned_coh.append([date, value_clean])

date, value = latest_total_liabilities
value_clean = float(value.replace("$", "").replace(",", ""))
cleaned_tl.append([date, value_clean])


# Organize all data into a dictionary
all_data = {
    "symbol": symbol,
    "stock_price": float(stock),
    "market_cap": float(latest_market_cap),
    "cagr": {
        "years": years_actual,
        "value_percent": cagr_rounded,
        "free_cash_flow_points": cleaned_fcf
    },
    "latest_cash_on_hand": cleaned_coh,
    "latest_total_liabilities": cleaned_tl
}

# Save to data.json
with open("data.json", "w") as f:
    json.dump(all_data, f, indent=4)

print("All data has been saved to data.json")

with open("data.json", "r") as f:
    data = json.load(f)

# Extract general info
general_info = {
    "symbol": data["symbol"],
    "Stock Price": data["stock_price"],
    "Market Cap (in billions)": data["market_cap"],
    "CAGR Years": data["cagr"]["years"],
    "CAGR Percent": data["cagr"]["value_percent"],
    "Latest Cash on Hand Date": data["latest_cash_on_hand"][0][0],
    "Cash on Hand": data["latest_cash_on_hand"][0][1],
    "Latest Liabilities Date": data["latest_total_liabilities"][0][0],
    "Total Liabilities": data["latest_total_liabilities"][0][1]
}

# Time-series data
fcf_data = data["cagr"]["free_cash_flow_points"]
fcf_df = pd.DataFrame(fcf_data, columns=["Year", "Free Cash Flow"])

# Add general info only to the first row
for key, value in general_info.items():
    fcf_df[key] = ""

fcf_df.loc[0, list(general_info.keys())] = list(general_info.values())

# Reorder columns (optional, put general info first)
columns_order = list(general_info.keys()) + ["Year", "Free Cash Flow"]
fcf_df = fcf_df[columns_order]

# Save to CSV
fcf_df.to_csv(f"{symbol}_stock_summary.csv", index=False)

print(f"Merged CSV '{symbol}_stock_summary.csv' created with general info only in the first row.")