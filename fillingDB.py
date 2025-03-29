from storage import StorageSQLite
from scraper import Scraper, URL

store = StorageSQLite()
scrap = Scraper(storage=store)

tickers = [
    'https://www.moex.com/ru/index/IMOEX/archive?from=2004-12-01&till=2025-03-27&sort=TRADEDATE&order=desc' #Индекс Мосбиржи
    #'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=TMOS&boardgroupid=57&mode_type=history&date_from=2020-08-26&date_till=2025-03-28', # БПИФ ТБанк 
    #'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=SBMX&boardgroupid=57&mode_type=history&date_from=2018-09-17&date_till=2025-03-28', # БПИФ Сбер
    #'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=EQMX&boardgroupid=57&mode_type=history&date_from=2020-01-01&date_till=2025-03-28' # БПИФ от ВТБ
]
urls = [URL.construct_from_url(x) for x in tickers]
scrap.load_content(urls)
scrap.scrape_pages()

x = scrap.load_page_data('IMOEX')
print(x)