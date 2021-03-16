import gspread
from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
import pandas
from date import time_delta_sufficient
from stock import Stock
import datetime
import time
import os

deltas = {
    'Closing_Price_t0': 0,
    'Closing_Price_t1': 1,
    'Closing_Price_t2': 2,
    'Closing_Price_t7': 7,
}

change_deltas = {
    'Closing_Price_t0': 'Change_t0',
    'Closing_Price_t1': 'Change_t1',
    'Closing_Price_t2': 'Change_t2',
    'Closing_Price_t7': 'Change_t7',
}

wks_name = {
    0: 'summary',
    1: 'Stockwits',
    2: 'Finviz',
    4: 'Deadnsyde',
    3: 'Tradingview Scanner'
}
SPREADSHEET_KEY = os.environ.get('spredsheet_key')
stock = Stock()

class Sheet:
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(os.environ.get('google_api_cred'),self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open('Pennystock Tracker')

    def post_data(self, sheet_name, values):
        self.sheet.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': values})

    def open(self, sheet_name):
        sheet = self.sheet.get_worksheet(sheet_name)
        response = sheet.get_all_records()
        export_data = pandas.DataFrame.from_dict(response, orient='columns')
        return export_data

    def update_sheet(self, sheet_name, data):
        df = data
        spreadsheet_key = SPREADSHEET_KEY
        d2g.upload(df, spreadsheet_key, wks_name=wks_name[sheet_name], credentials=self.creds, row_names=False)


    def update(self):
        sheets = self.sheet.fetch_sheet_metadata()['sheets']
        for ws in sheets:
            #ws index 0 is the summary sheet
            if ws['properties']['index'] != 0:
                sheet_index = ws['properties']['index']
                # update total signals
                data = self.sheet.get_worksheet(sheet_index)
                foo = data.get_all_records()
                df = pandas.DataFrame.from_dict(foo, orient='columns')
                # update total signals
                df['Total_Signals'] = df.apply(lambda row: '' if row['Other_Signals'] == '' else len(row['Other_Signals'].split(',')), axis=1)

                # update days elapsed
                today = datetime.date.today()
                df['t-_t0'] = df.apply(lambda row: (today - datetime.datetime.strptime(row['Log_Date_t0'], '%Y-%m-%d').date()).days, axis=1)

                # update absolute change based on last quote stored
                df['Absolute_Change'] = df.apply(lambda row: float(row['Closing_Price_t7'])/float(row['Log_Price_Closing_Price_t0']) if row['Absolute_Change'] == '' and row['Closing_Price_t7'] != '' and row['Closing_Price_t7'] != 'no data'
                                                 else (float(row['Closing_Price_t2'])/float(row['Log_Price_Closing_Price_t0']) if row['Closing_Price_t2'] != '' and row['Closing_Price_t2'] != 'no data'
                                                       else
                                                       (float(row['Closing_Price_t1'])/float(row['Log_Price_Closing_Price_t0']) if row['Closing_Price_t1'] != '' and row['Closing_Price_t1'] != 'no data'
                                                        else
                                                        (float(row['Closing_Price_t0'])/float(row['Log_Price_Closing_Price_t0']) if row['Closing_Price_t0'] != '' and row['Closing_Price_t0'] != 'no data'
                                                         else ''))),axis=1)
                df['Absolute_Change'] = df.apply(lambda row: round(float(row['Absolute_Change']),2) if row['Absolute_Change'] != '' else row['Absolute_Change'], axis=1)

                # update change
                df['Change_t7'] = df.apply(lambda row: round(float(row['Closing_Price_t7']) / float(row['Log_Price_Closing_Price_t0']), 2) if row['Change_t7'] == '' and row['Closing_Price_t7'] != '' and row['Closing_Price_t7'] != 'no data' else row['Change_t7'], axis=1)
                df['Change_t2'] = df.apply(lambda row: round(float(row['Closing_Price_t2'])/float(row['Log_Price_Closing_Price_t0']),2) if  row['Change_t2'] == '' and row['Closing_Price_t2'] != '' and row['Closing_Price_t2'] != 'no data' else row['Change_t2'], axis=1)
                df['Change_t1'] = df.apply(lambda row: round(float(row['Closing_Price_t1']) / float(row['Log_Price_Closing_Price_t0']),2) if row['Change_t1'] == '' and row['Closing_Price_t1'] != '' and row['Closing_Price_t1'] != 'no data' else row['Change_t1'], axis=1)
                df['Change_t0'] = df.apply(lambda row: round(float(row['Closing_Price_t0']) / float(row['Log_Price_Closing_Price_t0']), 2) if  row['Change_t0'] == '' and row['Closing_Price_t0'] != '' and row['Closing_Price_t0'] != 'no data' else row['Change_t0'], axis=1)

                # update quotes
                df['Closing_Price_t0'] = df.apply(lambda row: stock.get_quote(row['Ticker'], time_delta_sufficient(row['Log_Date_t0'], deltas['Closing_Price_t0'])[1]) if row['Closing_Price_t0'] == '' and time_delta_sufficient(row['Log_Date_t0'], deltas['Closing_Price_t0'])[0] else row['Closing_Price_t0'], axis=1)
                df['Closing_Price_t1'] = df.apply(lambda row: stock.get_quote(row['Ticker'],time_delta_sufficient(row['Log_Date_t0'],deltas['Closing_Price_t1'])[1]) if row['Closing_Price_t1'] == '' and row['Closing_Price_t0'] != '' and time_delta_sufficient(row['Log_Date_t0'], deltas['Closing_Price_t1'])[0] else row['Closing_Price_t1'], axis=1)
                df['Closing_Price_t2'] = df.apply(lambda row: stock.get_quote(row['Ticker'],time_delta_sufficient(row['Log_Date_t0'],deltas['Closing_Price_t2'])[1]) if row['Closing_Price_t2'] == '' and row['Closing_Price_t1'] != '' and time_delta_sufficient(row['Log_Date_t0'], deltas['Closing_Price_t2'])[0] else row['Closing_Price_t2'], axis=1)
                df['Closing_Price_t7'] = df.apply(lambda row: stock.get_quote(row['Ticker'],time_delta_sufficient(row['Log_Date_t0'],deltas['Closing_Price_t7'])[1]) if row['Closing_Price_t7'] == '' and row['Closing_Price_t2'] != '' and time_delta_sufficient(row['Log_Date_t0'], deltas['Closing_Price_t7'])[0] else row['Closing_Price_t7'], axis=1)

                self.update_sheet(sheet_index, df)

    def clean_duplicates(self, sheet_name):
        data = self.open(sheet_name)

        test = data.duplicated(['Ticker'])
        trial = data[test]
        x = {}
        for index, row in trial.iterrows():
            try:
                a = x[row.Ticker]
            except KeyError:
                x[row.Ticker] = f'{row.Signal} ({row.Log_Date_t0})'
            else:
                if row.Signal in x[row.Ticker]:
                    continue
                else:
                    x[row.Ticker] = f'{x[row.Ticker]}, {row.Signal} ({row.Log_Date_t0})'

        #drop duplicates
        foo = data.drop_duplicates(['Ticker'])

        for index, row in foo.iterrows():
            try:
                #checking if ticker is in duplicate dictionary
                b = x[row.Ticker]
            except KeyError:
                continue
            else:
                if row.Other_Signals == '':
                    foo.at[row.name, 'Other_Signals'] = f'{x[row.Ticker]}'
                else:
                    foo.at[row.name, 'Other_Signals'] = f'{row.Other_Signals}, {x[row.Ticker]}'


        self.update_sheet(sheet_name, foo)

    def summary(self):
        dataframe = pandas.DataFrame()
        sheets = self.sheet.fetch_sheet_metadata()['sheets']
        for ws in sheets:
            if ws['properties']['index'] != 0:
                sheet_name = ws['properties']['title']
                data = self.sheet.get_worksheet(ws['properties']['index'])
                foo = data.get_all_records()
                df = pandas.DataFrame.from_dict(foo, orient='columns')
                for index, row in df.iterrows():
                    df.at[row.name, 'Signal'] = f'({sheet_name}) {row.Signal}'

                dataframe = dataframe.append(df, ignore_index=True)
                self.update_sheet(0, dataframe)

        self.sort_by_date(0)
        self.clean_duplicates(0)

    def sort_by_date(self, sheet_name):
        values = self.open(sheet_name)
        new_values = values.sort_values(by=['Log_Date_t0'])
        self.update_sheet(0, new_values)

