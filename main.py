from crawler import Crawler
from stock import Stock
import datetime
import pandas as pd
from sheets import Sheet
from time import sleep

# set desired cutoff price here
PRICE = 10

stock = Stock()
sheet = Sheet()

class Stockwits:
    def __init__(self):
        self.urls = ['https://stocktwits.com/rankings/watchers','https://stocktwits.com/rankings/trending','https://stocktwits.com/rankings/most-active']

    def get_data(self):
        data = []
        for url in self.urls:
            crawler = Crawler(url)
            html = crawler.driver.page_source
            content = crawler.crawl(html)
            for row in content.find_all(class_='st_PaKabGw'):
                try:
                    price = float(row.find(class_='st_vuSv7f4').text)
                except:
                    price = '---'
                    ticker = row.find(class_='st_3ua_jwB').text
                    if ticker[-2:] == '-X':
                        continue

                    dict = {
                        'signal': url.split('/')[-1],
                        'sector': stock.sector(ticker),
                        'ticker': ticker,
                        'log-date': str(datetime.date.today()),
                        'log-price': price,
                        'change': '',
                        'description': '',  ##stock.description(ticker)
                    }
                    data.append(dict)
                else:
                    if price <= PRICE:
                        ticker = row.find(class_='st_3ua_jwB').text
                        # this means it is crypto, which requires another api and investment focus
                        if ticker[-2:] == '-X':
                            continue

                        change_span = row.find(class_='st_1xcwpLL')
                        change_a = change_span.find('path').attrs['d'][0]
                        if change_a == 'M':
                            change = 'red'
                        elif change_a =='m':
                            change = 'green'

                        dict = {
                            'signal': url.split('/')[-1],
                            'sector': stock.sector(ticker),
                            'ticker': ticker,
                            'log-date': str(datetime.date.today()),
                            'log-price': price,
                            'change': change,
                            'description': '',##stock.description(ticker)
                        }
                        data.append(dict)


        dataframe = pd.DataFrame(data)
        values = dataframe.values.tolist()
        sheet.post_data('stockwits', values)

        sheet.clean_duplicates(1)

class Finviz:
    def __init__(self):
        self.urls = ['https://finviz.com/screener.ashx?v=111&s=it_latestbuys&f=sec_healthcare,sh_price_u10','https://finviz.com/screener.ashx?v=121&f=geo_usa,sh_avgvol_o500,sh_float_u20,sh_price_u2,ta_sma20_cross50&ft=4','https://finviz.com/screener.ashx?v=111&s=ta_mostactive&f=sec_healthcare,sh_price_u10&o=-change','https://finviz.com/screener.ashx?v=111&s=ta_unusualvolume&f=sec_healthcare,sh_price_u10&o=-relativevolume']

    def get_data(self):
        data = []

        def run(curl):
            crawler = Crawler(curl)
            driver = crawler.driver
            sleep(5)
            consent = driver.find_element_by_class_name('ConsentManager__Overlay-np32r2-0')
            read = consent.find_element_by_xpath('//button[.="Lesen Sie mehr, um Präferenzen zu akzeptieren"]')
            read.click()
            sleep(1)
            accept = consent.find_element_by_xpath('//button[.="Alles akzeptieren"]')
            accept.click()
            sleep(1)
            html = crawler.driver.page_source
            content = crawler.crawl(html)

            try:
                for row in content.find_all(class_=['table-dark-row-cp', 'table-light-row-cp']):
                    ticker = row.find('a', class_='screener-link-primary').text
                    try:
                        if len(row.find_all('span', class_=['is-green', 'is-red'])) > 1:
                            price = row.find_all('span', class_=['is-green', 'is-red'])[-2]
                            pricex = price.text
                        else:
                            price = row.find('span', class_=['is-green', 'is-red'])
                            pricex = price.text
                        change = price.attrs['class'][0].split('-')[1]
                    except:
                        pricex = stock.log_price(ticker)
                        change = ''
                    try:
                        signal = url.split('s=')[1].split('_')[1].split('&')[0]
                    except:
                        signal = 'Special Filter'
                        sector = ''
                    else:
                        sector = url.split('sec_')[1].split(',')[0]

                    dict = {
                        'signal': signal,
                        'sector': sector,
                        'ticker': ticker,
                        'log-date': str(datetime.date.today()),
                        'log-price': pricex,
                        'change': change,
                        'description': '',  ##stock.description(ticker)
                    }
                    data.append(dict)

                try:
                    button = crawler.driver.find_element_by_xpath('//b[.="next"]')
                    button.click()
                    test = crawler.driver.current_url
                    run(test)
                except:
                    return
            except:
                print(f'no data for this url: {url}')

        for url in self.urls:
            run(url)

        dataframe = pd.DataFrame(data)
        values = dataframe.values.tolist()
        sheet.post_data('finviz', values)

        sheet.clean_duplicates(2)

class Tradingview:
    def __init__(self):
        self.url = 'https://www.tradingview.com/screener/'

    def get_data(self):
        data = []
        SCREENERS = 2
        crawler = Crawler(self.url)
        driver = crawler.driver
        login = driver.find_element_by_xpath('//a[.="Sign in"]')
        login.click()
        crawler.fb_login(driver)
        sleep(10)

        for n in range (0,SCREENERS):
            screener_choice = driver.find_element_by_css_selector('div[data-name="screener-filter-sets"]')
            screener_choice.click()
            sleep(1)
            sets = driver.find_element_by_class_name('tv-screener-popup__item--presets')
            screeners = sets.find_elements_by_class_name('tv-dropdown-behavior__item')
            name = screeners[n].text
            screeners[n].click()
            sleep(2)

            html = driver.page_source
            content = crawler.crawl(html)
            for row in content.find_all(class_='tv-screener-table__result-row'):
                price = row.find('td', class_='tv-data-table__cell tv-screener-table__cell tv-screener-table__cell--with-marker').text
                dict = {
                    'signal': name,
                    'sector': row.find(attrs={'data-field-key':'sector'}).text,
                    'ticker': row.find(class_='tv-screener__symbol apply-common-tooltip').text,
                    'log-date': str(datetime.date.today()),
                    'log-price': price,
                    'change': 'green',
                    'description': '',#stock.description(ticker)
                }
                data.append(dict)

        dataframe = pd.DataFrame(data)
        values = dataframe.values.tolist()
        sheet.post_data('Tradingview Scanner', values)

        sheet.clean_duplicates(3)

stockwits = Stockwits()
stockwits.get_data()

finviz = Finviz()
finviz.get_data()

trav = Tradingview()
trav.get_data()

sheet.update()
sheet.summary()



