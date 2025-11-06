import asyncio
import uuid
from http import HTTPStatus

import aiohttp

from yacut import app
from .exceptions import YandexDiskAPIError

AUTH_HEADER = {'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'}
YADISK_API_BASE = (
    f'{app.config["DISK_API_HOST"]}{app.config["DISK_API_VERSION"]}'
)
UPLOAD_URL = f'{YADISK_API_BASE}/disk/resources/upload'
DOWNLOAD_URL = f'{YADISK_API_BASE}/disk/resources/download'

ERROR_UPLOAD_URL_FAILED = 'Не удалось получить upload URL: {}'
ERROR_FILE_UPLOAD_FAILED = 'Не удалось загрузить файл: статус {}'
ERROR_DOWNLOAD_LINK_FAILED = 'Не удалось получить ссылку для скачивания: {}'


async def async_upload_files_to_disk(files):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                get_download_link(
                    session, file_item, f'{uuid.uuid4().hex}'
                ) for file_item in files
            ]
        )


async def get_download_link(session, file_item, safe_filename):
    disk_path = f'app:/{safe_filename}'

    async with session.get(
        url=UPLOAD_URL,
        headers=AUTH_HEADER,
        params={'path': disk_path, 'overwrite': 'true'}
    ) as response:
        if response.status != HTTPStatus.OK:
            raise YandexDiskAPIError(
                ERROR_UPLOAD_URL_FAILED.format(await response.text())
            )
        upload_url = (await response.json())['href']

    await asyncio.to_thread(file_item.seek, 0)
    filecontent = await asyncio.to_thread(file_item.read)

    async with session.put(upload_url, data=filecontent) as response:
        if response.status not in (
            HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.ACCEPTED
        ):
            raise YandexDiskAPIError(
                ERROR_FILE_UPLOAD_FAILED.format(response.status)
            )

    async with session.get(
        url=DOWNLOAD_URL,
        headers=AUTH_HEADER,
        params={'path': disk_path}
    ) as response:
        if response.status != HTTPStatus.OK:
            raise YandexDiskAPIError(
                ERROR_DOWNLOAD_LINK_FAILED.format(await response.text())
            )

        return (await response.json())['href']
