import asyncio
import configargparse
import json
import logging
from contextlib import closing

import aiofiles

TIMEOUT = 30


def get_argparser():
    parser = configargparse.ArgParser(default_config_files=["chat.ini"])
    parser.add_argument("--host", help="URL of chat hosting server")

    return parser


async def save_text(file, mode, text):
    async with aiofiles.open(file, mode) as fh:
        await fh.writelines(text)


def wait_for(seconds):
    def wrap(func):
        async def wrapped(*args):
            return await asyncio.wait_for(func(*args), seconds)

        return wrapped

    return wrap


@wait_for(TIMEOUT)
async def connect_to_server(host, port):
    while True:
        try:
            return await asyncio.open_connection(host, port)
        except OSError:
            await asyncio.sleep(1)


async def register(host, port):
    reader, writer = await connect_to_server(host, port)
    with closing(writer):
        logging.debug(await reader.readuntil())
        writer.write(b"\n")
        logging.debug(await reader.readuntil())
        username = input("Hello user! Please enter your preferred nickname:\n")
        writer.write(f"{username}\n".encode())
        response = await reader.readuntil()

    creds = json.loads(response)
    record = f"TOKEN={creds['account_hash']}\nUSERNAME={creds['nickname']}"
    await save_text(".env", "w", record)

    return creds["account_hash"], creds["nickname"]


async def authorize(reader, writer, token):
    logging.debug(await reader.readuntil())
    writer.write(f"{token}\n".encode())
    logging.debug(await reader.readuntil())
