from typing import List

import aiohttp
import aiofiles
import os
import logging


async def download_file(url: str, file_dir: str, file_name: str):
    """
    异步下载文件

    :param url: 文件 URL
    :param file_dir: 文件目录
    :param file_name: 文件名
    :return: 文件路径
    """
    os.makedirs(file_dir, exist_ok=True)

    file_path = os.path.join(file_dir, file_name)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                logging.error(
                    f"Failed to download file: {url} (status code: {response.status})"
                )
                return None

            async with aiofiles.open(file_path, "wb") as file:
                # 1MB chunk size
                async for chunk in response.content.iter_chunked(1024 * 1024):
                    await file.write(chunk)

    logging.info(f"Downloaded file: {file_path}")
    return file_path


async def download_image_file(file_dir: str, image_urls: List[str]) -> List[str]:
    return [
        await download_file(image_url, file_dir, f"{index}.jpg")
        for index, image_url in enumerate(image_urls)
    ]
