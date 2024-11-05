from prometheus_client import Counter
import socket


def get_instance_id():
    return socket.gethostname()


async def inc_counters():
    count_database_errors.labels(instance=instance_id).inc(0)
    unknown_command_counter.labels(instance=instance_id).inc(0)
    error_counter.labels(instance=instance_id).inc(0)
    count_general_errors.labels(instance=instance_id).inc(0)
    count_instance_errors.labels(instance=instance_id).inc(0)  # count_instance_errors
    count_user_errors.labels(instance=instance_id).inc(0)

database_errors_counters = [
    Counter('database_connection_errors', 'Database connection errors', ['instance']),
    Counter('database_query_errors', 'Database query errors', ['instance']),
    Counter('database_other_errors', 'Other database errors', ['instance'])
]


instance_id = get_instance_id()

count_database_errors = Counter('database_errors', 'Database errors', ['instance'])  # Database errors +

unknown_command_counter = Counter('unknown_commands', 'Count of unknown commands received',
                                  ['instance'])  # Count of unknown commands received +
error_counter = Counter('errors', 'Count of errors encountered', ['instance'])  # Count of errors encountered +

count_general_errors = Counter('general_errors', 'General application errors', ['instance'])

count_instance_errors = Counter('instance_errors', 'Count of errors by instance', ['instance'])

count_user_errors = Counter('user_errors', 'User interaction errors', ['instance'])  # User interaction errors

