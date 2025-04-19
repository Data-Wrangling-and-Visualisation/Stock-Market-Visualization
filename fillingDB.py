from storage import StorageSQLite
from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL

store = StorageSQLite()
indexScrap = IndexScraper(storage=store)
tradeScrap = TradeScraper(storage=store)

tickersIndexes = [
    # Индекс Мосбиржи
    'https://www.moex.com/ru/index/IMOEX/archive?from=2015-01-01&till=2025-03-27&sort=TRADEDATE&order=desc',
    'https://www.moex.com/ru/index/MIPO/archive?from=2021-11-11&till=2025-04-18&sort=TRADEDATE&order=desc'
]
tickersETFs = [
    # БПИФ ТБанк starts 2020
    # 'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=TMOS&boardgroupid=57&mode_type=history&date_from=2020-01-01&date_till=2025-03-28',
    # # БПИФ Сбер starts 2018
    # 'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=SBMX&boardgroupid=57&mode_type=history&date_from=2018-01-01&date_till=2025-03-28',
    # # БПИФ от ВТБ starts 2020
    # 'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=EQMX&boardgroupid=57&mode_type=history&date_from=2020-01-01&date_till=2025-03-28'
]
indexUrls = [IndexURL.construct_from_url(x) for x in tickersIndexes]
indexScrap.load_content(indexUrls)
indexScrap.scrape_pages()


tradeUrls = [TradeURL.construct_from_url(x) for x in tickersETFs]
tradeScrap.load_content(tradeUrls)
tradeScrap.scrape_pages()
