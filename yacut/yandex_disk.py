import asyncio
import re
import uuid

import aiohttp
from http import HTTPStatus

from yacut import app

AUTH_HEADER = {'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'}
YADISK_API_BASE = f'{app.config["DISK_API_HOST"]}{
    app.config["DISK_API_VERSION"]
}'
UPLOAD_URL = f'{YADISK_API_BASE}/disk/resources/upload'
DOWNLOAD_URL = f'{YADISK_API_BASE}/disk/resources/download'


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


async def async_upload_files_to_disk(files):
    if not files:
        return []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for file_item in files:
            safe_filename = sanitize_filename(file_item.filename)
            tasks.append(get_download_link(session, file_item, safe_filename))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]


async def get_download_link(session, file_item, safe_filename):
    file_path = f'app:/{uuid.uuid4().hex}_{
        sanitize_filename(file_item.filename)
    }'

    async with session.get(
        url=UPLOAD_URL,
        headers=AUTH_HEADER,
        params={'path': file_path, 'overwrite': 'true'}
    ) as response:
        if response.status != HTTPStatus.OK:
            error = await response.json()
            raise Exception(
                f'Не удалось получить URL-адрес загрузки: {error}'
            )
        data = await response.json()
        upload_url = data['href']

    await asyncio.to_thread(file_item.seek, 0)
    filecontent = await asyncio.to_thread(file_item.read)

    async with session.put(
        url=upload_url,
        data=filecontent
    ) as response:
        if response.status not in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED
        ):
            raise Exception(
                f'Не удалось загрузить файл: статус {response.status}'
            )

    async with session.get(
        url=DOWNLOAD_URL,
        headers=AUTH_HEADER,
        params={'path': file_path}
    ) as response:
        if response.status != HTTPStatus.OK:
            error = await response.json()
            raise Exception(
                f'Не удалось получить ссылку для скачивания: {error}'
            )
        data = await response.json()
        download_link = data['href']

    return {
        'filename': file_item.filename,
        'original_link': download_link
    }
