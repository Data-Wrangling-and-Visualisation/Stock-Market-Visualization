# Stock Market Visualization

## Deployed

http://5.129.199.157:8080/

## Table of Contents
<ol>
<li> <a href="#description">Project Description</a> </li>
<li> <a href="#dataset">Dataset Description</a> </li>
<li> <a href="#milestones">Project Milestones</a> </li>
<li> <a href="#installation">Installation</a> </li>
<li> <a href="#scraper">Scraper Client</a> </li>
<li> <a href="#eda">EDA</a> </li>
<li> <a href="#visualization">Visualization</a> </li>
<li> <a href="#roadmap">Checkpoint Information and Roadmap</a> </li>
<li> <a href="#contributors">Contributors</a> </li>
</ol>

<a name="description"> <h2> Project Description </h2> </a>
<p>
This project is inspired by the illustrative visualization of the historical American stock market returns by <a href="https://archive.nytimes.com/www.nytimes.com/interactive/2011/01/02/business/20110102-metrics-graphic.html">E. Easterling</a>. We seek to expand that knowledge to the Russian stock market by providing similar visualization as well as by adding other supporting graphs. The aim of this work is to provide investors (with any capital) an estimate for their potential profit and risk in the Russian stock market. Our target audience are primarily Russian citizens who are interested in investing and want to choose a desired share of stocks in their portfolio.
</p>

<a name="dataset"> <h2> Dataset Description </h2> </a>
<p>
Web data will be scraped from the archive of the Moscow Exchange (MOEX) web site. The pages of the site consists of tables, so document structure knowledge is used by scraper to extract relevant information.
</p>
<p>
The MOEX web site provides exhaustive information about the price of MOEX indexes by days and months recorded from 1997. Particularly, the tables consist of the following columns: the date of a record (dd.mm.yyyy), the values of an index at the beginning of the period and at the end of the period (floating-point numbers), the maximum and minimum recorded values of an index during the period (floating-point numbers), the money volume of an index during the period (floating-point number), and the money capitalization of index during the period (floating-point number).

Individual stocks and ETF's on the other hand contain slightly different columns. Those are: date of a record (dd.mm.yyyy), instrument name (string), number of trades on a given day (int), weighted average price (floating-point number), the values of stock at the beginning of the period and at the end of the period (floating-point numbers), the maximum and minimum recorded values of an index during the period (floating-point numbers), the money volume of an index during the period (floating-point number).
</p>

<a name="milestones"> <h2> Project Milestones </h2> </a>
<ol>
<li>Data Scraping. Scraper is developed to parse data from MOEX to JSON format / save into DB. </li>
<li>Data Cleaning and Preprocessing. Pandas will be used for data cleaning and preprocessing. </li>
<li>Data Exploration and Processing. Pandas and Matplotlib will be used for Exploratory Data. Analysis (EDA). Potentially we will add different visualizations to our project if some interesting insights are found during that step. </li>
<li>Data Delivery. A Flask RESTful API will provide smooth communication between the data processing and the website application. </li>
<li> Data Visualization. Mainly D3.js library will be used for visualization of our data. </li>
</ol>

<a name="installation"> <h2> Installation </h2> </a>
<h3> Manual </h3>
Clone the repository:

```bash
git clone https://github.com/Data-Wrangling-and-Visualisation/Stock-Market-Visualization
```

Create and setup a local python environment (example on Windows):
```bash
python -m venv venv
./venv/Scripts/activate
```

Install the necessary requirements
```bash
pip install -r src/req.txt
playwright install
```

<a name="scraper"> <h2> Scraper client example </h2> </a>
Below you can see the code for the client to start scraping process:
```Python
from storage import StorageSQLite
from trade_scraper import TradeScraper, TradeURL
from index_scraper import IndexScraper, IndexURL

store = StorageSQLite()
indexScrap = IndexScraper(storage=store)
tradeScrap = TradeScraper(storage=store)

tickersIndexes = [
    'https://www.moex.com/ru/index/IMOEX/archive?from=2023-12-01&till=2025-03-27&sort=TRADEDATE&order=desc'
]
tickersETFs = [
    'https://www.moex.com/ru/marketdata/#/mode=instrument&secid=TMOS&boardgroupid=57&mode_type=history&date_from=2024-08-26&date_till=2025-03-28'
    ]
indexUrls = [IndexURL.construct_from_url(x) for x in tickersIndexes]
indexScrap.load_content(indexUrls)
indexScrap.scrape_pages()


tradeUrls = [TradeURL.construct_from_url(x) for x in tickersETFs]
tradeScrap.load_content(tradeUrls)
tradeScrap.scrape_pages()
```
Scraped data will be added to local moex.db data base via SQLite and will be accessible by backend.

Start backend server:
```bash
python src/backend.py
```

Access the <a href="http://127.0.0.1:8080/">127.0.0.1:8080/</a> for the index webpage.

<h3> With Docker </h3>
Run the following command to create a container:

```bash
docker compose up -d
```

Access the <a href="http://127.0.0.1:8080/">127.0.0.1:8080/</a> for the index webpage.

Run the following command to stop and remove the container:
```bash
docker compose down
```

<a name="eda"> <h2> EDA </h2> </a>
The <a href="https://github.com/Data-Wrangling-and-Visualisation/Stock-Market-Visualization/blob/EDA/Russia_Stock_Market_Index.ipynb">notebook </a> provides a brief review of the related dataset information that can be further used to select data and visualizations.

<a name="visualization"> <h2> Visualization </h2> </a>
Proceed to the <a href="https://data-wrangling-and-visualisation.github.io/Stock-Market-Visualization/"> website </a> to see the visualizations that are implemented so far. If you want to get the source code, you can go to the <a href="https://github.com/Data-Wrangling-and-Visualisation/Stock-Market-Visualization/tree/frontend"> frontend </a> branch.

<a name="roadmap"> <h2> Checkpoint Information and Roadmap </h2> </a>
The project checkpoint information can be found <a href="https://github.com/Data-Wrangling-and-Visualisation/Stock-Market-Visualization/blob/Checkpoints/DWV_Checkpoint.pdf">here </a>

- [x] Select web pages and analyze data format for further extraction.
- [x] Develop a data extraction pipeline by configuring the scraping tools.
- [x] Integrate data preparation and cleaning parts to the existing pipeline: select necessary data for the project, clean and format extracted information.
- [x] Setup the exploration tools and determine data worth visualizing based on the analysis.
- [x] Establish interface for transferring data from the processing pipeline to visualization application and integrate it into a Flask RESTful API.
- [x] Develop web application with basic display functionality of the visualizations (statically displayed plots) and data supply through API.
- [ ] Add styles and variety for visualizations (e.g. various indexes for heatmap instead of a single one).
- [ ] Test application, fix bugs, and prepare presentation.

<a name="contributors"> <h2> Contributors </h2> </a>
The team consists of three members:
- Ilya Grigorev, DS-01 student, responsible for scraping and parsing data;
- Ruslan Gatiatullin, DS-02 student, responsible for EDA;
- Salavat Faizullin, DS-01 student, responsible developing visualizations.
