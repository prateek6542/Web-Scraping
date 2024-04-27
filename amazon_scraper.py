import argparse
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_product_info(url):
    """
    Extracts product information from an Amazon product page.

    Args:
        url (str): The URL of the Amazon product page.

    Returns:
        tuple: A tuple containing product name, ASIN, original price, discounted price, and product rating.
    """
    try:
        # Extract ASIN from the URL
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        asin_index = path_segments.index('dp') + 1 if 'dp' in path_segments else None
        if asin_index:
            asin = path_segments[asin_index]
        else:
            raise ValueError("ASIN not found in URL")

        # Extract Product Name from the URL
        product_name_index = path_segments.index('dp') - 1 if 'dp' in path_segments else None
        if product_name_index:
            product_name = path_segments[product_name_index].replace('-', ' ')
        else:
            raise ValueError("Product name not found in URL")

        # Initialize default values for product details
        original_price = 'Not available'
        discounted_price = 'Not available'
        product_rating = 'Not available'

        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract original price
        price_element = soup.find('span', {'id': 'priceblock_ourprice'})
        if price_element:
            original_price = price_element.get_text().strip()

        # Extract discounted price
        discounted_price_element = soup.find('span', {'class': 'priceBlockDealPriceString'})
        if discounted_price_element:
            discounted_price = discounted_price_element.get_text().strip()

        # Extract product rating
        rating_element = soup.find('span', {'class': 'a-icon-alt'})
        if rating_element:
            product_rating = rating_element.get_text().strip()

    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    except ValueError as e:
        print(f"Error processing URL {url}: {e}")

    return product_name, asin, original_price, discounted_price, product_rating

def main():
    """
    Main function for extracting product information from Amazon product URLs.
    """
    parser = argparse.ArgumentParser(description='Extract product information from Amazon product URLs.')
    parser.add_argument('input_csv', type=str, help='Path to the input CSV file containing Amazon product URLs')
    parser.add_argument('output_csv', type=str, help='Path to the output CSV file where product information will be saved')
    args = parser.parse_args()

    rows = []
    with open(args.input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) 
        for row in reader:
            url = row[0]
            product_name, asin, original_price, discounted_price, product_rating = extract_product_info(url)
            rows.append([url, product_name, asin, original_price, discounted_price, product_rating])

    # Write data to the output CSV file
    with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL', 'Product Name', 'ASIN', 'Original Price', 'Discounted Price', 'Product Rating'])
        writer.writerows(rows)

if __name__ == "__main__":
    main()

