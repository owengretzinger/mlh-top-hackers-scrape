import requests
from bs4 import BeautifulSoup
import json
import re
import time
from pathlib import Path
import csv

# year = "2023"
# year = "2022"
# year = "2021"
year = "2020"


class MLHTopHackersScraper:
    def __init__(self):
        self.base_url = f"https://top.mlh.io/{year}"
        self.profiles_url = f"{self.base_url}/profiles"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.hackers = []

    def get_profile_links(self):
        """Get all hacker profile links from the main page"""
        print("Getting profile links...")

        response = requests.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all profile links
        profile_links = []

        # Looking for all elements that match the pattern of hacker entries on the main page
        # Based on the provided example, these seem to be elements with names and ages
        hacker_elements = soup.find_all(
            lambda tag: tag.name
            and tag.text
            and re.search(r"[A-Za-z\s]+,\s+\d+", tag.text)
        )

        for element in hacker_elements:
            # Find the nearest parent that's a link
            parent_link = element.find_parent("a")
            if parent_link and "href" in parent_link.attrs:
                href = parent_link["href"]
                if href.startswith(f"/{year}/profiles/"):
                    # Make sure we have the full URL
                    if href.startswith("/"):
                        full_url = f"https://top.mlh.io{href}"
                    else:
                        full_url = f"{self.profiles_url}/{href}"
                    profile_links.append(full_url)

        # Make sure we have unique links
        profile_links = list(set(profile_links))
        print(f"Found {len(profile_links)} profile links")
        return profile_links

    def extract_profile_data(self, profile_url):
        """Extract data from a hacker's profile page"""
        print(f"Scraping {profile_url}")

        response = requests.get(profile_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Initialize data dictionary
        data = {
            "name": "",
            "age": "",
            "devpost": "",
            "github": "",
            "linkedin": "",
            "website": "",
            "about": "",
        }

        # Extract name and age from title (h1 tag)
        title_element = soup.find("h1")
        if title_element:
            title_text = title_element.text.strip()
            match = re.search(r"(.*?),\s*(\d+)", title_text)
            if match:
                data["name"] = match.group(1).strip()
                data["age"] = match.group(2).strip()

        # Extract links from the Links section
        # First, look for the h4 "Links" heading
        links_heading = soup.find("h4", string=lambda text: text and "Links" in text)
        if links_heading:
            # Get the div that contains the links section
            links_container = links_heading.find_parent("div")
            if links_container:
                # Find all link elements in this container
                for div in links_container.find_all("div", class_="mb-1"):
                    text = div.text.strip()
                    link = div.find("a")
                    link_text = link.text.strip() if link else ""

                    if "Devpost:" in text:
                        data["devpost"] = link_text
                    elif "GitHub:" in text:
                        data["github"] = link_text
                    elif "LinkedIn:" in text:
                        data["linkedin"] = link_text
                    elif "Website:" in text:
                        data["website"] = link_text

        # Extract the about section - main profile text
        # This is based on the observed HTML structure where paragraphs are in a div with class="mt-4"
        about_paragraphs = []

        # Try to find the main content div
        main_content_div = None

        # First try looking for a div containing the about paragraphs (class="mt-4" or similar)
        for div in soup.find_all(
            "div", class_=lambda c: c and ("mt-4" in c or "w-md-60" in c)
        ):
            if div.find("p"):
                main_content_div = div
                break

        # If we found the main content div, extract paragraphs from it
        if main_content_div:
            for p in main_content_div.find_all("p"):
                text = p.text.strip()
                if text:
                    about_paragraphs.append(text)
        else:
            # Fallback: Just look for paragraphs that aren't in the Quick Facts or Links sections
            for p in soup.find_all("p"):
                # Skip paragraphs in divs that have Quick Facts or Links headings
                if any(
                    h4.text.strip() in ["Quick Facts", "Links"]
                    for h4 in p.find_parents("div")[0].find_all("h4", recursive=True)
                    if p.find_parents("div")
                ):
                    continue

                # Skip paragraphs that contain names of other hackers
                text = p.text.strip()
                if text and not re.search(r"[A-Za-z\s]+,\s+\d+", text):
                    about_paragraphs.append(text)

        # Join all paragraphs with double newlines to preserve format
        if about_paragraphs:
            data["about"] = "\n\n".join(about_paragraphs)

        # Add the URL to the data
        data["url"] = profile_url

        print(f"Extracted data for {data['name']}")
        return data

    def scrape_all_hackers(self):
        """Scrape data for all hackers"""
        profile_links = self.get_profile_links()

        for profile_url in profile_links:
            try:
                hacker_data = self.extract_profile_data(profile_url)
                self.hackers.append(hacker_data)
                # Be nice to the server
                time.sleep(1)
            except Exception as e:
                print(f"Error scraping {profile_url}: {e}")

        return self.hackers

    def save_to_json(
        self, filename=f"extracted_data/{year}/mlh_top_hackers_{year}.json"
    ):
        """Save scraped data to a JSON file"""
        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        Path(filename).write_text(json.dumps(self.hackers, indent=2), encoding="utf-8")
        print(f"Saved data to {filename}")

    def save_to_csv(self, filename=f"extracted_data/{year}/mlh_top_hackers_{year}.csv"):
        """Save scraped data to a CSV file"""
        if not self.hackers:
            print("No data to save")
            return

        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        fields = self.hackers[0].keys()

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(self.hackers)

        print(f"Saved data to {filename}")

    def run(self):
        """Run the full scraping process"""
        self.scrape_all_hackers()
        self.save_to_json()
        self.save_to_csv()
        print(f"Scraped {len(self.hackers)} hacker profiles successfully!")


if __name__ == "__main__":
    scraper = MLHTopHackersScraper()
    scraper.run()
