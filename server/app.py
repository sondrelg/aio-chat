from enum import IntEnum

from aiohttp import web, WSMsgType

from logger import logger
from server.usernames import get_username
from utils import FixedLengthList

routes = web.RouteTableDef()
clients = set()


# TODO: Replace with redis
messages = FixedLengthList(max_length=10)


class Sender(IntEnum):
    SELF = 1
    OTHER = 2


@routes.get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        # Generate a random username for new users
        username, request = get_username(request)

        # Maintain a set of clients so we can broadcast
        # messages to everyone when they come in
        if ws not in clients:
            clients.add(ws)

        if msg.type == WSMsgType.TEXT and msg.data == 'close':
            await ws.close()
            break
        if msg.type == WSMsgType.TEXT and msg.data == 'open_connection':
            await ws.send_json(messages)
            continue
        elif msg.type == WSMsgType.CLOSE:
            await ws.close()
            break
        elif msg.type == WSMsgType.ERROR:
            logger.error(f'ws connection closed with exception {ws.exception()}')
            break
        elif msg.type != WSMsgType.TEXT:
            raise ValueError(f'Received unhandled message type: {msg.type}')

        for client in set(clients):

            message = f'{username}: {msg.data}'

            try:
                # Add message to our message history list
                messages.append(message)

                # Send message to all clients
                if client == ws:
                    await client.send_json({'message': message, 'sender': Sender.SELF})
                else:
                    await client.send_json({'message': message, 'sender': Sender.OTHER})
            except ConnectionResetError:
                # This happens when a client has disconnected and we try to send them a message
                logger.debug('Removing disconnected client from set')
                clients.remove(client)

    logger.info('websocket connection closed')
    return ws


app = web.Application()
app.add_routes(routes)
