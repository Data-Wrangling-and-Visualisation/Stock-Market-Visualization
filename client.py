from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL
from storage import StorageSQLite

def main():
    store = StorageSQLite()
    # scraper = TradeScraper(storage=store, credentials={})
    # scraper.load_content([
    #     TradeURL('IRDIVTR', '2024-01-01', '2024-01-31'),
    #     TradeURL('EQMX', '2024-01-01', '2025-04-01')
    # ])
    # scraper.scrape_pages()
    # df = scraper.load_dataset('IRDIVTR')
    # print(df.info())
    
    scraperInd = IndexScraper(storage=store, credentials={})
    df2 = scraperInd.load_dataset('TMOS')
    print(df2)

if __name__ == "__main__":
    main()
