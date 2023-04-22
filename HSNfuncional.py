import asyncio
import json
from pyppeteer import launch
import psutil
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# OS
from dotenv import load_dotenv
import os
import requests
# Carga las variables de entorno del archivo .env en el entorno de Python
load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def telegramMSG(str):
    data = {
                'chat_id': CHAT_ID,
                'text': f'{str}',
                'parse_mode': 'Markdown'
            }
    
    r = requests.post(TELEGRAM_API_SEND_MSG, data=data)

sitemap = {
    "startUrl": [
        "https://www.hsnstore.com/marcas/sport-series/evowhey-protein-2-0-2kg-chocolate",
        "https://www.hsnstore.com/marcas/sport-series/evocasein-2-0-caseina-micelar-digezyme-2kg-chocolate",
        "https://www.hsnstore.com/marcas/food-series/harina-de-avena-instantanea-2-0-3kg-chocolate"
    ],
    "selectors": [
        {
            "id": "product-price-16688",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "div#product-price-16688",
            "type": "SelectorText"
        },
        {
            "id": "product-price-17737",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "div#product-price-17737",
            "type": "SelectorText"
        },
        {
            "id": "product-price-18856",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "div#product-price-18856",
            "type": "SelectorText"
        },
        {
            "id": "name",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "h1",
            "type": "SelectorText"
        }
    ],
    "_id": "hsnstore"
}

async def get_data(url):
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 120000})
    await asyncio.sleep(5) # Aumentar tiempo de espera a 5 segundos
    data = {}
    for selector in sitemap["selectors"]:
        element = await page.querySelector(selector["selector"])
        text = await page.evaluate('(element) => element.textContent', element) if element else None
        if text:
            data[selector["id"]] = text
    data["url"] = url
    await browser.close()
    return data

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(asyncio.gather(*[get_data(url) for url in sitemap["startUrl"]]))

    for d in data:
        name = d.get('name')
        price = d.get('product-price-16688') or d.get('product-price-17737') or d.get('product-price-18856')
        url = d.get('url')
        if name and price and url:
            message = (f"*HSN |* [{name}]({url}) * | {price}*")
            print(message)
            telegramMSG(message)

# Imprimir uso de recursos
process = psutil.Process()
memory_info = process.memory_info()
print(f"\nUso de memoria: {memory_info.rss / 1024 / 1024:.2f} MB")
print(f"Uso de CPU: {psutil.cpu_percent()}%")