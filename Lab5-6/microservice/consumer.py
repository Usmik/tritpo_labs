import json
import services
from encoders import DecimalEncoder
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import BasicProperties, Basic
from kink import inject
from dependencies import microservice_di
import requests

microservice_di()


def callback(ch: BlockingChannel, method: Basic.Deliver, props: BasicProperties, body: str) -> None:
    """
    Function that handle incoming messages, and if it's necessary send back page statistic as a response
    """
    print('[x] Received', json.loads(body))
    print(" [x] Done")
    match json.loads(body):
        case {'field': 'page', 'action': 'stats', 'page': page_pk}:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=json.dumps(services.page_stats(page_id=page_pk),
                                             cls=DecimalEncoder))
        case {'field': 'page', 'action': 'new', 'page': page_pk}:
            requests.post(f'http://localhost:8001/page/{page_pk}', params={'action': 'new'})
        case {'field': field, 'action': action, 'page': page_pk}:
            requests.put(f'http://localhost:8001/{field}/{page_pk}', params={'action': action})
    ch.basic_ack(delivery_tag=method.delivery_tag)


@inject()
def start_consumer(channel: BlockingChannel) -> None:
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(on_message_callback=callback, queue='fastapi')
    channel.start_consuming()
