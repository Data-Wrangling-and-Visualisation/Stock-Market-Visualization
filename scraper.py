from playwright.sync_api import sync_playwright, Playwright, Page, Locator
from bs4 import BeautifulSoup, Tag
from typing import List, TypedDict, Optional, Any
from storage import Storage, StorageJSON
import time
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


class URL:
    """
    Class for representing URL with query information.

    Attributes:
        BASE_URL (str): domain name of the server and path to the catalogue
        url (str): the url itself
        index_name (str): name of the index
        date_from (Date): start date of the records
        date_till (Date): end date of the records
        sort (str): sorting label
        order (str): sorting order ('asc' or 'desc')
    """

    BASE_URL: str = 'https://www.moex.com/ru/index/'
    url: str
    index_name: str
    date_from: Date
    date_till: Date
    sort: str
    order: str

    def __init__(self,
                 index_name: str,
                 date_from: str,
                 date_till: str,
                 sort: str = 'TRADEDATE',
                 order: str = 'desc'):
        self.index_name = index_name
        self.date_from = Date(date_from)
        self.date_till = Date(date_till)
        self.sort = sort
        self.order = order
        self.url = self.BASE_URL + index_name + '/archive?' + 'from=' + date_from + \
            '&till=' + date_till + '&sort=' + sort + '&order=' + order

    def construct_from_url(url: str):
        """
        Factory to construct a URL object from the url itself.
        """

        self_index_name = url[url.find("index/")+6:url.find("/archive")]
        from_info = url[url.find('from=')+5:]
        self_date_from = from_info[: from_info.find('&')]
        till_info = url[url.find('till=')+5:]
        self_date_till = till_info if till_info.find('&') == -1 else till_info[: till_info.find('&')]
        if url.find('sort=') != -1:
            sort_info = url[url.find('sort=')+5:]
            self_sort = sort_info if sort_info.find('&') == -1 else sort_info[: sort_info.find('&')]
        else:
            self_sort = 'TRADEDATE'
        if url.find('order=') != -1:
            order_info = url[url.find('order=')+6:]
            self_order = order_info
        else:
            self_order = 'desc'
        return URL(self_index_name, self_date_from, self_date_till, self_sort, self_order)


class IndexRecord(TypedDict):
    """
    Class representing a single record of an index
    """

    date: Optional[str]
    price_at_opening: Optional[str]
    max_price: Optional[str]
    min_price: Optional[str]
    price_at_closure: Optional[str]
    volume_of_trade: Optional[str]
    capitalization: Optional[str]


class Scraper:
    """
    Class to load pages, extract tables, and scrape information about indices.

    Attributes:
        pages_path (str): relative path to the directory with saved pages (*.html)
        storage (Storage): storage strategy for saving data on disk
        credentials (Any): credentials for accessing specified storage
        columns (List[str]): list of columns (see IndexRecord)
    """

    pages_path: str
    storage: Storage
    credentials: Any
    columns: List[str] = [
        'date',
        'price_at_opening',
        'max_price',
        'min_price',
        'price_at_closure',
        'volume_of_trade',
        'capitalization'
    ]

    def __init__(self,
                 pages_path: str = 'pages/',
                 storage: Storage = StorageJSON(),
                 credentials: Any = 'data/'):
        self.pages_path = pages_path
        self.storage = storage
        self.credentials = credentials

    def _select_date(self, page: Page, btn: Locator, date: Date):
        """
        Selects the date in the window created by clicking the `btn` button.

        Arguments:
            page (Page): Playwright page
            btn (Locator): button locator that needs
                to be clicked to obtain the calendar
            date (Date): date to be selected
        """

        btn.click()
        calendar = page.locator('[id="ui-datepicker-div"]')
        calendar.locator('[class="ui-datepicker-year"]').select_option(date.year)
        calendar.locator('[class="ui-datepicker-month"]').select_option(str(int(date.month)-1))
        calendar.locator('//table/tbody').get_by_text(date.day).click()

    def _lookup(self, playwright: Playwright, url: URL) -> str:
        """
        Loads a dataset webpage, signs in, navigates and extracts raw content.

        Arguments:
            playwright (Playwright): object to load a webpage
            url (URL): URL object of a datset webpage

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
        btn_keyword = 'Согласен'
        page.get_by_text(btn_keyword, exact=True).click()

        # Select intervals
        from_btn, till_btn = page.locator('[type="text"]').all()
        self._select_date(page, from_btn, url.date_from)
        self._select_date(page, till_btn, url.date_till)

        page.locator('button[aria-label="Показать"]').click()
        page.locator('button[title="Первая страница"]').click()
        time.sleep(1)

        # Navigate through pages
        htmls = []

        while True:
            htmls.append(page.content())
            page.wait_for_selector('button[title="Первая страница"]')
            next_btn = page.locator('button[title="Следующая страница"]')
            if not next_btn.is_visible():
                break
            next_btn.click()

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
        # columns = [header.text.strip() for header in soup_table.find('thead').find_all('th')]
        data: List[IndexRecord] = []
        for soup_table in soup_tables:
            columns = self.columns
            assert len(columns) == 7

            assert soup_table.find('tbody') is not None
            tbody = soup_table.find('tbody')
            assert tbody.find('tr') is not None

            for row in tbody.find_all('tr'):
                elements = row.find_all('td')
                assert len(elements) == 7
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

        date_column, *float_columns = df.columns
        df[date_column] = df[date_column].apply(pd.to_datetime, format='mixed')
        df[float_columns] = df[float_columns].apply(
            lambda cols: list(map(lambda x: float(x.replace(' ', '').replace(',', '.')), cols))
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
                filename = (f'{url.index_name}#from={url.date_from.__str__()}&till={url.date_till.__str__()}'
                            f'&sort={url.sort}&order={url.order}')
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
            if selected_raw_datasets is None or content_name in selected_raw_datasets:
                content_tables = self._scrape_page(self.pages_path + filename)
                page_df = self._convert_to_df(content_tables)
                formated_df = self._parse_df(page_df)

                conn = self.storage.connect(self.credentials)
                self.storage.write(conn, formated_df, content_name)
                self.storage.close(conn)

    def load_page_data(self, dataset_name: str) -> pd.DataFrame:
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
