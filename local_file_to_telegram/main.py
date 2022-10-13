import asyncio
import random
import re
import sqlite3
import time
from pathlib import Path

from aiogram import Bot
from aiogram.types import InputFile

db = sqlite3.connect("document.db")

db.execute("CREATE TABLE IF NOT EXISTS document(name VARCHAR(300));")
db.commit()

existing_documents = [
    i[0] for i in db.execute("SELECT * FROM documents").fetchall()
]


# Constants

TOKEN = ""  # Telegram Bot token
CHAT_ID = ""  # Channel username
HOME_DIR = ""  # Path to folder directory
FILE_EXTENTIONS = [".doc", ".docx", ".pdf", ".txt"]
MAX_WAIT_TIME = 30  # Maximum waiting time for sending documents
MIN_WAIT_TIME = 15  # Minimum waiting time for sending documents

bot = Bot(TOKEN)

home_dir = Path(HOME_DIR)


documents = []  # Matched documents inside a given directory


def find_documents(dir):
    # Find directories inside the folder which may contain a documents
    # recursively
    dirs = filter(lambda c: c.is_dir(), dir.iterdir())
    for d in dirs:
        find_documents(d)
    files = filter(lambda c: c.is_file(), home_dir.iterdir())
    for file in files:
        if file.suffix in FILE_EXTENTIONS:
            documents.append(file)


def to_hashtag(doc):
    return "#" + "".join(
        [
            name.capitalize()
            for name in re.sub(r"[\-\_]", " ", doc.parent.name).split()
        ]
    )


def get_file_name(doc):
    return re.sub(r"[\-\_]", " ", doc.stem)


find_documents(home_dir)  # Start from home directory

for doc in documents:
    if doc.name in existing_documents:
        continue

    # Avoild Telegram Flood
    time.sleep(random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME))

    CAPTION = "\n\n".join([get_file_name(doc), to_hashtag(doc), CHAT_ID])

    try:
        asyncio.run(
            bot.send_document(
                CHAT_ID, document=InputFile(doc), caption=CAPTION
            )
        )
        db.execute("INSERT INTO document VALUES(?);", (doc.name,))
        db.commit()
    except Exception as error:
        print(error)
