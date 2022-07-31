import requests
import datetime
import csv
import aiohttp
import aiofiles
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiocsv import AsyncWriter


async def collect_data(city_code='2398'):
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    ua = UserAgent()

    cookies = {
        'PHPSESSID': '3bg13bka4trm0l5lsrc1ohph8l',
        'mg_geo_id': city_code,
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'PHPSESSID=3bg13bka4trm0l5lsrc1ohph8l; mg_geo_id=2398',
        'Origin': 'https://magnit.ru',
        'Referer': 'https://magnit.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'User-Agent': ua.random,
        'X-Requested-With': 'XMLHttpRequest',
        'dnt': '1',
        # 'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Linux"',
        # 'sec-gpc': '1',
    }

    async with aiohttp.ClientSession() as session:
        responsed = await session.get("https://magnit.ru/promo/", headers=headers, cookies=cookies)
        soups = BeautifulSoup(await responsed.text(), "lxml")

        all_cards = soups.find("div", class_='сatalogue__header-col_right').find('p', class_="сatalogue__header-text").text.strip().split(' ')[1]

        paginations = int(int(all_cards) / 50) + 1
        city = soups.find("a", class_="header__contacts-link_city").text.strip()


        datas = []
        for page in range(1, paginations + 1):
            data = {
                'page': f'{page}',
            }

            response = requests.post('https://magnit.ru/promo/', cookies=cookies, headers=headers, data=data)
            soup = BeautifulSoup(response.text, "lxml")
    
            cards = soup.find_all("a", class_="card-sale_catalogue")

            for card in cards:
                try:
                    card_title = card.find('div', class_='card-sale__title').text.strip()

                    card_discount = card.find("div", class_="card-sale__discount").text.strip()

                    card_price_old_integer = card.find("div", class_="label__price_old").find("span", class_="label__price-integer").text.strip()
                    card_price_old_decimal = card.find("div", class_="label__price_old").find("span", class_="label__price-decimal").text.strip()
                    card_old_price = f"{card_price_old_integer}.{card_price_old_decimal}"

                    card_price_integer = card.find("div", class_="label__price_new").find("span", class_="label__price-integer").text.strip()
                    card_price_decimal = card.find("div", class_="label__price_new").find("span", class_="label__price-decimal").text.strip()
                    card_price = f"{card_price_integer}.{card_price_decimal}"

                    card_sale_data = card.find("div", class_="card-sale__date").text.strip().replace('\n', ' ')

                    datas.append(
                        [card_title, card_old_price, card_price, card_discount, card_sale_data]
                    )
                    
                except AttributeError:
                    continue

            print(f"Сбор данных со страницы:{page}  Всего страниц: {paginations}")

    async with aiofiles.open(f"{city}_{cur_time}.csv", "w") as file:
        writer = AsyncWriter(file)

        await writer.writerow(
            [
                'Продукт',
                'Старая цена',
                'Новая цена',
                'Процент скидки',
                'Время акции'
            ]
        )

        await writer.writerows(
            datas
        )

    return f'{city}_{cur_time}.csv'


async def main():
    await collect_data(city_code='2398')

if __name__ == "__main__":
    asyncio.run(main())