import logging

from botocore.exceptions import ClientError
from kink import inject
from boto3.dynamodb.table import TableResource


@inject()
def page_stats(page_id: int, db_table: TableResource) -> dict:
    """
    Function that return statistic for existing page
    :param page_id: ID of page that would be handled
    :param db_table: Table in DB in which we work
    :return: Statistics of page
    """
    return db_table.get_item(Key={'page_id': page_id})['Item']


@inject()
async def new_page(page_id: int, db_table: TableResource) -> None:
    """
    Function that create a new page as an item in db
    :param page_id: ID of page that would be created
    :param db_table: Table in DB in which we work
    """
    db_table.put_item(Item={
        'page_id': page_id,
        'posts_count': 0,
        'likes_count': 0,
        'followers_count': 0
    })


@inject()
async def post_plus(page_id: int, db_table: TableResource) -> None:
    """
    Function that increment count of posts on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """
    db_table.update_item(
        Key={'page_id': page_id},
        UpdateExpression='ADD posts_count :inc',
        ExpressionAttributeValues={':inc': 1})


@inject()
async def post_minus(page_id: int, db_table: TableResource) -> None:
    """
    Function that decrement count of posts on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """
    try:
        db_table.update_item(
            Key={'page_id': page_id},
            UpdateExpression='ADD posts_count :dec',
            ConditionExpression="posts_count > :zero",
            ExpressionAttributeValues={':dec': -1,
                                       ':zero': 0})
    except ClientError as err:
        logging.error(err.response['Error']['Code'])


@inject()
async def like_plus(page_id: int, db_table: TableResource) -> None:
    """
    Function that increment count of likes on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """
    db_table.update_item(
        Key={'page_id': page_id},
        UpdateExpression='ADD likes_count :inc',
        ExpressionAttributeValues={':inc': 1})


@inject()
async def like_minus(page_id: int, db_table: TableResource) -> None:
    """
    Function that decrement count of likes on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """
    try:
        db_table.update_item(
            Key={'page_id': page_id},
            UpdateExpression='ADD likes_count :dec',
            ConditionExpression="likes_count > :zero",
            ExpressionAttributeValues={':dec': -1,
                                       ':zero': 0})
    except ClientError as err:
        logging.error(err.response['Error']['Code'])


@inject()
async def follower_plus(page_id: int, db_table: TableResource) -> None:
    """
    Function that increment count of followers on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """

    db_table.update_item(
        Key={'page_id': page_id},
        UpdateExpression='ADD followers_count :inc',
        ExpressionAttributeValues={':inc': 1})


@inject()
async def follower_minus(page_id: int, db_table: TableResource) -> None:
    """
    Function that decrement count of followers on a specified page
    :param page_id: ID of page that would be changed
    :param db_table: Table in DB in which we work
    """
    try:
        db_table.update_item(
            Key={'page_id': page_id},
            UpdateExpression='ADD followers_count :dec',
            ConditionExpression="followers_count > :zero",
            ExpressionAttributeValues={':dec': -1,
                                       ':zero': 0})
    except ClientError as err:
        logging.error(err.response['Error']['Code'])
