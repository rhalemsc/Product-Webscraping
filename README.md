# Product-Webscraping
Examples of webscrapers that I have built to scrape product data
<br>
## [Miele-Scraper.py](https://github.com/rhalemsc/Product-Webscraping/blob/main/Miele-Scraper.py)
This project shows how I've utilized Python to scrape product data from an appliance manufacturer. In this project, we were intersted in capturing images, product specs, spec sheets, and other available product data.

## [Leads_NLP.ipynb](https://github.com/rhalemsc/Product-Webscraping/blob/main/Leads_NLP.ipynb)
In this project, I was tasked with searching the websites of potential leads for certain keywords. The presence of many of these keywords on a website would indicate that the company was a good lead.<br><br>
In order to achieve this, I first scraped all of the websites in question and stored the data in our data warehouse.<br><br>
Then I wrote a script in python that searched for these keywords on each site and analyze how many keywords were featured on each company website. This was used as a ranking tool to prioritize these leads.
