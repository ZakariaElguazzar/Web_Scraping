import requests

url = "https://codeavecjonathan.com/scraping/recette/"
response = requests.get(url)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("Page loaded successfully!")
    html= response.text
    # Save the HTML content to a file
    with open("recette.html", "w", encoding=response.apparent_encoding) as file:
        file.write(html)
else:
    print("Failed to load the page. Status code:", response.status_code)
# Note: Facebook may block requests from scripts or bots.
# To scrape Facebook, you may need to use a headless browser like Selenium or Puppeteer.
# Note: Scraping Facebook is against their terms of service.
# If you want to parse the HTML content, you can use BeautifulSoup or any other library.
# Example of using BeautifulSoup to parse the HTML content
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(html, 'html.parser')
# print(soup.prettify())
    # You can now parse the page content using BeautifulSoup or any other library
    # For example:
    # from bs4 import BeautifulSoup
    # soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup.prettify())