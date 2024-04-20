from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio
import aiohttp
import json
import requests
from telebot.async_telebot import AsyncTeleBot

bot = AsyncTeleBot('TOKEN')

app = FastAPI()


@app.post("/")
async def handle_message(request: Request):
    json_data = await request.json()
    chat_id = json_data.get("chat_id")

    # Check if the incoming message contains text
    if "text" in json_data:
        # Check if the text is not empty
        if json_data["text"]:
            # Respond with "привет" if the message is not empty
            await bot.send_message(chat_id, "привет")


@app.post("/telegram_dispatcher")
async def telegram_dispatcher(request: Request):
    if request.method == 'POST':
        json_string = await request.body()
        json_dict = json.loads(json_string.decode())

        if 'message' in json_dict and 'text' in json_dict['message']:
            message = json_dict['message']['text']
            chat_id = json_dict['message']['chat']['id']

            if message == '/start':
                await bot.send_message(chat_id, 'Привет, я бот. Напиши мне что-нибудь.')
            else:
                await bot.send_message(chat_id, message)

        async with aiohttp.ClientSession() as session:
            async with session.post('YOUR_TELEGRAM_BOT_API_URL', json=json_dict) as response:
                if response.status == 200:
                    return JSONResponse(content={})
                else:
                    return JSONResponse(content={"error": "Failed to process update"}, status_code=response.status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
