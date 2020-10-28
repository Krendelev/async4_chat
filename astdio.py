import asyncio
import os
import sys


async def astdio():
    loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader(loop=loop)
    reader_protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    # we don't want to close stdout when we're done
    temp_out = os.dup(sys.stdout.fileno())

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        asyncio.Protocol, os.fdopen(temp_out, "wb")
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)

    return reader, writer


async def ainput(prompt=None):
    reader, writer = await astdio()
    if prompt:
        writer.write(prompt.encode())
    data = await reader.readuntil()
    writer.close()
    return data.decode().strip()
