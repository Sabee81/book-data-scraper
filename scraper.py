import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
OUTPUT_FILE = "data/books.csv"


def get_page(url):
    """Fetch a webpage safely."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response.raise_for_status()
        return response.text

    except requests.RequestException as error:
        print(f"Error fetching {url}: {error}")
        return None


def scrape_page(url):
    """Extract book information from one page."""
    html = get_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    books = []

    for book in soup.select("article.product_pod"):
        title = book.select_one("h3 a")["title"]
        price = book.select_one(".price_color").text.strip()
        rating = book.select_one(".star-rating")["class"][1]
        availability = book.select_one(".availability").get_text(strip=True)

        relative_url = book.select_one("h3 a")["href"]
        product_url = urljoin(url, relative_url)

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "url": product_url
        })

    return books


def scrape_books():
    """Scrape books from all available pages."""
    all_books = []
    page_number = 1

    while True:
        url = urljoin(
            BASE_URL,
            f"catalogue/page-{page_number}.html"
        )

        print(f"Scraping page {page_number}...")

        html = get_page(url)

        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        page_books = scrape_page(url)

        if not page_books:
            break

        all_books.extend(page_books)

        next_button = soup.select_one("li.next")

        if not next_button:
            break

        page_number += 1
        time.sleep(0.5)

    return all_books


def save_to_csv(books):
    """Save scraped data to CSV."""
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "title",
                "price",
                "rating",
                "availability",
                "url"
            ]
        )

        writer.writeheader()
        writer.writerows(books)


if __name__ == "__main__":
    print("Starting Book Data Scraper...\n")

    books = scrape_books()

    save_to_csv(books)

    print(f"\nScraping completed!")
    print(f"Total books scraped: {len(books)}")
    print(f"Data saved to: {OUTPUT_FILE}")
