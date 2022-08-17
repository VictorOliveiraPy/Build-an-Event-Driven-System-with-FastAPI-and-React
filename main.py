import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import consumers
from src.repository.redis.models import Delivery, Event, redis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/deliveries/{pk}/")
async def get_state(pk: str):
    state = redis.get(f"delivery:{pk}")

    if state is not None:
        return json.loads(state)

    state = build_state(pk)
    redis.set(f'delivery:{pk}', json.dumps(state))

    return state


def build_state(pk: str):
    pks = Event.all_pks()
    all_events = [Event.get(pk) for pk in pks]
    events = [event for event in all_events if event.delivery_id == pk]
    state = {}

    for event in events:
        state = consumers.CONSUMERS[event.type](state, event)

    return all_events


@app.post('/deliveries/')
async def create(request: Request):
    body = await request.json()

    delivery = Delivery(budget=body['data']['budget'], notes=body['data']['notes']).save()
    event = Event(delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()

    state = consumers.CONSUMERS[event.type]({}, event)
    redis.set(f"delivery:{delivery.pk}", json.dumps(state))
    return state


@app.post('/event')
async def dispatch(request: Request):
    body = await request.json()
    delivery_id = body['delivery_id']

    event = Event(delivery_id=delivery_id, type=body['type'], data=json.dumps(body['data'])).save()
    state = await get_state(delivery_id)

    new_state = consumers.CONSUMERS[event.type](state, event)
    redis.set(f"delivery:{delivery_id}", json.dumps(new_state))
    return new_state
