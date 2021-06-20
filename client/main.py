import asyncio
from dataclasses import dataclass

import aioconsole as aioconsole
import aiohttp
import orjson as orjson
from aiohttp import WSMsgType
from rich.console import Console

from client.render import render_messages
from logger import logger
from server.app import Sender
from utils import FixedLengthList

console = Console()

INPUT_VALUE = '> '


@dataclass
class WsResponse:
    message: str
    sender: Sender


async def get_chat_history(ws) -> FixedLengthList:
    """
    Return the channel's message history.
    """
    await ws.send_str('open_connection')
    msgs = FixedLengthList(orjson.loads(await ws.receive_str()), max_length=10)
    return msgs


async def write(ws) -> None:
    """
    Listen for console inputs.
    """
    while True:
        msg = await aioconsole.ainput(INPUT_VALUE)
        if msg:
            await ws.send_str(msg)
        else:
            # anscii code for cursor up
            # nullifies the default behavior of just pressing enter
            print('\x1b[1A' * 2)


async def read(ws, messages) -> None:
    """
    Listen for messages and re-render when content changes.
    """
    async for msg in ws:
        if msg.type == WSMsgType.CLOSED or msg.type == WSMsgType.ERROR:
            logger.info('Websocket closed')
            break
        elif msg.type == WSMsgType.TEXT and msg.data == 'close cmd':
            logger.info('Received message to close cmd')
            await ws.close()
            break
        elif msg.type != WSMsgType.TEXT:
            raise ValueError(f'Received unhandled message type: {msg.type}')

        # Handle regular messages here
        response = WsResponse(**orjson.loads(msg.data))
        messages.append(response.message)
        console.print(render_messages(messages), INPUT_VALUE, end='')


async def main():
    async with aiohttp.ClientSession().ws_connect('http://localhost:8080/ws') as ws:
        # Print the chat history to the terminal when we start-up
        messages = await get_chat_history(ws)
        console.print(render_messages(messages))

        t1 = asyncio.create_task(read(ws, messages))
        t2 = asyncio.create_task(write(ws))
        await asyncio.gather(t1, t2)
