from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL
from storage import StorageSQLite


def main():
    store = StorageSQLite()
    scraper = IndexScraper(storage=store, credentials={})
    scraper.load_content([
        IndexURL('IMOEX', '2005-01-01', '2025-01-01'),
        IndexURL('IMOEX2', '2020-06-22', '2025-01-01'),
        IndexURL('RTSI', '2005-01-01', '2025-01-01'),
        IndexURL('IMOEXCNY', '2023-01-01', '2025-01-01')
    ])
    scraper.scrape_pages()


if __name__ == "__main__":
    main()
