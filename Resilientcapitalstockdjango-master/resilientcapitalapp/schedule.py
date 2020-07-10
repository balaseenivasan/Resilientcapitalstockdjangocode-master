import json

import pandas
import pandas as pd
from django.shortcuts import render
from datetime import datetime,date,timezone
from resilientcapitalapp.forms import UserForm,UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from resilientcapitalapp.models import SpNasdaqDmaData
import csv
import numpy as np
import yfinance as yf
import datetime  as dt
from pandas_datareader import data as pdr
import requests
import lxml.html as lh
import gspread
import pytz
import schedule
import time


def my_view(request, *args, **kwargs):
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
    for j in range(2, len(tr_elements)):
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
    col_one_list = df["Symbol\n"].tolist()
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

    stock1 = '^GSPC'
    today = dt.datetime.now()

    yesterday = today - dt.timedelta(days=1)

    df = yf.download(stock1, period="1d", interval="1d")
    fdtest = df.tail(1)
    sp = fdtest.index[0]
    yesterday1 = sp.strftime("%m/%d/%Y")
    sp500_ret = round(fdtest['Adj Close'].iloc[-1], 2)
    #sheetlastdate = sheet200.cell(curentrow200 - 1, 1).value
    # yesterday1 = yesterday.strftime("%m/%d/%Y")
    row200 = [yesterday1, sp500_ret, SPabove200]
    row50 = [yesterday1, sp500_ret, SPabove50]
    date = pd.to_datetime(yesterday1, infer_datetime_format=True)
    #if (yesterday1 != sheetlastdate):
        #SpNasdaqDmaData.objects.create(date=yesterday1, sp500=sp500_ret, dma50=SPabove200)
    #SpNasdaqDmaData.objects.create(date = date, sp500 = sp500_ret, dma50 = SPabove50)

    #sp500 = 336
    #dma50 = 54.02

    # Iterate through all the data items
    #for i in range(len(date)):

        # Insert in the database
    #SpNasdaqDmaData.objects.create(date = date, sp500 = sp500, dma50 = dma50)


    # Getting all the stuff from database
    query_results = SpNasdaqDmaData.objects.all();

    # Creating a dictionary to pass as an argument
    context = { 'query_results' : query_results }
    print("Database Updated")
    # Returning the rendered html
    return render(request, "home.html", context)
def my_viewhelo():
    print('Hello')

schedule.every(10).seconds.do(my_viewhelo)
while 1:
    schedule.run_pending()
    time.sleep(1)