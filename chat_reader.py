import asyncio
from contextlib import closing

from utils import get_args, save_text


async def chat_reader(host, port, file="chat.history"):
    reader, writer = await asyncio.open_connection(host, port)
    with closing(writer):
        while True:
            data = await reader.readuntil()
            if reader.at_eof():
                break
            text = data.decode()
            print(text, end="")
            await save_text(text, file)


if __name__ == "__main__":
    args = get_args()
    asyncio.run(chat_reader(args.host, args.inport, args.history))
