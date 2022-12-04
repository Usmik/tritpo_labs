import json
import pika
import uuid
from kink import inject
from pika.connection import ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import BasicProperties, Basic


@inject
class Statistics:
    def __init__(self, conn_params: ConnectionParameters) -> None:
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        stats = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = stats.method.queue
        self.channel.queue_declare(queue='fastapi')

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch: BlockingChannel, method: Basic.Deliver, props: BasicProperties, body: str) -> None:
        """
        Check if it suitable message
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def publish(self, page_pk: int, field: str, action: str) -> None:
        """
        Send message to microservice for changing specified field on a specified page
        @param page_pk: ID of page that would be changed
        @param field: Field that would be changed ('followers_count', 'likes_count', 'posts_count')
        @param action: 'plus' or 'minus'
        """
        message = {'page': page_pk, 'field': field, 'action': action}
        self.channel.basic_publish(exchange='', routing_key='fastapi', body=json.dumps(message))

    def get_stats(self, page_pk: int) -> dict:
        """
        Get statistic of page from microservice
        @param page_pk: ID of page
        @return: Dict with statistic
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='fastapi',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id),
            body=json.dumps({'page': page_pk, 'field': 'page', 'action': 'stats'}))
        self.connection.process_data_events(time_limit=5)
        return json.loads(self.response)
