from playwright.sync_api import Playwright, Page, Locator
from bs4 import Tag
from typing import List, TypedDict, Optional, Any
from storage import Storage, StorageJSON
import time
import pandas as pd
from trade_scraper import Date, URL, TradeScraper


class IndexURL(URL):
    """
    Specific class for index information urls.

    Attributes:
        BASE_URL (str): domain name of the server and path to the catalogue
        url (str): the url itself
        index_name (str): name of the index
        date_from (Date): start date of the records
        date_till (Date): end date of the records
        sort (str): sorting label
        order (str): sorting order ('asc' or 'desc')
    """

    index_name: str
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


class IndexScraper(TradeScraper):
    """
    Class to load pages, extract tables, and scrape information about indices.

    Attributes:
        columns (List[str]): list of columns (see IndexRecord)
    """

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
        super().__init__(pages_path, storage, credentials)
        self.prefix_name = 'INDEX'

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
