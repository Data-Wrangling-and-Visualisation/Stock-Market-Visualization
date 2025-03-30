from scraper import Scraper, URL


def main():
    scraper = Scraper()
    scraper.load_content([
        URL.construct_from_url(
            ('https://www.moex.com/ru/index/IMOEX/'
             'archive?from=2020-01-15&till=2021-05-29&sort=TRADEDATE&order=desc')
        )
    ])
    scraper.scrape_pages(
        selected_raw_datasets='IMOEX#from=2020-01-15&till=2021-05-29&sort=TRADEDATE&order=desc'
    )


if __name__ == "__main__":
    main()
