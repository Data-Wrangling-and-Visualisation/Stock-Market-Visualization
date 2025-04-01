from playwright.sync_api import sync_playwright, Playwright, TimeoutError
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from storage import Storage, StorageJSON
import pandas as pd
import os
import datetime


class Date:
    """
    Class for specifying the type for a date.

    Attributes:
        day (str): day number (1..31)
        month (str): month number (1..12)
        year (str): year number (positive integer)
    """

    day: str
    month: str
    year: str

    def __init__(self, date: str):
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            raise ValueError('Incorrect data format, should be YYYY-MM-DD')
        self.year, self.month, self.day = date.split('-')

    def __str__(self) -> str:
        return self.year + '-' + self.month + '-' + self.day

    def __lt__(self, rhs) -> bool:
        return datetime.datetime(
            int(self.year),
            int(self.month),
            int(self.day)
        ) < datetime.datetime(
            int(rhs.year),
            int(rhs.month),
            int(rhs.day)
        )


class URL(ABC):
    """
    Class for representing URL with query information.
    """
    BASE_URL: str
    url: str
    date_from: Date
    date_till: Date

    @staticmethod
    @abstractmethod
    def construct_from_url(url: str):
        """
        Factory to construct a URL object from the url itself.
        """
        pass


class TradeURL(URL):
    """
    Specific class for trade section urls.

    Attributes:
        BASE_URL (str): domain name of the server and path to the catalogue
        url (str): the url itself
        index_name (str): name of the index
        mode_type (str): mode of listings
        date_from (Date): start date of the records
        date_till (Date): end date of the records
    """

    index_name: str
    mode_type: str

    def __init__(self,
                 index_name: str,
                 date_from: str,
                 date_till: str,
                 mode_type: str = 'history'):
        self.BASE_URL = 'https://www.moex.com/ru/marketdata/#/mode=instrument'
        self.index_name = index_name
        self.date_from = Date(date_from)
        self.date_till = Date(date_till)
        self.mode_type = mode_type
        self.url = self.BASE_URL + '&secid=' + index_name + '&mode_type=' + mode_type + '&date_from=' + date_from + \
            '&date_till=' + date_till

    @staticmethod
    def construct_from_url(url: str):
        self_index_name = url[url.find("&secid=")+7:url.find("&boardgroupid")]
        self_mode_type = url[url.find("&mode_type=")+11:url.find("&date_from")]
        from_info = url[url.find('&date_from=')+11:]
        self_date_from = from_info[: from_info.find('&')]
        till_info = url[url.find('&date_till=')+11:]
        self_date_till = till_info if till_info.find('&') == -1 else till_info[: till_info.find('&')]
        return URL(self_index_name, self_date_from, self_date_till, self_mode_type)


class TradeScraper:
    """
    Class to load pages, extract tables, and scrape information about trading.

    Attributes:
        pages_path (str): relative path to the directory with saved pages (*.html)
        storage (Storage): storage strategy for saving data on disk
        credentials (Any): credentials for accessing specified storage
        prefix_name (str): name prefix for export files
    """

    pages_path: str
    storage: Storage
    credentials: Any
    prefix_name: str = 'TRADE_INDEX'

    def __init__(self,
                 pages_path: str = 'pages/',
                 storage: Storage = StorageJSON(),
                 credentials: Any = 'data/'):
        self.pages_path = pages_path
        self.storage = storage
        self.credentials = credentials

    def _lookup(self, playwright: Playwright, url: URL) -> str:
        """
        Loads a dataset webpage, signs in, navigates and extracts raw content.

        Arguments:
            playwright (Playwright): object to load a webpage
            url (URL): URL object of a dataset webpage

        Returns:
            List[str]: list of html content of webpages
        """

        # Setup client
        webkit = playwright.webkit
        browser = webkit.launch()
        context = browser.new_context()
        page = context.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0'})
        page.goto(url.url)

        # Pass the welcome page
        try:
            btn_keyword = 'Согласен'
            page.get_by_text(btn_keyword, exact=True).click()
        except TimeoutError:
            raise ValueError("Expected an agreement page. Check the url correctness")

        # Select intervals
        try:
            submit_btn = page.locator('[type="submit"]')
            submit_btn.click()
        except TimeoutError:
            raise ValueError("Failed to load the start page. Check the url correctness")

        htmls = []

        # Reload content by date ordering
        try:
            page.wait_for_selector('//div[@class="ui-table__container"]/table/tbody')
        except TimeoutError:
            raise ValueError("Failed to fetch data. Check parameter correctness")
        order_btn_text = 'Дата торгов'
        order_btn = page.get_by_title(order_btn_text)
        order_btn.click()

        # Save the first date
        page.wait_for_selector('//div[@class="ui-table__container"]/table/tbody')
        date_element = page.locator(('//div[@class="ui-table__container"]/table/tbody'
                                    '/tr[position()=1]/td[position()=1]'))
        date1 = Date(date_element.inner_html())
        order_btn_text = 'Дата торгов'
        order_btn = page.get_by_title(order_btn_text)
        order_btn.click()

        # Save the second date
        page.wait_for_selector('//div[@class="ui-table__container"]/table/tbody')
        date_element = page.locator(('//div[@class="ui-table__container"]/table/tbody'
                                    '/tr[position()=1]/td[position()=1]'))
        date2 = Date(date_element.inner_html())

        # Set descending order of dates
        if (date2 < date1):
            order_btn_text = 'Дата торгов'
            order_btn = page.get_by_title(order_btn_text)
            order_btn.click()

        current_top_date = date1.__str__() if date2 < date1 else date1.__str__()

        htmls.append(page.content())

        # Navigate through pages
        while True:
            next_btn = page.locator('button[title="Следующая страница"]')
            if not next_btn.is_visible():
                break
            next_btn.click()
            page.wait_for_selector('//div[@class="ui-table__container"]/table/tbody')

            # Wait for content to be updated
            while True:
                date_element = page.locator(('//div[@class="ui-table__container"]/table/tbody/'
                                             'tr[position()=1]/td[position()=1]'))
                date = date_element.inner_html()
                if date != current_top_date:
                    current_top_date = date
                    break
            htmls.append(page.content())

        browser.close()

        return htmls

    def _convert_to_df(self, soup_tables: List[Tag]) -> pd.DataFrame:
        """
        Converts tables into a pandas dataframe with string values

        Arguments:
            soup_tables (List[Tag]): list of tables in the html format

        Returns:
            pd.Dataframe: dataframe with retrieved information
        """
        columns = [header.text.strip() for header in soup_tables[0].find('thead').find_all('th')]
        data: List[Dict] = []
        for soup_table in soup_tables:

            assert soup_table.find('tbody') is not None
            tbody = soup_table.find('tbody')
            assert tbody.find('tr') is not None

            for row in tbody.find_all('tr'):
                elements = row.find_all('td')
                data.append([element.text.strip() for element in elements])

        return pd.DataFrame(data, columns=columns)

    def _parse_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Data type conversion of the dataframe.

        Arguments:
            df (pd.DataFrame): dataframe object with the specific columns

        Returns:
            pd.DataFrame: formatted dataframe
        """
        df = df.apply(
            lambda cols: list(map(lambda x: x.replace('\xa0', ''), cols))
        )

        return df

    def _scrape_page(self, filename: str) -> Tag:
        """
        Loads raw dataset content and scrapes tabular information from it.

        Arguments:
            filename (str): name of the saved dataset raw content.

        Returns:
            List[Tag]: list of table tags in the content.
        """

        with open(filename, 'r', encoding='UTF-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        tables = [elem.find('table') for elem in soup.find_all('div', {'class': 'ui-table__container'})]
        assert len(tables) != 0
        return tables

    def load_content(self, urls: List[URL]) -> None:
        """
        Loads content from the specified dataset urls into files on disk.

        Arguments:
            urls (List[URL]): list of URL objects representing dataset website
        """

        with sync_playwright() as playwright:
            for url in urls:
                htmls = self._lookup(playwright, url)
                filename = (f'{self.prefix_name}={url.index_name}&from={url.date_from.__str__()}'
                            f'&till={url.date_till.__str__()}.html')
                for html in htmls:
                    with open(self.pages_path + filename, 'a', encoding='UTF-8') as f:
                        f.write(html)

    def scrape_pages(self, selected_raw_datasets: List[str] = None) -> None:
        """
        Loads selected dataset raw content files from disk, scrapes information to form dataframes,
        and saves dataframes in the storage.

        Arguments:
            selected_raw_datasets (List[str]): list of names of saved contents to parse
        """

        for filename in os.listdir(self.pages_path):
            content_name = filename.split('.')[0]
            if not content_name.startswith(self.prefix_name):
                continue
            if selected_raw_datasets is None or content_name in selected_raw_datasets:
                content_tables = self._scrape_page(self.pages_path + filename)
                page_df = self._convert_to_df(content_tables)
                formatted_df = self._parse_df(page_df)

                conn = self.storage.connect(self.credentials)
                self.storage.write(conn, formatted_df, content_name)
                self.storage.close(conn)

    def load_dataset(self, dataset_name: str) -> pd.DataFrame:
        """
        Loads scraped dataset formatted content from the storage.

        Arguments:
            dataset_name (str): name of the dataset.

        Returns:
            pd.DataFrame: dataframe with the formatted dataset contents.
        """
        conn = self.storage.connect(self.credentials)
        df = self.storage.read(conn, dataset_name)
        self.storage.close(conn)
        return df
