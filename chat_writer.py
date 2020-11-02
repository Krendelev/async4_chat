import asyncio
import logging
import os
from contextlib import closing

from dotenv import load_dotenv

from utils import authorize, connect_to_server, get_argparser, register


async def chat_writer(host, port, token):
    reader, writer = await connect_to_server(host, port)
    await authorize(reader, writer, token)

    with closing(writer):
        while True:
            data = await reader.readuntil()
            logging.debug(data.decode().strip())
            input_ = input("> ")
            logging.debug(input_)
            writer.write(f"{input_}\n\n".encode())
            await writer.drain()


async def main():
    load_dotenv()

    argparser = get_argparser()
    argparser.add_argument("--port", type=int, default=5050, help="port to write to")
    args = argparser.parse_args()

    try:
        token = os.environ["TOKEN"]
        username = os.environ["USERNAME"]
    except KeyError:
        try:
            token, username = await register(args.host, args.port)
            print(f"Welcome {username}! Registration complete.")
        except asyncio.TimeoutError:
            print(f"Can't connect to {args.host}")
            return

    while True:
        try:
            await chat_writer(args.host, args.port, token)
        except asyncio.TimeoutError:
            print(f"Can't connect to {args.host}")
            return
        except (ConnectionResetError, asyncio.exceptions.IncompleteReadError):
            print(f"Lost connection to {args.host}. Trying to reconnect...")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)s  %(message)s",
        filename="chat.log",
    )
    asyncio.run(main())
