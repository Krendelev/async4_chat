import asyncio
import json
import logging
import os
import sys
import socket

from dotenv import load_dotenv
from utils import get_args


async def ainput():
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader(loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return await reader.readuntil()


def register(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.recv(4096)
        sock.send(b"\n")
        sock.recv(4096)
        username = input("Hello user! Please enter your preferred nickname:\n")
        sock.send(f"{username}\n".encode())
        response = sock.recv(4096).decode()

    creds = json.loads(response)
    with open(".env", "w") as fh:
        fh.write(f"TOKEN={creds['account_hash']}\nUSERNAME={creds['nickname']}")

    print(f"Welcome {creds['nickname']}! Registration complete")
    return creds["account_hash"], creds["nickname"]


async def authorize(host, port):
    try:
        token = os.environ["TOKEN"]
        username = os.environ["USERNAME"]
    except KeyError:
        token, username = register(host, port)

    input_ = input(
        f"Join chat as {username} or register new user?\nPress 'R' to register, 'Enter' to join: "
    )
    if input_.lower() == "r":
        token, _ = register(host, port)

    reader, writer = await asyncio.open_connection(host, port)
    await reader.readline()
    writer.write(f"{token}\n\n".encode())
    await reader.readline()

    return reader, writer


async def chat_writer(host, port):
    reader, writer = await authorize(host, port)

    while True:
        data = await reader.readuntil()
        message = data.decode().strip()
        logging.debug(message)
        print(message)

        input_ = await ainput()
        logging.debug(input_.decode())
        writer.write(input_ + b"\n\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)s  %(message)s",
        filename="chat.log",
    )
    load_dotenv()
    args = get_args()
    asyncio.run(chat_writer(args.host, args.outport))
