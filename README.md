# Stock Market Visualization

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
Clone the repository:
```bash
git clone https://github.com/Data-Wrangling-and-Visualisation/Stock-Market-Visualization
```

<a name="scraper"> <h2> Scraper client example </h2> </a>
Below you can see the code for the client to start scraping process:
```Python
import scraper
    
scr = scraper.Scraper()
my_url = scraper.URL.construct_from_url(
  url=("https://www.moex.com/ru/index/IMOEX/archive"
       "?from=2025-01-26&till=2025-02-26&sort=TRADEDATE&order=desc")
)
scr.load_content([my_url])  # load page with driver
scr.scrape_pages()  # scrape html files in the page/ folder

df = scr.load_page_data('page') # load data from example page
print(df.head())
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
- [ ] Develop web application with basic display functionality of the visualizations (statically displayed plots) and data supply through API.
- [ ] Add styles and variety for visualizations (e.g. various indexes for heatmap instead of a single one).
- [ ] Test application, fix bugs, and prepare presentation.

<a name="contributors"> <h2> Contributors </h2> </a>
The team consists of three members:
- Ilya Grigorev, DS-01 student, responsible for scraping and parsing data;
- Ruslan Gatiatullin, DS-02 student, responsible for EDA;
- Salavat Faizullin, DS-01 student, responsible developing visualizations.
