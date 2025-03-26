<div align="center">
<h3 align="center">MLH Top Hackers Scraper</h3>

  <p align="center">
    Scrapes profile data from the MLH Top Hackers website for a given year.
  </p>
</div>

## About The Project

This project is a Python script that scrapes data from the MLH (Major League Hacking) Top Hackers website. It extracts information such as name, age, links to profiles (Devpost, GitHub, LinkedIn, personal website), and "about" sections from the hacker profiles for a specified year. The scraped data is then saved into both JSON and CSV files.

## Tech

The project consists of a single Python script, `scrape.py`, which uses the following libraries:

- **requests:** For making HTTP requests to the MLH Top Hackers website.
- **BeautifulSoup4:** For parsing the HTML content of the pages.
- **json:** For saving the scraped data in JSON format.
- **re:** For using regular expressions to extract data from the HTML.
- **time:** For adding delays between requests to avoid overloading the server.
- **pathlib:** For creating directories and saving files.
- **csv:** For saving the scraped data in CSV format.

## Getting Started

1. Install the required Python packages:
   ```sh
   pip install requests beautifulsoup4
   ```
2. Run the script:
   ```sh
   python scrape.py
   ```
   **Note:** The script is currently configured to scrape data for the year 2020. To change the year, modify the `year` variable at the beginning of the `scrape.py` file.

## Acknowledgments

- This README was created using [gitreadme.dev](https://gitreadme.dev) — an AI tool that looks at your entire codebase to instantly generate high-quality README files.
