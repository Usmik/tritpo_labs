from fastapi import FastAPI, Depends
from consumer import start_consumer
from multiprocessing import Process
import services
from pydantic import BaseModel
from typing import Literal


app = FastAPI()

process = Process(target=start_consumer)
process.start()


class ActionItem(BaseModel):
    action: Literal['plus', 'minus']


@app.get('/stats/{page_id}')
async def stats(page_id: int):
    return services.page_stats(page_id=page_id)


@app.post('/page/{page_id}')
async def page(page_id: int, action: str):
    if action == 'new':
        await services.new_page(page_id)


@app.put('/post/{page_id}')
async def post(page_id: int, action: ActionItem = Depends()):
    match action.action:
        case 'plus':
            await services.post_plus(page_id)
        case 'minus':
            await services.post_minus(page_id)


@app.put('/like/{page_id}')
async def post(page_id: int, action: ActionItem = Depends()):
    match action.action:
        case 'plus':
            await services.like_plus(page_id)
        case 'minus':
            await services.like_minus(page_id)


@app.put('/follower/{page_id}')
async def post(page_id: int, action: ActionItem = Depends()):
    match action.action:
        case 'plus':
            await services.follower_plus(page_id)
        case 'minus':
            await services.follower_minus(page_id)
