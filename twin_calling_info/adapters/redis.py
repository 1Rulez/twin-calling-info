import redis


class RedisStorage:
    def __init__(self, redis_host, redis_port, redis_user, redis_db, password):
        self.redis_client = redis.StrictRedis(
            host=redis_host,
            username=redis_user,
            port=redis_port,
            db=redis_db,
            password=password,
            decode_responses=True
        )

    def save_token(self, token: str, key: str, expiration: int | None = 3600):
        """
        Сохраняет токен в Redis.

        :param key: ключ редис
        :param token: Токен авторизации.
        :param expiration: Время жизни токена в секундах (по умолчанию 3600 секунд).
        :return: None
        """
        self.redis_client.set(key, token, ex=expiration)

    def get_token(self, key: str):
        """
        Извлекает токен из Redis.
        :param key: ключ редис
        :return: Токен или None, если токен не найден.
        """
        token = self.redis_client.get(key)
        return token

    def del_key(self, key: str):
        """
        Удаляет ключ из Redis.
        :param key: ключ редис
        :return: bool
        """
        result = self.redis_client.delete(key)
        return result > 0
