from prometheus_client import Counter
import socket



def get_instance_id():
    return socket.gethostname()


instance_id = get_instance_id()


async def inc_counters():
    unknown_command_counter.labels(instance=instance_id).inc(0)
    count_instance_errors.labels(instance=instance_id).inc(0)
    count_user_errors.labels(instance=instance_id).inc(0)
    database_errors_counters[0].labels(instance=instance_id).inc(0)
    database_errors_counters[1].labels(instance=instance_id).inc(0)
    database_errors_counters[2].labels(instance=instance_id).inc(0)
    database_errors_counters[3].labels(instance=instance_id).inc(0)
    validation_error.labels(instance=instance_id).inc(0)

    for status_code in [401, 403]:
        external_api_error.labels(instance=instance_id, status_code=status_code).inc(0)


database_errors_counters = [
    Counter('database_connection_errors', 'Database connection errors', ['instance']),
    Counter('database_query_errors', 'Database query errors', ['instance']),
    Counter('database_other_errors', 'Other database errors', ['instance']),
    Counter('data_base_runtime', 'Database runtime errors', ['instance'])
]
external_api_error = Counter('external_api_error', 'Count of errors', ['instance', 'status_code'])

validation_error = Counter('external_api_validation_errors', 'Count of validation errors from external API services', ['instance'])

unknown_command_counter = Counter('unknown_commands', 'Count of unknown commands received',
                                  ['instance'])

count_instance_errors = Counter('instance_errors', 'Count of errors by instance', ['instance'])

count_user_errors = Counter('user_errors', 'User interaction errors', ['instance'])


#
# Дашборд 1: Общая информация
#
# Название: "Общая информация"
# Метрики:
# Количество неизвестных команд (unknown_command_counter)
# Количество ошибок по экземплярам (count_instance_errors)
# Количество ошибок пользователей (count_user_errors)
# Графики:

# Линейный график для каждого счетчика
# Дашборд 2: Ошибки базы данных
#
# Название: "Ошибки базы данных"
# Метрики:
# Количество ошибок подключения к базе данных (database_errors_counters[0])
# Количество ошибок запросов к базе данных (database_errors_counters[1])
# Количество других ошибок базы данных (database_errors_counters[2])
# Количество ошибок рантайма базы данных (database_errors_counters[3])
# Графики:
# Столбчатый график для каждого счетчика
# Линейный график для отображения тенденций
# Дашборд 3: Внешние API
#
# Название: "Внешние API"
# Метрики:
# Количество ошибок внешних API (external_api_requests)
# Количество ошибок валидации внешних API (validation_error)
# Графики:
# Столбчатый график для каждого счетчика
# Линейный график для отображения тенденций
# Дашборд 4: Статус запросов
#
# Название: "Статус запросов"
# Метрики:
# Количество запросов с статус-кодом 200 (external_api_requests с фильтром по статус-коду 200)
# Количество запросов с статус-кодом 400 (external_api_requests с фильтром по статус-коду 400)
# Количество запросов с статус-кодом 401 (external_api_requests с фильтром по статус-коду 401)
# Количество запросов с статус-кодом 403 (external_api_requests с фильтром по статус-коду 403)
# Количество запросов с статус-кодом 404 (external_api_requests с фильтром по статус-коду 404)
# Количество запросов с статус-кодом 500 (external_api_requests с фильтром по статус-коду 500)
# Количество запросов с статус-кодом 502 (external_api_requests с фильтром по статус-коду 502)
# Графики:
# Круговая диаграмма для отображения распределения статус-кодов
#
#

# Дашборд 1: Общая информация
#
# Название: "Общая информация"
# Панели:
# "Количество неизвестных команд" (unknown_command_counter)
# "Количество ошибок по экземплярам" (count_instance_errors)
# "Количество ошибок пользователей" (count_user_errors)
# "Время обработки запросов" (fastapi_request_duration)
# Дашборд 2: Ошибки базы данных
#
# Название: "Ошибки базы данных"
# Панели:
# "Количество ошибок подключения к базе данных" (database_errors_counters[0])
# "Количество ошибок запросов к базе данных" (database_errors_counters[1])
# "Количество других ошибок базы данных" (database_errors_counters[2])
# "Время обработки запросов к базе данных" (database_request_duration)
# Дашборд 3: Экземпляры
#
# Название: "Экземпляры"
# Панели:
# "Количество ошибок по экземплярам" (count_instance_errors)
# "Количество ошибок пользователей по экземплярам" (count_user_errors)
# "Время обработки запросов по экземплярам" (fastapi_request_duration_by_instance)
# Стандартные дашборды для FastAPI
#
# Дашборд 1: Общая информация
# "Количество запросов" (fastapi_requests_total)
# "Количество ошибок" (fastapi_errors_total)
# "Количество исключений" (fastapi_exceptions_total)
# "Время обработки запросов" (fastapi_request_duration)
# Дашборд 2: Запросы
# "Количество запросов по методам" (fastapi_requests_by_method)
# "Количество запросов по статусам" (fastapi_requests_by_status)
# "Время обработки запросов по методам" (fastapi_request_duration_by_method)
# Дашборд 3: Ошибки
# "Количество ошибок по типам" (fastapi_errors_by_type)
# "Количество ошибок по статусам" (fastapi_errors_by_status)
# "Время обработки ошибок" (fastapi_error_duration)
