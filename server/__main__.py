from aiohttp import web

from server.app import app

if __name__ == '__main__':
    web.run_app(app)
