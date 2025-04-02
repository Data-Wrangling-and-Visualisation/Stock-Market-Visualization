from extractor import extract_json_from_html
from parser import load_all_pages_from_url

url = 'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=TMOS&boardgroupid=57&mode_type=history&date_from=2024-08-26&date_till=2025-03-28'
load_all_pages_from_url(url, './pages')
extract_json_from_html('./pages')