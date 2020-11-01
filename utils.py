import asyncio
import configargparse
import json
import logging
import os
from contextlib import closing

import aiofiles


def get_args():
    parser = configargparse.ArgParser(default_config_files=["chat.ini"])
    parser.add("--host", help="URL of chat hosting server")
    parser.add("--inport", type=int, help="port to read from")
    parser.add("--outport", type=int, help="port to write to")
    parser.add("--history", help="where to save transcript")

    return parser.parse_args()


async def save_text(file, mode, text):
    async with aiofiles.open(file, mode) as fh:
        await fh.writelines(text)


async def register(host, port):
    reader, writer = await asyncio.open_connection(host, port)
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
