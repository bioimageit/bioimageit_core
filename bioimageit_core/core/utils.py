import datetime
import os
import uuid


def format_date(date: str):
    if date == 'now':
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')
    else:
        return date


def extract_filename(uri: str):
    pos = uri.rfind(os.sep)
    return uri[pos:]


def generate_uuid():
    return str(uuid.uuid4())
