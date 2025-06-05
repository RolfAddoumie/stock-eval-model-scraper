import requests
from bs4 import BeautifulSoup

url = "https://www.macrotrends.net/stocks/charts/GOOS/apple/free-cash-flow"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find("table", {"class": "historical_data_table table"})
rows = table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

#last 10 years
last_10_years = data_rows[:11]



#cagr
start_value = (float(last_10_years[-1].find_all("td")[1  ].text.replace(",", "")) + float(last_10_years[-2].find_all("td")[1  ].text.replace(",", ""))) / 2
end_value = (float(last_10_years[0].find_all("td")[1].text.replace(",", "")) + float(last_10_years[1].find_all("td")[1].text.replace(",", ""))) / 2
years = len(last_10_years) - 1  # number of periods (years)

# Calculate CAGR
cagr = (pow(end_value / start_value, 1/years) - 1) * 100

print('Compound Annual Growth Rate (CAGR): ' + str(cagr) + "%")

for row in last_10_years:
    cols = [col.text.strip() for col in row.find_all("td")]
    print(cols)
