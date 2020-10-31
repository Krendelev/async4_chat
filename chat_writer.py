import asyncio
import logging
from contextlib import closing

from dotenv import load_dotenv

from astdio import ainput
from utils import authorize, get_args


async def chat_writer(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    with closing(writer):
        await authorize(host, port, reader, writer)

        while True:
            data = await reader.readuntil()
            logging.debug(data.decode().strip())

            input_ = await ainput("> ")
            logging.debug(input_)
            writer.write(f"{input_}\n\n".encode())
            await writer.drain()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)s  %(message)s",
        filename="chat.log",
    )
    load_dotenv()
    args = get_args()
    asyncio.run(chat_writer(args.host, args.outport))
