from kink import di
import pika


def pika_di():
    conn_params = pika.ConnectionParameters(host='rabbit', port=5672)

    di['conn_params'] = conn_params
