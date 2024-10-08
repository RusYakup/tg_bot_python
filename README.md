# WeatherForecastBot

WeatherForecastBot is your personal assistant for getting accurate weather forecasts. It provides weather information for any city. Just enter the city name, and the bot will inform you about the weather!

## Featuresa

- Get the current weather information for any city
- Accurate and timely weather data

## Installation

Follow these steps to set up and run the project:

### Cloning the Repository

```bash
git clone https://github.com/yourusername/WeatherForecastBot.git
cd WeatherForecastBot
```

## Using Docker

Follow these steps to build and run the Docker container:

### Building Docker Image

Use the following command to build the Docker image:

```bash
docker build -t weather-forecast-bot .
```

### Running Docker Container

Run the Docker container using the following command:

```bash
docker run -d --name weather-forecast-bot -p 8000:8000 weather-forecast-bot
```

This will start the container and map host port 8000 to container port 8000.

## Using Docker Compose

Follow these steps to use Docker Compose to run the project:

### Environment Configuration

Create a `.env` file in the project's root directory and add the necessary environment variables:

```env
TOKEN=your_telegram_bot_token
API_KEY=your_api_key
TG_BOT_API_URL=your_telegram_bot_api_url
APP_DOMAIN=your_app_domain
SECRET_TOKEN_TG_WEBHOOK=your_secret_token
NGROK_AUTHTOKEN=your_ngrok_authtoken
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db
```

### Obtaining API Keys

1. **Telegram Bot Token**: Get your bot token from [@BotFather](https://core.telegram.org/bots#botfather).
2. **Weather API Key**: Register at [WeatherAPI](https://www.weatherapi.com/) to create a new API key.

### Running Docker Compose

Use the following command to start all services defined in `docker-compose.yml`:

```bash
cd deploy
docker-compose up --build
```

This will create and run containers for your application and database, as well as set up a tunnel using Ngrok.

## Entry Point

The main script to start your bot:

```python
import traceback
from helpers.helpers import check_bot_token, check_api_key, logging_config
from helpers.set_webhook import set_webhook
from postgres.database_adapters import create_table
import uvicorn
import asyncio
import logging
from config.config import get_settings
from handlers.web_hook_handler import app

log = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        settings = get_settings()
        logging_config(settings.LOG_LEVEL)
        check_bot_token(settings.TOKEN)
        check_api_key(settings.API_KEY)
        set_webhook(settings.TOKEN, settings.APP_DOMAIN, settings.SECRET_TOKEN_TG_WEBHOOK)
        asyncio.run(create_table())
        uvicorn.run(app, host="0.0.0.0", port=8888)
    except Exception as e:
        log.critical("Error during startup: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
        exit(1)
```

### Main script tasks:

1. Load settings using `get_settings()`.
2. Configure logging with `logging_config`.
3. Validate the bot token using `check_bot_token`.
4. Validate the API key using `check_api_key`.
5. Set up the webhook for the Telegram bot using `set_webhook`.
6. Create necessary database tables using `asyncio.run(create_table())`.
7. Start the server using `uvicorn.run`.

## Command Handling and Database Interaction

The project includes several functions for handling commands from users and interacting with the PostgreSQL database.

### Module Functions

#### `check_chat_id`

Checks the presence of `chat_id` in the `user_state` table and inserts a record if not found, then returns user data.

```python
async def check_chat_id(pool: Pool, message):
    try:
        query = "INSERT INTO user_state (chat_id, city, date_difference, qty_days) VALUES ($1, $2, $3, $4) ON CONFLICT (chat_id) DO NOTHING"
        args = [message.chat.id, "Moskva", "None", "None"]
        await execute(pool, query, *args, fetch=True)
        sql_select = select("user_state", fields=("city", "date_difference", "qty_days"))
        query, args = where(sql_select, {"chat_id": ("=", message.chat.id)}, 1)
        res = await execute(pool, query, *args, fetch=True)
        decoded_result = [dict(r) for r in res][0]
        log.info("user_state table updated successfully")
        return decoded_result
    except Exception as e:
        log.debug("An error occurred: %s", str(e))
        log.debug(f"Exception traceback: \n {traceback.format_exc()}")
```

#### `check_waiting`

Checks user status and performs actions based on the status.

```python
async def check_waiting(status_user: dict, pool, message, bot: AsyncTeleBot, config: Settings):
    try:
        if status_user["city"] == "waiting_value":
            await add_city(pool, message, bot, config)
        if status_user["date_difference"] == "waiting_value":
            await add_day(pool, message, bot, config)
            query = await sql_update_user_state_bd(bot, pool, message, "date_difference", "None")
        if status_user["qty_days"] == "waiting_value":
            await get_forecast_several(pool, message, bot, config)
            query = await sql_update_user_state_bd(bot, pool, message, "qty_days", "None")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback: ", traceback.format_exc())
```

#### `handlers`

Handles different message commands and calls corresponding functions.

```python
async def handlers(pool, message, bot, config, status_user):
    try:
        if message.text == '/start':
            await start_message(pool, message, bot)
        elif message.text == '/help':
            await help_message(message, bot)
        elif message.text == '/change_city':
            await change_city(pool, message, bot)
        elif message.text == '/current_weather':
            await weather(message, bot, config, status_user)
        elif message.text == '/weather_forecast':
            await weather_forecast(pool, message, bot)
        elif message.text == '/forecast_for_several_days':
            await forecast_for_several_days(pool, message, bot)
        elif message.text == '/weather_statistic':
            await statistic(pool, message, bot, config, status_user)
        elif message.text == '/prediction':
            await prediction(pool, message, bot, config, status_user)
        else:
            await bot.send_message(message.chat.id, 'Unknown command. Please try again\n/help')
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.error("Exception traceback: ", traceback.format_exc())
    finally:
        await add_statistic_bd(pool, message)
```

### Main Commands

- **`/start`**: Sends a welcome message to the user and initializes their state in the database.
- **`/help`**: Displays a list of available commands and their descriptions.
- **`/change_city`**: Changes the user's current city.
- **`/current_weather`**: Gets the current weather information for the selected city.
- **`/weather_forecast`**: Gets the weather forecast for a specific date.
- **`/forecast_for_several_days`**: Provides a weather forecast for several days (from 2 to 10).
- **`/weather_statistic`**: Gets weather statistics for the last 7 days.
- **`/prediction`**: Predicts the average temperature for 3 days.

## Endpoint to Get User Actions

The new endpoint `/users_actions` allows you to retrieve user action data from the database based on various criteria.

### Input Parameters

- `chat_id` (int, optional): Chat/User ID.
- `from_ts` (int, optional): Start timestamp.
- `until_ts` (int, optional): End timestamp.
- `limits` (int, optional): Maximum number of results. Default is 1000.
- `credentials` (HTTPBasicCredentials, optional): Security credentials. Default is `Security(verify_credentials)`.
- `pool` (Pool, optional): Global database connection pool. Default is `Depends(create_pool)`.

### Return Value

- `list`: List of user actions retrieved based on the specified criteria.

### Exceptions

- `HTTPException`: Raised if an error occurs during the query execution or unauthorized access.

### Request Example

```bash
# Authorization with credentials in the header
curl -u your_username:your_password -X 'GET' \
  'http://localhost:8000/users_actions?chat_id=12345&from_ts=1609459200&until_ts=1612137600&limits=10' \
  -H 'accept: application/json'
```

This request will return user actions with `chat_id` 12345 that occurred between the timestamps `1609459200` and `1612137600`, with a maximum of 10 records.

## Endpoint to Get User Actions Count

The new endpoint `/actions_count` allows you to retrieve the count of user actions from the database based on various criteria.

### Input Parameters

- `chat_id` (int): Chat/User ID.
- `credentials` (HTTPBasicCredentials, optional): Security credentials. Default is `Security(verify_credentials)`.
- `pool` (Pool, optional): Global database connection pool. Default is `Depends(create_pool)`.

### Return Value

- `dict`: Dictionary containing the count of user actions based on the specified criteria.

### Exceptions

- `HTTPException`: Raised if an error occurs during the query execution or unauthorized access.

### Request Example

```bash
# Authorization with credentials in the header
curl -u your_username:your_password -X 'GET' \
  'http://localhost:8000/actions_count?chat_id=12345' \
  -H 'accept: application/json'
```

This request will return the count of user actions with `chat_id` 12345.

#### Example Output

```json
[
    {
        "chat_id": 859805066,
        "month": "2024-06-01T00:00:00+00:00",
        "actions_count": 26
    },
    {
        "chat_id": 859805066,
        "month": "2024-10-01T00:00:00+00:00",
        "actions_count": 98
    },
    {
        "chat_id": 859805066,
        "month": "2024-09-01T00:00:00+00:00",
        "actions_count": 7
    },
    {
        "chat_id": 859805066,
        "month": "2024-05-01T00:00:00+00:00",
        "actions_count": 5
    }
