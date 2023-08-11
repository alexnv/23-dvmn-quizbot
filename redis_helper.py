import redis


def auth_redis(redis_address, redis_port, redis_user, redis_password):
    redis_obj = redis.Redis(host=redis_address, port=redis_port, username=redis_user, password=redis_password,
                            charset='utf-8', decode_responses=True)
    return redis_obj
