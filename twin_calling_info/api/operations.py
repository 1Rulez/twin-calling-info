from datetime import timedelta

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response

from twin_calling_info.api.crud import get_contacts, get_twin_repo, get_redis_cli, send_contacts, get_call_statistic_info
from twin_calling_info.configuration import Request
from twin_calling_info.api.input_models import InputCallEnd
from twin_calling_info.adapters.telegram import Telegram

operation_router = APIRouter()

def get_session(request: Request) -> AsyncSession:
    return AsyncSession(bind=request.app.container.database_engine)


@operation_router.post("/send_call")
async def send_call(request: Request) -> Response:
    """'Ручка' для отправки на обзвон"""
    redis_repo = get_redis_cli(request)
    twin_repo = get_twin_repo(request, redis_repo)
    webhook = request.app.container.settings.twin_webhook
    async with get_session(request) as session:
        contacts = await get_contacts(session)
        await send_contacts(contacts=contacts, twin=twin_repo, webhook=webhook)
    return Response()

@operation_router.post("/sessions")
async def add_session(event: InputCallEnd, request: Request) -> Response:
    """'Ручка' для анализа данных звонка"""
    tg_token = request.app.container.settings.tg_token
    tg_chat_id = request.app.container.settings.tg_chat_id
    if event.event == 'CALL_ENDED':
        if event.status and event.status != 'ANSWERED':
            message = \
f"""❗️❗️❗️
Не удалось дозвониться до номера: {event.callTo}
Время: {(event.startedAt + timedelta(hours=3)).strftime("%d-%m-%Y %H:%M")} по мск
Статус вызова: {event.status}
Необходимо узнать причину
"""
            await Telegram(tg_token, tg_chat_id).send_telegram_message(message)
    return Response()


@operation_router.post("/send_info")
async def send_call_statistic_tg(request: Request) -> Response:
    """'Ручка' для получения информации в ТГ"""
    tg_token = request.app.container.settings.tg_token
    tg_chat_id = request.app.container.settings.tg_chat_id
    twin_acc = request.app.container.settings.twin_login
    async with get_session(request) as session:
        call_count = await get_call_statistic_info(session)
        message = f"""Количество звонков за сутки: {int(call_count)}"""
    await Telegram(tg_token, tg_chat_id).send_telegram_message(message)
    return Response()



