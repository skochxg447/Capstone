import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error
import re
import time
import datetime

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('Stock.sqlite')
cur = conn.cursor()

# -------------------------------------------------------------------------------------
def fin():
    '''Ending the program'''
    print('========' * 7)
    print('Program Finished')
    quit()

def nwl():
    '''Newline seperation for reader'''
    print('--------' * 7)

# -------------------------------------------------------------------------------------

def pull(ticker):
    '''Prompt for Ticker and Scrape for data'''

    # Get today's date
    today = datetime.date.today()

    # Convert today's date to Unix time
    unix_time_today = int(time.mktime(today.timetuple()))

    # Calculate the date one year ago
    one_year_ago = today - datetime.timedelta(days=365)

    # Convert one year ago date to Unix time
    unix_time_one_year_ago = int(time.mktime(one_year_ago.timetuple()))

    url = (
        f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}'
        f'?period1={unix_time_one_year_ago}'
        f'&period2={unix_time_today}'
        '&interval=1d'
        '&events=history'
        '&includeAdjustedClose=true'
    )
    try:
        file = urllib.request.urlopen(url, context=ctx).read()

    except:
        print('Please only input a Stock Ticker')
        return 'not_found'

    data = file.decode().split()

    newlist = [row.split(',') for row in data]
    newlist = [row for row in newlist if len(row) > 6]

    # Create Table and Input data
    cur.execute(f'''DROP TABLE IF EXISTS {ticker}''')

    cur.execute(f'''CREATE TABLE IF NOT EXISTS {ticker}
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Stock TEXT, 
    Date TEXT UNIQUE, 
    Open INTEGER,
    High INTEGER, 
    Low INTEGER, 
    Close INTEGER, 
    Adj INTEGER,
    Volume INTEGER)''')

    cur.executemany(f'''INSERT INTO {ticker}
    (Stock, Date, Open, High, Low, Close, Adj, Volume) 
    VALUES (?,?,?,?,?,?,?,?)''', [(ticker,) + tuple(row) for row in newlist])

    conn.commit()
    print('Database Updated.')
    return 'found'


# -------------------------------------------------------------------------------------
#Data Manipulation (AKA -inquire)
def color(symbol):
    cur.execute(f'SELECT Open, Close FROM {symbol} ORDER BY id DESC LIMIT 250')
    opnclo = cur.fetchall()
    difflst = [round(x[0]-x[1], 5) for x in opnclo]
    
    poscount = sum(1 for diff in difflst if (diff / opnclo[0][0]) * 100 >= 0)
    negcount = 250 - poscount
    
    if poscount > negcount:
        print('GREEN', round(poscount / 2.50, 2), '%', 'chance')
    else:
        print('RED', round(negcount / 2.50, 2), '%', 'chance')

    # print('positive changes:', poscount, '\nnegative changes:', negcount)

#Algorithm needs improvement, currently based on how many red or green days for the year
# -------------------------------------------------------------------------------------

def inquire(ticker):
    from datetime import datetime

    while True:
        request = input('''Inquire Data:
            - date (all data on specific date)
            - max (highest price in data)
            - min (lowest price in data)
            - color (what does the database predict tomorrow? +/-)
            - done (finish program)
            - ''')

        if request.lower() == 'done':
            fin()
        elif request.lower() == 'date':
            while True:
                ymd = input('Input valid market date from past year in format "YYYY-MM-DD": ')
                if ymd.lower() == 'done':
                    fin()
                try:
                    ymd = datetime.strptime(ymd, "%Y-%m-%d").strftime("%Y-%m-%d")
                except ValueError:
                    print('Error: must be in YYYY-MM-DD')
                    continue

                try:
                    cur.execute(f"SELECT * FROM {ticker} WHERE Date = '{ymd}'")
                    date = cur.fetchone()
                    print(f'''Stock: {date[1]}
                    Date: {date[2]}
                    Open: {date[3]}
                    High: {date[4]}
                    Low: {date[5]}
                    Close: {date[6]}
                    Adjusted Price: {date[7]}
                    Volume: {date[8]}''')
                    break
                except:
                    print('Date out of range. Please try again.')
            break

        elif request.lower() == 'max':
            cur.execute(f"SELECT Date, MAX(High) FROM {ticker}")
            pricemax = cur.fetchone()
            print(pricemax[0], pricemax[1])
            break

        elif request.lower() == 'min':
            cur.execute(f"SELECT Date, MIN(Low) FROM {ticker}")
            pricemax = cur.fetchone()
            print(pricemax[0], pricemax[1])
            break

        elif request.lower() == 'color':
            color(ticker)
            break

        else:
            print('Please input a valid entry.')
            continue

# -------------------------------------------------------------------------------------
#Presenting bulk data from Database
def bulk(ticker):
    while True:
        request = input('\tBulk Data:\n'
                        '\t  -highs (all of the highs for the last year)\n'
                        '\t  -lows (all of the lows for the last year)\n'
                        '\t  -opens (all of the opening prices for the last year)\n'
                        '\t  -closes (all of the closing prices for the last year)\n'
                        f'\t  -all (all of the data on {ticker})\n'
                        '\t  -done (finish program)\n'
                        '-')

        if request.lower() == 'done':
            fin()

        elif request.lower() == 'highs':
            fetch_and_print_all(cur, f'SELECT Date, High FROM {ticker}')
            break

        elif request.lower() == 'lows':
            fetch_and_print_all(cur, f'SELECT Date, Low FROM {ticker}')
            break

        elif request.lower() == 'opens':
            fetch_and_print_all(cur, f'SELECT Date, Open FROM {ticker}')
            break

        elif request.lower() == 'closes':
            fetch_and_print_all(cur, f'SELECT Date, Close FROM {ticker}')
            break

        elif request.lower() == 'all':
            fetch_and_print_all(cur, f'SELECT * FROM {ticker}',
                                columns='Stock, Date, Open, High, Low, Close, Volume')
            break

        else:
            print('>>>Please input valid entry<<<')


def fetch_and_print_all(cursor, query, columns=None):
    cursor.execute(query)
    data = cursor.fetchall()
    if columns:
        print(columns)
    for row in data:
        print(', '.join(str(cell) for cell in row))
# -------------------------------------------------------------------------------------

def run():
    while True:
        nwl()
        ticker = input('Please input the ticker you would like to know about: ')

        if not ticker:
            fin()

        if ticker.lower() == 'done':
            fin()

        if pull(ticker) == 'not_found':
            continue

        while True:
            nwl()
            print(f'What would you like to do for {ticker}?')
            nav = input('\tOptions:\n\t  -bulk (retrieve bulk data)\n'
                        '\t  -inq (inquire about specifics)\n'
                        '\t  -done (finish program)\n-')

            if nav.lower() == 'bulk':
                bulk(ticker)
                break

            if nav.lower() == 'inq':
                inquire(ticker)
                break

            if nav.lower() == 'done':
                fin()

            print('>>>Please input valid entry<<<')

        # time.sleep(2)

if __name__ == '__main__':
    run()


