import asyncio
import urllib.parse

import aiohttp

from . import app

AUTH_HEADER = {'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'}
REQUEST_UPLOAD_URL = (
    f'{app.config["YADISK_API_HOST"]}{app.config["YADISK_API_VERSION"]}'
    '/disk/resources/upload'
)
DOWNLOAD_LINK_URL = (
    f'{app.config["YADISK_API_HOST"]}{app.config["YADISK_API_VERSION"]}'
    '/disk/resources/download'
)


# Асинхронная функция, которая создаёт задачи и запускает их.
async def async_upload_files_to_ydisk(files):
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file_item in files:
                tasks.append(
                    asyncio.ensure_future(
                        get_download_link(session, file_item)
                    )
                )
            urls = await asyncio.gather(*tasks)
        return urls


async def get_download_link(session, file_item):
    payload = {
        'path': f'/Приложения/uploads/{file_item.filename}',
        'overwrite': 'True'
    }
    async with session.get(
        headers=AUTH_HEADER,
        params=payload,
        url=REQUEST_UPLOAD_URL
    ) as response:
        data = await response.json()
        upload_url = data['href']

    await asyncio.to_thread(file_item.seek, 0)
    filecontent = await asyncio.to_thread(file_item.read)
    async with session.put(
        data=filecontent,
        url=upload_url,
    ) as response:
        data = response.headers
        location = data.get('Location')

    location = urllib.parse.unquote(location)
    location = location.replace('/disk', '')

    async with session.get(
        headers=AUTH_HEADER,
        url=DOWNLOAD_LINK_URL,
        params={'path': location}
    ) as response:
        data = await response.json()
        link = data['href']

    return {'filename': file_item.filename, 'original_link': link}