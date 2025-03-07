# Global Firepower Scraper

This script is designed to scrape military strength details from the Global Firepower website using `aiohttp` and `BeautifulSoup`. It performs a search based on a given country ID, extracts relevant information from the search results, and organizes the data into a structured format.

## Requirements

- Python 3.6+
- aiohttp
- asyncio
- BeautifulSoup4

## Installation

1. Clone the repository or download the `globalfirepower-scraper.py` file.

2. Install the required Python packages using pip:

    ```bash
    pip install aiohttp asyncio beautifulsoup4
    ```

## Usage

1. Ensure that you have Python installed on your system.

2. Run the [globalfirepower-scraper.py](http://_vscodecontentref_/1) script:

    ```bash
    python globalfirepower-scraper.py
    ```

3. The script will perform a search on the Global Firepower website based on the country ID provided in the [search](http://_vscodecontentref_/2) method and print the extracted results.

## Note

You can find a list of available country IDs in the [country_ids.txt](http://_vscodecontentref_/1) file
