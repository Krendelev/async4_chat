import asyncio
from contextlib import closing
from datetime import datetime

from utils import connect_to_server, get_argparser, save_text


async def chat_reader(host, port, file):
    reader, writer = await connect_to_server(host, port)
    with closing(writer):
        while True:
            data = await reader.readuntil()
            text = data.decode()
            print(text, end="")
            now = datetime.now().strftime("%d.%m.%y %H:%M")
            record = f"[{now}]  {text}"
            await save_text(file, "a", record)


async def main():
    argparser = get_argparser()
    argparser.add_argument("--port", type=int, default=5000, help="port to read from")
    argparser.add_argument(
        "--history", default="chat.history", help="where to save transcript"
    )
    args = argparser.parse_args()

    while True:
        try:
            await chat_reader(args.host, args.port, args.history)
        except asyncio.TimeoutError:
            print(f"Can't connect to {args.host}")
            return
        except asyncio.exceptions.IncompleteReadError:
            print(f"Lost connection to {args.host}. Trying to reconnect...")


if __name__ == "__main__":
    asyncio.run(main())
