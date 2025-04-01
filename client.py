from trade_scraper import TradeScraper, TradeURL


def main():
    scraper = TradeScraper()
    scraper.load_content([
        TradeURL('IRDIVTR', '2024-01-01', '2024-01-31'),
        TradeURL('EQMX', '2024-01-01', '2025-04-01')
    ])
    scraper.scrape_pages()
    df = scraper.load_dataset('TRADE_INDEX=IRDIVTR&from=2024-01-01&till=2024-01-31')
    print(df.info())


if __name__ == "__main__":
    main()
