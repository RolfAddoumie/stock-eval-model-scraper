import requests
from bs4 import BeautifulSoup

#Stock Price
symbol = input("Input the ticker of the stock: ")
api_key = "14d9e55888524b43a3da05c004f6946f"
url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"

response = requests.get(url)
data = response.json()

print(f"Stock Price: ${data['price']}")


#Market Cap
url = f"https://api.twelvedata.com/market_cap?symbol={symbol}&apikey={api_key}"

response = requests.get(url)
data = response.json()

latest_market_cap = data['market_cap'][0]['value']

print(f"Market Cap: ${latest_market_cap}")

#CAGR
while True:
    years = input("Input the time period that you would like to use in the CAGR calculation (min 4 yrs): ")
    try:
        years = int(years)
        if years >= 4:
            break
        else:
            print("Please enter a number greater than or equal to 4.")
    except ValueError:
        print("Invalid input. Please enter an integer number.")

url = f"https://www.macrotrends.net/stocks/charts/{symbol}/apple/free-cash-flow"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find("table", {"class": "historical_data_table table"})
rows = table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

#last 10 years
years_count = data_rows[:years]

#cagr
start_value = (float(years_count[-1].find_all("td")[1  ].text.replace(",", "")) + float(years_count[-2].find_all("td")[1  ].text.replace(",", ""))) / 2
end_value = (float(years_count[0].find_all("td")[1].text.replace(",", "")) + float(years_count[1].find_all("td")[1].text.replace(",", ""))) / 2
years = len(years_count) - 1  #Number of years

cagr = ((pow(end_value / start_value, 1/years) - 1) * 100) #Calculating CAGR
cagr_rounded = round(cagr, 2) #Rounding 

print('Compound Annual Growth Rate (CAGR) for the last 10 years: ' + str(cagr_rounded) + "%")

print("Last 10 years individual data points (Free Cash Flow):")
for row in years_count:
    cols = [col.text.strip() for col in row.find_all("td")]
    print(cols)

#cash on hand

url = f"https://www.macrotrends.net/stocks/charts/{symbol}/apple/cash-on-hand"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find_all("table", {"class": "historical_data_table table"})
quarterly_table = table[1] 
rows = quarterly_table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

#Latest quarter
latest_quarter = data_rows[:1]

print("Latest quarter's cash on hand:")
for row in latest_quarter:
    cols = [col.text.strip() for col in row.find_all("td")]
    print(cols)


#total liabilities

url = f"https://www.macrotrends.net/stocks/charts/{symbol}/apple/total-liabilities"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find_all("table", {"class": "historical_data_table table"})
quarterly_table = table[1] 
rows = quarterly_table.find_all("tr")
data_rows = [row for row in rows if len(row.find_all("td")) >= 2]

#lastest quarter
latest_quarter = data_rows[:1]

print("Latest quarter's total liabilities:")
for row in latest_quarter:
    cols = [col.text.strip() for col in row.find_all("td")]
    print(cols)
