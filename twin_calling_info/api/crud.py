from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from twin_calling_info.adapters.redis import RedisStorage
from twin_calling_info.adapters.twin import TwinRepository
from twin_calling_info.configuration import Request
from twin_calling_info.models import CalNumbers
from twin_calling_info.shemas.create_call import CreateCallModel, SendContacts, Contact

def get_redis_cli(request: Request) -> RedisStorage:
    redis_host = request.app.container.settings.redis_host
    redis_user = request.app.container.settings.redis_user
    redis_password = request.app.container.settings.redis_user_password
    redis_port = request.app.container.settings.redis_port
    redis_db = request.app.container.settings.redis_db

    redis_cache = RedisStorage(
        redis_host=redis_host, redis_port=redis_port,
        password=redis_password, redis_user=redis_user,
        redis_db=redis_db,
    )
    return redis_cache


def get_twin_repo(request: Request, redis: RedisStorage) -> TwinRepository:
    auth_url = request.app.container.settings.twin_auth_url
    create_call_url = request.app.container.settings.twin_create_call_url
    send_contacts_url = request.app.container.settings.twin_send_contacts_url
    login = request.app.container.settings.twin_login
    password = request.app.container.settings.twin_password
    twin_ttl = request.app.container.settings.twin_ttl
    logger = request.app.container.logger
    twin_operation = TwinRepository(
        auth_url=auth_url, create_call_url=create_call_url,
        send_contacts_url=send_contacts_url, login=login,
        password=password, redis=redis, twin_ttl=int(twin_ttl),
        logger=logger
    )
    return twin_operation


async def get_contacts(session: AsyncSession) -> list[CalNumbers]:
    query = select(CalNumbers).where(CalNumbers.is_active.is_(True))
    return (await session.execute(query)).scalars().all()

def get_send_contact(data: list[CalNumbers]) -> SendContacts:
    send_cont = SendContacts()
    contacts, variables = [], {}
    current_time = (datetime.now() + timedelta(hours=3)).time()
    for cont in data:
        if cont.time_start <= current_time <= cont.time_end:
            contacts.append(
                Contact(
                    phone=[cont.phone],
                    variables={"line_phone": cont.phone}
                )
            )
    send_cont.batch = contacts
    return send_cont


class SendContactError(Exception):
    pass

async def send_contacts(contacts: list[CalNumbers], twin: TwinRepository, webhook: str):
    if contacts:
        contacts_data = get_send_contact(contacts)
        task_data = CreateCallModel(webhookUrls=[webhook]).model_dump()
        resp = await twin.send_twin_cont(
            task_data=task_data,
            contacts_data=contacts_data,
            task_key='call_task'
        )
        if resp.status == 200:
            return
        raise SendContactError(
            f'Send contacts error: {contacts_data} \n response: {resp}'
        )

async def get_call_statistic_info(session: AsyncSession):
    current_date = datetime.now().date()
    query = f"""
        select count(*)
        from call_statistic.call_info ci
        where ci.project = 'api_connector@bztwin.zxc'
        and ci."startedAt" >= '{current_date}'
    """
    return (await session.execute(text(query))).scalar()
