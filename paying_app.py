from aiogram import types
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas as pd

import uvicorn
from main import bot, pattern_url, PAYMENTS_PROVIDER_TOKEN

file_name = "database.xlsx"
app = FastAPI()


async def create_payment(title: str, description: str, img_url: str, prices: list, index):
    return await bot.create_invoice_link(
        title=title,
        description=description,
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency='rub',
        photo_url=img_url,
        photo_size=256,
        photo_width=512,
        photo_height=512,
        prices=prices,
        payload=index,
        provider_data=None
    )


@app.get("/paying/{chat_id}/{name}/{cost}")
async def paying(name: str, cost: int, chat_id: str):
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(
            file_name,
            engine='openpyxl',
        )
    elif file_name.endswith('.xls'):
        df = pd.read_excel(
            file_name,
            engine='xlrd'
        )
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_name)
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        for i in df.iloc:
            if str(i["id"]) == str(name):
                title = i["cours_name"]
                description = i["cours_discription"]
                img_url = i["img_url"]
                prices = [types.LabeledPrice(amount=int(i["cost"]), label=title)]
                break

    return RedirectResponse(await create_payment(title, description, img_url, prices, name))


@app.get("/{chat_id}")
async def get_page(chat_id: str):
    if file_name.endswith('.xlsx'):
        df = pd.read_excel(
            file_name,
            engine='openpyxl',
        )
    elif file_name.endswith('.xls'):
        df = pd.read_excel(
            file_name,
            engine='xlrd'
        )
    elif file_name.endswith('.csv'):
        df = pd.read_csv(file_name)
    file = []

    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        for k, i in enumerate(df.iloc):
            url_pay = f'{pattern_url}/paying/{chat_id}/{k}/{i["cost"]}'
            json = {
                "cours_name": i["cours_name"],
                "cours_discription": i["cours_discription"],
                "cours_about": i["cours_about"],
                "img_url": i["img_url"],
                "url_pay": url_pay
            }
            file.append(json)

    elif file_name.endswith('.csv'):
        for i in df.iloc:
            tmp = str(i[0]).split(";")
            url_pay = f'{pattern_url}/paying/{chat_id}/{i["cours_name"]}/{i["cost"]}'
            json = {
                "cours_name": tmp[0],
                "cours_discription": tmp[1],
                "cours_about": tmp[2],
                "img_url": tmp[3],
                "url_pay": url_pay
            }
            file.append(json)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    marking = env.get_template('marking.html')

    rendered_page = marking.render(
        elements=file
    )
    return HTMLResponse(content=rendered_page, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="v2249831.hosted-by-vdsina.ru", port=443,
                ssl_keyfile='/etc/letsencrypt/live/v2249831.hosted-by-vdsina.ru-0001/privkey.pem',
                ssl_certfile='/etc/letsencrypt/live/v2249831.hosted-by-vdsina.ru-0001/fullchain.pem')
