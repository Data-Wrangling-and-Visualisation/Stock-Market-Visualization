from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL
from storage import StorageSQLite


def main():
    index_scraper = IndexScraper(storage=StorageSQLite())
    index_scraper.load_content([
        IndexURL('IMOEX', '2005-01-01', '2025-03-28'),
        IndexURL('MIPO', '2021-11-11', '2025-03-28'),
        IndexURL('MCFTR', '2003-03-03', '2025-03-28'),
        IndexURL('MCFTRR', '2003-03-03', '2025-03-28')
    ])
    index_scraper.scrape_pages()

    trade_scraper = TradeScraper()
    trade_scraper.load_content([
        TradeURL('TMOS', '2020-01-01', '2025-01-01'),
        TradeURL('SBMX', '2018-01-01', '2025-01-01'),
        TradeURL('EQMX', '2020-01-01', '2025-01-01')
    ])
    trade_scraper.scrape_pages()


if __name__ == "__main__":
    main()
