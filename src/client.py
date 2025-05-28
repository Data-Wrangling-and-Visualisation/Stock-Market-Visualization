from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL
from storage import StorageSQLite


def main():
    # index_scraper = IndexScraper(storage=StorageSQLite())
    # index_scraper.load_content([
    #     # IndexURL('IMOEX', '2003-01-01', '2025-03-28'),
    #     # IndexURL('MIPO', '2021-01-01', '2025-03-28'),
    #     # IndexURL('MCFTR', '2003-01-01', '2025-03-28'),
    #     IndexURL('MCFTRR', '2003-03-03', '2025-05-23')
    # ])
    # index_scraper.scrape_pages()

    trade_scraper = TradeScraper()
    trade_scraper.load_content([
        TradeURL('TMOS', '2020-01-01', '2025-05-27'),
        TradeURL('SBMX', '2018-01-01', '2025-05-27'),
        TradeURL('EQMX', '2022-01-01', '2025-05-27')
    ])
    print('Finished loading')
    trade_scraper.scrape_pages()
    print('Finished scraping')

if __name__ == "__main__":
    main()
