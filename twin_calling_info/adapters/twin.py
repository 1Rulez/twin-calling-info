import logging
import aiohttp
import asyncio
import random

from twin_calling_info.decorators import error_handler
from twin_calling_info.shemas.create_call import CreateCallModel, SendContacts, Contact
from twin_calling_info.adapters.redis import RedisStorage


class TwinRepository:

    def __init__(
            self,
            auth_url: str,
            create_call_url: str,
            send_contacts_url: str,
            login: str,
            password: str,
            twin_ttl: int,
            redis: RedisStorage,
            logger: logging.Logger = None
    ):
        self.auth_url = auth_url
        self.login = login
        self.password = password
        self.create_call_url = create_call_url
        self.send_contacts_url = send_contacts_url
        self.redis: RedisStorage = redis
        self.twin_ttl = twin_ttl
        self.logger = logger

    @error_handler
    async def send_twin_cont(
            self,
            task_data: CreateCallModel | dict,
            contacts_data: SendContacts,
            task_key: str
    ):
        token = await self._get_auth_token()
        task_id = await self._get_task(data=task_data, token=token, task_key=task_key)
        contacts_data.batch = self.upd_call_id(task_id, contacts_data.batch)
        contacts_data = contacts_data.model_dump()
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.send_contacts_url, headers=headers, json=contacts_data) as response:
                response.raise_for_status()
                self.logger.info(response)
                if response.status == 422:
                    self.redis.del_key(task_key)
        return response

    async def _get_task(self, data: CreateCallModel, token: str, task_key: str):
        task_id = self.redis.get_token(key=task_key)
        if not task_id:
            task_id = await self._create_call_task(data, token)
            self.redis.save_token(task_id, key=task_key, expiration=None)
        return task_id

    async def _get_auth_token(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        json_data = {
            'email': self.login,
            'password': self.password,
            'ttl': self.twin_ttl,
        }
        await asyncio.sleep(random.randint(5, 10))
        async with aiohttp.ClientSession() as session:
            async with session.post(self.auth_url, headers=headers, json=json_data) as response:
                response.raise_for_status()
                if response.status == 200:
                    data = await response.json()
                    return data.get("token")

    async def _create_call_task(self, data: CreateCallModel, token: str):
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {token}"}
        await asyncio.sleep(random.randint(10, 15))
        async with aiohttp.ClientSession() as session:
            async with session.post(self.create_call_url, headers=headers, json=data) as response:
                response.raise_for_status()
                if response.status == 200:
                    data = await response.json()
                    return data.get("id").get("identity")

    @staticmethod
    def upd_call_id(task_id: str, contacts: list[Contact]) -> list[Contact]:
        update_contacts = []
        for cont in contacts:
            cont.autoCallId = task_id
            update_contacts.append(cont)
        return update_contacts
