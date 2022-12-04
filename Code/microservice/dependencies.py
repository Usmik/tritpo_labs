from kink import di
import boto3
from dotenv import dotenv_values
from boto3.resources.base import ServiceResource
from boto3.dynamodb.table import TableResource
import pika


def microservice_di() -> None:
    """
    Function that define dependencies, to be registered in inside dependency injection container
    """
    config = dotenv_values('.env')
    db = boto3.resource('dynamodb',
                        endpoint_url=config['AWS_ENDPOINT_URL'],
                        region_name=config['AWS_DEFAULT_REGION'],
                        aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])

    if not list(db.tables.all()):
        table = initialize_db(db)
    else:
        table = db.Table('Statistic')

    di['database'] = db
    di['db_table'] = table

    conn_params = pika.ConnectionParameters(host='rabbit', port=5672)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue='fastapi')

    di['channel'] = channel


def initialize_db(db: ServiceResource) -> TableResource:
    """
    Function that create a table in db, that are specified as a parameter, and return that Table
    """
    table = db.create_table(
            TableName='Statistic',
            KeySchema=[
                {
                    'AttributeName': 'page_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'page_id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            })
    print(f'Table status: {table.table_status}')

    return table
