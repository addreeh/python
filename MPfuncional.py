import asyncio
import json
import psutil
from pyppeteer import launch
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
    "startUrl": ["https://www.myprotein.es/my.basket"],
    "selectors": [
        {
            "id": "product-name-1",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": ".athenaBasket_itemName",
            "type": "SelectorText"
        },
        {
            "id": "product-price-1",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "li.athenaBasket_basketItemRow:nth-child(1) div.athenaBasket_bodyItem-subTotal",
            "type": "SelectorText"
        },
        {
            "id": "product-name-2",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "li.athenaBasket_basketItemRow:nth-child(2) .athenaBasket_itemName",
            "type": "SelectorText"
        },
        {
            "id": "product-price-2",
            "multiple": False,
            "parentSelectors": ["_root"],
            "regex": "",
            "selector": "li.athenaBasket_basketItemRow:nth-child(2) div.athenaBasket_bodyItem-subTotal",
            "type": "SelectorText"
        }
    ],
    "_id": "myprotein-basket"
}

async def login(page):
    await page.goto('https://www.myprotein.es/login.jsp', {'waitUntil': 'networkidle2'})
    await page.type('input[type="email"]', 'pedrominguezquevedo@gmail.com')
    await page.type('input[type="password"]', 'Agualanjaron1.')
    await page.click('button[type="submit"]')
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    #if 'myprotein.es' in page.url:
        #print('Inicio de sesión exitoso')
    #else:
        #print('Falló el inicio de sesión')

async def get_data(url):
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
    page = await browser.newPage()
    #print("Iniciando sesión...")
    await login(page) # Llamamos a la función login antes de acceder a la página de la cesta
    #print("Accediendo a la página de la cesta...")
    await page.goto(url, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)
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
        product_name_1 = d.get('product-name-1').strip().upper()
        product_price_1 = d.get('product-price-1').strip()
        product_name_2 = d.get('product-name-2').strip().upper()
        product_price_2 = d.get('product-price-2').strip()
        product_url_1 = "https://www.myprotein.es/nutricion-deportiva/impact-whey-protein/10530943.html?variation=10530986"
        product_url_2 = "https://www.myprotein.es/nutricion-deportiva/caseina-de-liberacion-lenta/10798909.html?variation=10798922"
        if product_name_1 and product_price_1 and product_name_2 and product_price_2:
            msg = (f"*MP |* [{product_name_1}]({product_url_1}) * | {product_price_1}*")
            print(msg)
            telegramMSG(msg)
            msg = (f"*MP |* [{product_name_2}]({product_url_2}) * | {product_price_2}*")
            print(msg)
            telegramMSG(msg)

# Imprimir uso de recursos
process = psutil.Process()
memory_info = process.memory_info()
print(f"\nUso de memoria: {memory_info.rss / 1024 / 1024:.2f} MB")
print(f"Uso de CPU: {psutil.cpu_percent()}%")
