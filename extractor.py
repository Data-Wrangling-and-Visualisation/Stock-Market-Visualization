from bs4 import BeautifulSoup
import json
import os

def extract_json_from_html(pages_dir: str):
    i = 1
    all_rows = []
    while os.path.isfile(f'{pages_dir}/page_{i}.html'):
        # Read HTML file
        with open(f'{pages_dir}/page_{i}.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all table rows (tr tags)
        rows = soup.find_all('tr')

        # Extract data from rows
        table_data = []
        for row in rows:
            # Get all cells (td/th) in the row
            cells = row.find_all(['td', 'th'])
            # Extract text from each cell and clean whitespace
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:  # Skip empty rows
                table_data.append(row_data)

        data = table_data[2:22]

        data = [[y.replace('\xa0', '').replace(',', '.') for y in x] for x in data]

        for row in data:
            try:
                all_rows += [{
                    'date': row[0],
                    'instrument_code': row[1],
                    'sales': float(row[2]),
                    'volume_of_trade': float(row[3]),
                    'mean_price': float(row[4]),
                    'price_at_opening': float(row[5]),
                    'min_price': float(row[6]),
                    'max_price': float(row[7]),
                    'price_at_closure': float(row[8])
                }]
            except:
                break
        i += 1

    with open('output.json', 'w') as f:
        json.dump(all_rows, f)
