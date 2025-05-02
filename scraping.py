import requests
from bs4 import BeautifulSoup

url = "https://codeavecjonathan.com/scraping/recette/"
response = requests.get(url)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("Page loaded successfully!")
    response.encoding = response.apparent_encoding
    html= response.text
    # Save the HTML content to a file
    with open("recette.html", "w", encoding=response.apparent_encoding) as file:
        file.write(html)
        file.close()
    soup=BeautifulSoup(html, 'html5lib')
    # Parse the HTML content
    # Example: Find all <h1> tags
    Title = soup.find('h1')
    Description = soup.find('p', class_="description")
    Ingredients = soup.find('div', class_="ingredients")
    Table_Preparation = soup.find('table', class_="preparation")
    Preparation = Table_Preparation.find_all('td', class_="preparation_etape")
    Numeros = Table_Preparation.find_all('p', class_="numero")
    print(Ingredients)
    # Print the results
    print("Title:")
    for title in Title:
        print(title.text.strip())
    print("\nDescription:")
    for description in Description:
        print(description.text.strip())
    print("\nIngredients:")
    for ingredient in Ingredients.find_all('p'):
        print(ingredient.text.strip())
    print("\nPreparation:")
    for numero,preparation in zip(Numeros,Preparation):
        print(numero.text.strip()+"-"+preparation.text.strip())

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