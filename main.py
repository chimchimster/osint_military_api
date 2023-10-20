import sys

from uvicorn import Server, config


async def main():

    conf = config.Config(app='app:app', host='0.0.0.0', port=8000, log_level='debug', reload=True)
    server = Server(config=conf)

    try:
        await server.serve()
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())