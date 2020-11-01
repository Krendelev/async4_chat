import asyncio
import logging
import os
from contextlib import closing

from dotenv import load_dotenv

from astdio import ainput
from utils import authorize, get_args, register


async def chat_writer(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    with closing(writer):
        await authorize(reader, writer, token)

        while True:
            data = await reader.readuntil()
            logging.debug(data.decode().strip())

            input_ = await ainput("> ")
            logging.debug(input_)
            writer.write(f"{input_}\n\n".encode())
            await writer.drain()


async def main():
    load_dotenv()
    args = get_args()

    try:
        token = os.environ["TOKEN"]
        username = os.environ["USERNAME"]
    except KeyError:
        token, username = await register(args.host, args.outport)
        print(f"Welcome {username}! Registration complete.")

    await chat_writer(args.host, args.outport, token)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)s  %(message)s",
        filename="chat.log",
    )
    asyncio.run(main())
