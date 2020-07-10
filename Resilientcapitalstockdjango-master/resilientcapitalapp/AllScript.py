import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import requests
import lxml.html as lh
import gspread
import pytz
from oauth2client.service_account import ServiceAccountCredentials

yf.pdr_override()
utc = pytz.utc
utc_dt = dt.datetime.now()
# eastern = pytz.timezone('US/Eastern')
# loc_dt = utc_dt.astimezone(eastern)
# fmt = '%Y-%m-%d %H:%M:%S %Z%z'
# loc_dt.strftime(fmt)
day = dt.timedelta(400)
start = utc_dt - day

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
# Create a handle, page, to handle the contents of the website
page = requests.get(url)
# Store the contents of the website under doc
doc = lh.fromstring(page.content)
# Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')
# Create empty list
col = []
i = 0
# For each row, store each first element (header) and an empty list
for t in tr_elements[1]:
    i += 1
    name = t.text_content()
    col.append((name, []))
for j in range(1, len(tr_elements)):
    # T is our j'th row
    T = tr_elements[j]

    # If row is not of size 10, the //tr data is not from our table
    if len(T) != 9:
        break

    # i is the index of our column
    i = 0

    # Iterate through each element of the row
    for t in T.iterchildren():
        data = t.text_content()

        # Check if row is empty
        if i > 0:
            # Convert any numerical value to integers
            try:
                data = int(data)
            except:
                pass
        # Append the data to the empty list of the i'th column
        col[i][1].append(data)
        # Increment i for the next column
        i += 1
[len(C) for (title, C) in col]
Dict = {title: column for (title, column) in col}
df = pd.DataFrame(Dict)
col_one_list = df["MMM\n"].tolist()
splist = []

for element in col_one_list:
    splist.append(element.strip())
for i in range(len(splist)):
    if '.' in splist[i]:
        splist[i] = splist[i].replace(".", "-")
count = 0
count1 = 0
for i in range(len(splist)):
    stock = splist[i]
    print(stock)
    print(start, utc_dt)
    df = pdr.get_data_yahoo(stock, start, utc_dt)
    isempty = df.empty
    if (isempty != True):
        df['200 dma'] = df['Adj Close'].rolling(200).mean().round(5)
        df['50 dma'] = df['Adj Close'].rolling(50).mean().round(5)
        df['over200'] = df['Adj Close'] > df['200 dma']  # Check if close > 200 day moving avg across all dates
        df['over50'] = df['Adj Close'] > df['50 dma']  # Check if close > 50 day moving avg across all dates
        if (df['over200'].iloc[
            -1] == True): count = count + 1  # check if the last 'over200' value is True. If so, increase count
        if (df['over50'].iloc[
            -1] == True): count1 = count1 + 1  # check if the last 'over50' value is True. If so, increase count

print(count)
print(len(splist))
print(count1)
SPabove200 = round((float(count) / float(len(splist))) * 100, 1)
print(count)
print(float(count) / float(len(splist)))
print(SPabove200)
SPabove50 = round((float(count1) / float(len(splist))) * 100, 1)
# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet200 = client.open("SpNasdaqdmaData").worksheet("SP200")
sheet50 = client.open("SpNasdaqdmaData").worksheet("SP50")

curentrow200 = len(sheet200.get_all_values()) + 1
curentrow50 = len(sheet50.get_all_values()) + 1

stock1 = '^GSPC'
today = dt.datetime.now()

yesterday = today - dt.timedelta(days=1)

df = yf.download(stock1, period="1d", interval="1d")
fdtest = df.tail(1)
sp = fdtest.index[0]
yesterday1 = sp.strftime("%m/%d/%Y")
sp500_ret = round(fdtest['Adj Close'].iloc[-1], 2)
sheetlastdate = sheet200.cell(curentrow200 - 1, 1).value
# yesterday1 = yesterday.strftime("%m/%d/%Y")
row200 = [yesterday1, sp500_ret, SPabove200]
row50 = [yesterday1, sp500_ret, SPabove50]

index200 = curentrow200
index50 = curentrow50
if (yesterday1 != sheetlastdate):
    sheet200.insert_row(row200, index200)
    sheet50.insert_row(row50, index50)

