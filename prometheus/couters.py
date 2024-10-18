from prometheus_client import Counter, Histogram, Gauge
import socket


def get_instance_id():
    return socket.gethostname()


instance_id = get_instance_id()
# Gauge для отслеживания текущего количества активных пользователей
current_users_gauge = Gauge('current_users', 'Current number of active users', ['instance'])
total_users_counter = Counter('total_users', 'Total number of users',['instance']) # Total number of users +

# Database errors
count_database_errors = Counter('database_errors', 'Database errors',['instance']) # Database errors +


# Метрика для подсчета ошибок при обработке команд
unknown_command_counter = Counter('unknown_commands', 'Count of unknown commands received',['instance']) # Count of unknown commands received +
error_counter = Counter('errors', 'Count of errors encountered',['instance']) # Count of errors encountered +


# Метрики производительности (время выполнения)
request_duration = Histogram('request_duration_seconds', 'Time spent processing request',['instance'])


# Общие ошибки приложения
count_general_errors = Counter('general_errors', 'General application errors',['instance'])


# Инициализируем счетчик для POST запросов
post_request_counter = Counter('post_requests_total', 'Total number of POST requests received',['instance']) # Total number of POST requests received +



# Метрики для подсчета успешных запросов и ошибок
count_api_weather_errors = Counter('api_weather_errors', 'Errors with weather API',['instance']) # Errors with weather API +
count_successful_requests = Counter('successful_requests', 'Successful requests to weather API',['instance']) # Successful requests +
count_failed_requests = Counter('failed_requests', 'Failed requests to weather API',['instance']) # Failed requests  +
count_instance_errors = Counter('instance_errors', 'Count of errors by instance', ['instance'])
count_response_code_200 = Counter('response_code_200', 'Count of 200 OK responses', ['instance'])
count_response_code_400 = Counter('response_code_400', 'Count of 400 Bad Request responses', ['instance'])
count_response_code_401 = Counter('response_code_401', 'Count of 401 Unauthorized responses', ['instance'])
count_response_code_403 = Counter('response_code_403', 'Count of 403 Forbidden responses', ['instance'])
count_response_code_404 = Counter('response_code_404', 'Count of 404 Not Found responses', ['instance'])
count_response_code_500 = Counter('response_code_500', 'Count of 500 Internal Server Error responses', ['instance'])
count_response_code_502 = Counter('response_code_502', 'Count of 502 Bad Gateway responses', ['instance'])


# Метрики для подсчета ошибок взаимодействия с пользователем
count_user_errors = Counter('user_errors', 'User interaction errors',['instance']) # User interaction errors

# Инициализируем счетчик для неавторизованных запросов
unauthorized_access_counter = Counter('unauthorized_access_errors', 'Count of unauthorized access attempts',['instance']) # Count of unauthorized access attempts +



# 1. Общая информация по запросам и пользователям
# Панель (Panel) 1: Общая статистика
# current_users_gauge: current_users
# Total Users: total_users
# POST Requests: post_requests_total
# Duration of Requests: request_duration_seconds
# 2. Ошибки, связанные с пользователями
# Панель (Panel) 2: Ошибки пользователей
# User Interaction Errors: user_errors
# Unknown Commands: unknown_commands
# 3. Ошибки, связанные с API
# Панель (Panel) 3: Ошибки API
# API Weather Errors: api_weather_errors
# Successful Requests: successful_requests
# Failed Requests: failed_requests
# Unauthorized Access Errors: unauthorized_access_errors
# 4. Ошибки сервера и внутренние ошибки
# Панель (Panel) 4: Ошибки сервера и внутренние ошибки
# General Application Errors: general_errors
# Database Errors: database_errors
# Instance Errors: instance_errors
# 5. HTTP Ответы
# Панель (Panel) 5: Статистика HTTP Ответов
# HTTP 200 Responses: response_code_200
# HTTP 400 Responses: response_code_400
# HTTP 401 Responses: response_code_401
# HTTP 403 Responses: response_code_403
# HTTP 404 Responses: response_code_404
# HTTP 500 Responses: response_code_500
# HTTP 502 Responses: response_code_502