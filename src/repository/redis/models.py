from redis_om import get_redis_connection, HashModel

redis = get_redis_connection(
    host="redis-15567.c57.us-east-1-4.ec2.cloud.redislabs.com",
    port=15567,
    password="IrsVdfDWKfQETZLf5weRyVjH5Lwyr8hQ",
    decode_responses=True,
)


class Delivery(HashModel):
    budget: int = 0
    notes: str = ''

    class Meta:
        database = redis


class Event(HashModel):
    delivery_id: str = None
    type: str
    data: str

    class Meta:
        database = redis
