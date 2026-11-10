import requests
import bs4

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

response = requests.get('https://biggeek.ru/catalog/noutbuki-apple', headers=headers)

# print(response.text)

bs = bs4.BeautifulSoup(response.text, 'html.parser')

all_cards = bs.find_all('div', class_='catalog-card')

for card in all_cards:
    name_tag = card.find('a', class_='catalog-card__title').text
    price_tag = card.find('b', class_='cart-modal-count').text
    print(f'{name_tag.strip()} - {price_tag.strip()}')
