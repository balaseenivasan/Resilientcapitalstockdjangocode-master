from builtins import list
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def my_scheduled_job():
    dic = list()
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheetsp1 = client.open("newhighlow").worksheet('SPlow52')
    curentrowsp = len(sheetsp1.get_all_values()) + 1
    dic = sheetsp1.row_values(curentrowsp)
    print(dic)
    # row = [yesterday1, sp_ret, high52percent]

    # index = curentrowsp
    # if (yesterday1 != sheetlastdate):
    #   sheetsp.insert_row(row, index)
    print ("Decorated cron job")