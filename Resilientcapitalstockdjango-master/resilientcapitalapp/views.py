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
from resilientcapitalapp.models import SpNasdaqDmaData,SpNasdaq200DmaData,SpIssuesData,SpRsi,\
        SpBollingerbands,Spnewhighlow,SPcorrection,SPbearmarket,NasdaqDmaData,Nasdaq200DmaData,NasdaqIssuesData,NasdaqRsi,NasdaqBollingerbands,Nasdaqnewhighlow

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
from oauth2client.service_account import ServiceAccountCredentials

def index(request):
    return render(request,'index.html')
@login_required
def special(request):
    return HttpResponse("You are logged in !")
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'login.html', {})


def save_datas(request):
    with open('SpNasdaqdmaData - SP50.csv') as csvfile:
         reader = csv.DictReader(csvfile)
         for row in reader:
             p = SPbearmarket(date=pd.to_datetime(row['Date'], infer_datetime_format=True), sp500=row['S&P 500'],
                              Spbearmarket=row['% of S&P 500 members in a bear market']
                                  )

             p.save()

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
    po = SpNasdaqDmaData.objects.latest('date')
    print(po.date)
    if (date != po.date):
        SpNasdaqDmaData.objects.create(date=date, sp500=sp500_ret, dma50=SPabove200)
        SpNasdaqDmaData.objects.create(date = date, sp500 = sp500_ret, dma50 = SPabove50)

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

    # Returning the rendered html
    return render(request, "home.html", context)
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def plot_view(request):
    dataset  = SpNasdaqDmaData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma50_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma50_series.append(entry.dma50)
    dates = date
    values = sp500_series
    values1 = dma50_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp50dma.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma50_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })

   # query_results = list(SpNasdaqDmaData.objects.all())
    #print(query_results)
    # Creating a dictionary to pass as an argument
    #context = {'query_results': query_results}
    #return render(request, "home.html", context)
def plot_view200dma(request):
    dataset  = SpNasdaq200DmaData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.dma200)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]

    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp200dma.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })

def plot_spissuesview(request):
    dataset  = SpIssuesData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPUpIssuesRadio)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'spissues.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sprsi70view(request):
    dataset  = SpRsi.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPRsi70)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sprsi70.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma50_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sprsi30view(request):
    dataset  = SpRsi.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPRsi30)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sprsi30.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma50_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_spupperbolingerview(request):
    dataset  = SpBollingerbands.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPupperBollingerBand)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'spupperbolinger.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_splowerbolingerview(request):
    dataset  = SpBollingerbands.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPlowerBollingerBand)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'splowerbolinger.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sp52weekshighview(request):
    dataset  = Spnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SP52weekhigh)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp52weekshigh.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sp52weekslowview(request):
    dataset  = Spnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SP52weeklow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp52weekslow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sphighlowview(request):
    dataset  = Spnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SPSPhighlow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sphighlow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sp24weekshighview(request):
    dataset  = Spnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SP24weekhigh)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp24weekshigh.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_sp24weekslowview(request):
    dataset  = Spnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.SP24weeklow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'sp24weekslow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_spcorrectionview(request):
    dataset  = SPcorrection.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.Spcorrection)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'spcorrection.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_spbearmarketview(request):
    dataset  = SPbearmarket.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.sp500)
        dma200_series.append(entry.Spbearmarket)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'spbearmarket.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_view50dma(request):
    dataset  = NasdaqDmaData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.dma50)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    print(data)
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq50dma.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaq200dmaview(request):
    dataset  = Nasdaq200DmaData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.dma200)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    print(data)
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq200dma.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqissuesview(request):
    dataset  = NasdaqIssuesData.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.nasdaqUpIssuesRadio)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    print(data)
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaqissues.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqrsi70view(request):
    dataset  = NasdaqRsi.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.NasdaqRsi70)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    print(data)
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaqrsi70.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqrsi30view(request):
    dataset  = NasdaqRsi.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.NasdaqRsi30)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    print(data)
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaqrsi30.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqupperbolingerview(request):
    dataset  = NasdaqBollingerbands.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.NasdaqupperBollingerBand)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'spupperbolinger.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqplowerbolingerview(request):
    dataset  = NasdaqBollingerbands.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.NasdaqlowerBollingerBand)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'splowerbolinger.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaq52weekshighview(request):
    dataset  = Nasdaqnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.Nasdaq52weekhigh)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq52weekshigh.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaq52weekslowview(request):
    dataset  = Nasdaqnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.Nasdaq52weeklow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq52weekslow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaqhighlowview(request):
    dataset  = Nasdaqnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.Nasdaqhighlow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaqhighlow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaq24weekshighview(request):
    dataset  = Nasdaqnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.Nasdaq24weekhigh)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq24weekshigh.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
def plot_nasdaq24weekslowview(request):
    dataset  = Nasdaqnewhighlow.objects.all().order_by('date')

    date = list()
    sp500_series = list()
    dma200_series = list()
    for entry in dataset:
        mydate = datetime.strptime(str(entry.date), '%Y-%m-%d')

        timestamp = datetime.timestamp(mydate)
        date.append(timestamp *1000)
        sp500_series.append(entry.nasdaq100)
        dma200_series.append(entry.Nasdaq24weeklow)
    dates = date
    values = sp500_series
    values1 = dma200_series

    data = [[d, v] for d, v in zip(dates, values)]
    data1 = [[d, v] for d, v in zip(dates, values1)]

    return render(request, 'nasdaq24weekslow.html', {
        'sp500_series': json.dumps(data,sort_keys=False,default=json_serial),
        'dma200_series': json.dumps(data1,sort_keys=False,default=json_serial)
    })
from apscheduler.schedulers.blocking import BlockingScheduler

def some_job():
    dic =  list()
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheetsp = client.open("newhighlow").worksheet('SPhigh52')
    curentrowsp = len(sheetsp.get_all_values())
    dic = sheetsp.row_values(curentrowsp)
    print(dic)
    #row = [yesterday1, sp_ret, high52percent]
    p = Spnewhighlow(date=pd.to_datetime(dic[0], infer_datetime_format=True), sp500=dic[1],
                     SP52weekhigh=dic[2],SP52weeklow=dic[2],SPSPhighlow=dic[2],SP24weekhigh=dic[2],SP24weeklow=dic[2]
                     )

    p.save()

    #index = curentrowsp
    #if (yesterday1 != sheetlastdate):
     #   sheetsp.insert_row(row, index)
    print ("Decorated job")

scheduler = BlockingScheduler()
#scheduler.add_job(some_job, 'interval', seconds=10)
scheduler.add_job(some_job, 'cron', day_of_week='mon-fri', hour=8, minute=40)
scheduler.start()