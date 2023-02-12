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

    cur.execute(f'''SELECT id,Open,Close FROM {symbol}''')
    opnclo = cur.fetchall()
    slist = sorted(opnclo, reverse=True)
    
    difflst = []
    id_num = 0
    posit = 0
    while id_num >= 0 and posit < 250:
        id_num = slist[0][0]
        diff = round(slist[posit][1] - slist[posit][2], 5)
        difflst.append(diff)
        id_num = id_num - 1
        posit = posit + 1
 
    val = 0
    poscount = 0
    negcount = 0
    for diff in difflst:
        perc = (diff/slist[val][1]) * 100
        val = val + 1
        # print('percentage change:', round(perc, 2))
        if perc >= 0:
            poscount = poscount + 1

        elif perc <= 0:
            negcount = negcount + 1
        else: continue
    if (poscount/250) > (negcount/250):
        print('GREEN', poscount/2.50, '%', 'chance')
    else:
        print('RED', negcount/2.50, '%', 'chance')
    # print('positive changes:', poscount, '\nnegative changes:', negcount)

#Algorithm needs improvement, currently based on how many red or green days for the year
# -------------------------------------------------------------------------------------

def inquire(ticker):
    from datetime import date
    from datetime import datetime

    x = True

    while x == True:

        request = input('\t Inquire Data:\n'
        '\t  -date (all data on specific date)\n'
        '\t  -max (highest price in data)\n'
        '\t  -min (lowest price in data)\n'
        '\t  -color (what does the database predict tomorrow? +/-)\n'
        '\t  -done (finish program)\n'
        '-')

        if request.lower() == 'done':
            fin()
        elif request.lower() == 'date':
            t = True
            while t == True:
                ymd = (input('Input valid market date from past year in format \"YYYY-MM-DD\": '))
                if ymd.lower() == 'done':
                    fin()
                try:
                    ymd = datetime.strptime(ymd, "%Y-%m-%d")
                    x = str(ymd)
                    ymd = x[:10]
                    
                except:
                    print('Error: must be in YYYY-MM-DD')
                    # nwl()
                    continue

                try: 
                    cur.execute(f'''SELECT * FROM {ticker} Where Date = \'{ymd}\'''')
                    date = cur.fetchone()
                    print('Stock:', date[1], "\n" 'Date:', date[2], "\n" 'Open:', date[3], "\n"  'High:', date[4], "\n"  'Low:', date[5], "\n"  'Close:', date[6], "\n"  'Adjusted Price:', date[7], "\n"  'Volume:', date[8])
                    t = False
                except:
                    print('Date out of range.',
                    'Please try again.')

            break

        elif request.lower() == 'max':
            cur.execute(f'''SELECT Date,max(High) FROM {ticker}''')
            pricemax = cur.fetchone()
            print(pricemax[0]+",", pricemax[1])
            break

        elif request.lower() == 'min':
            cur.execute(f'''SELECT Date,max(Low) FROM {ticker}''')
            pricemax = cur.fetchone()
            print(pricemax[0]+",", pricemax[1])
            break

        elif request.lower() == 'color':
            color(ticker)
            break

        else:
            print('>>>Please input valid entry<<<')
            continue
# -------------------------------------------------------------------------------------
#Presenting bulk data from Database

def bulk(ticker):
    
    x = True 

    while x == True:

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
            cur.execute(f'''SELECT Date,High FROM {ticker}''')
            pricehighs = cur.fetchall()
            for line in pricehighs:
                print(line[0]+",", line[1])
            break

        elif request.lower() == 'lows':
            cur.execute(f'''SELECT Date,Low FROM {ticker}''')
            pricelows = cur.fetchall()
            for line in pricelows:
                print(line[0]+",", line[1])
            break

        elif request.lower() == 'opens':
            cur.execute(f'''SELECT Date,Open FROM {ticker}''')
            priceopens = cur.fetchall()
            for line in priceopens:
                print(line[0]+",", line[1])
            break

        elif request.lower() == 'closes':
            cur.execute(f'''SELECT Date,Close FROM {ticker}''')
            pricecloses = cur.fetchall()
            for line in pricecloses:
                print(line[0]+",", line[1])
            break

        elif request.lower() == 'all':
            cur.execute(f'''SELECT * FROM {ticker}''')
            pricecloses = cur.fetchall()
            for line in pricecloses:
                print(line[1]+",", line[2]+",", line[3],
                line[4], line[5], line[6], line[8])
            print('Stock, Date, Open, High, Low, Close, Volume')
            break

        else:
            print('>>>Please input valid entry<<<')
            continue
# -------------------------------------------------------------------------------------

def run():
    #Program Navigation
    ticker_valid = True
    while ticker_valid:
        
        nwl()
        ticker = input(
        'Please input the ticker you would like to know about: ')

        if ticker.lower() == 'done':
            fin()
        if ticker.lower() == '':
            fin()

        if pull(ticker) == 'not_found':
            continue

        else:

            # nwl()
            print(f'What would you like to do for {ticker}?')
            while ticker_valid:
                nav = input(
                '\tOptions:\n'
                '\t  -bulk (retrieve bulk data)\n'
                '\t  -inq (inquire about specifics)\n'
                '\t  -done (finish program)\n'
                '-'
                )
                if nav.lower() == 'bulk':
                    bulk(ticker)
                    break
                elif nav.lower() == 'inq':
                    inquire(ticker)
                    break
                elif nav.lower() == 'done':
                    fin()
                else:
                    # nwl()
                    print('>>>Please input valid entry<<<')
                    continue


        # time.sleep(2)

if __name__ == '__main__':
    run()


