import asyncio
from datetime import datetime

import aiofiles

from utils import get_args


async def save_text(text, file):
    async with aiofiles.open(file, "a") as fh:
        now = datetime.now().strftime("%d.%m.%y %H:%M")
        await fh.writelines(f"[{now}]  {text}")


async def chat_reader(host, port, file="chat.history"):
    reader, _ = await asyncio.open_connection(host, port)
    while True:
        data = await reader.readuntil()
        if not data:
            break
        text = data.decode()
        print(text, end="")
        await save_text(text, file)


if __name__ == "__main__":
    args = get_args()
    asyncio.run(chat_reader(args.host, args.inport, args.history))
