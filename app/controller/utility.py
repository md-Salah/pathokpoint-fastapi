import slugify as slg
from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
from datetime import datetime
import pytz


def slugify(text):
    """_summary_
    Args:
        text (str): any text (e.g. 'Hello World', 'আমার সোনার বাংলা')
    Returns:
        str: Lower case english slug (e.g. 'hello-world', 'amar-sonar-bangla')
    """
    return slg.slugify(text).replace('aa', 'a').replace('ii', 'i').replace('ea', 'o')


async def unique_slug(base_slug: str, cls: Any, db: AsyncSession) -> str:
    slug = slugify(base_slug)
    counter = 0
    while True:
        result = await db.execute(select(cls).filter_by(slug=slug))
        if not result.scalars().first():
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"


def bangladesh_time(utc_time: datetime) -> str:
    """_summary_
    Args:
        utc_time (str): UTC time string (e.g. '2022-02-02T12:00:00Z')
    Returns:
        str: BST time string (e.g. '24-Aug-2022 12:00 PM')
    """
    return utc_time.astimezone(pytz.timezone('Asia/Dhaka')).strftime('%d-%b-%Y %I:%M %p')


def convert_uuid_to_str(data):
    if isinstance(data, dict):
        return {key: convert_uuid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_to_str(item) for item in data]
    elif isinstance(data, UUID):
        return str(data)
    else:
        return data


def convert_str_to_uuid(data):
    if isinstance(data, dict):
        return {key: convert_str_to_uuid(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_str_to_uuid(item) for item in data]
    elif isinstance(data, str):
        try:
            return UUID(data)
        except ValueError:
            return data
    else:
        return data


def is_filename(val: str) -> bool:
    filename_pattern = r'^[\w,\s-]+\.[A-Za-z]{3,4}$'
    if not val.startswith(('http://', 'https://', 'ftp://')):
        return bool(re.match(filename_pattern, val))

    return False
