import asyncio
import configargparse
import json
import os
from datetime import datetime

import aiofiles


def get_args():
    parser = configargparse.ArgParser(default_config_files=["chat.ini"])
    parser.add("--host", help="URL of chat hosting server")
    parser.add("--inport", type=int, help="port to read from")
    parser.add("--outport", type=int, help="port to write to")
    parser.add("--history", help="where to save transcript")

    return parser.parse_args()


async def save_text(text, file):
    async with aiofiles.open(file, "a") as fh:
        now = datetime.now().strftime("%d.%m.%y %H:%M")
        await fh.writelines(f"[{now}]  {text}")


async def register(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    await reader.readuntil()
    writer.write(b"\n")
    await reader.readuntil()
    username = input("Hello user! Please enter your preferred nickname:\n")
    writer.write(f"{username}\n".encode())
    response = await reader.readuntil()
    writer.close()
    await writer.wait_closed()

    creds = json.loads(response)
    with open(".env", "w") as fh:
        fh.write(f"TOKEN={creds['account_hash']}\nUSERNAME={creds['nickname']}")

    print(f"Welcome {creds['nickname']}! Registration complete.")
    return creds["account_hash"], creds["nickname"]


async def authorize(host, port):
    try:
        token = os.environ["TOKEN"]
        username = os.environ["USERNAME"]
    except KeyError:
        token, username = await register(host, port)

    input_ = input(
        f"Join chat as {username} or register new user?\nPress 'R' to register, 'Enter' to join: "
    )
    if input_.lower() == "r":
        token, _ = await register(host, port)

    reader, writer = await asyncio.open_connection(host, port)
    await reader.readuntil()
    writer.write(f"{token}\n".encode())
    await reader.readuntil()

    return reader, writer
