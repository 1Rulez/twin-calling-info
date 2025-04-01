from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database: PostgresDsn
    database_schema: str
    debug_enabled: bool
    interface_opened: bool
    twin_auth_url: str
    twin_contacts_url: str
    twin_create_call_url: str
    twin_send_contacts_url: str
    twin_login: str
    twin_password: str
    twin_ttl: str
    twin_webhook: str

    date_start: str = '2025-02-24'

    tg_token: str
    tg_chat_id: str

    redis_host: str
    redis_user: str
    redis_user_password: str
    redis_port: str
    redis_db: int
