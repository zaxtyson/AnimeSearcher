from core.config import config
from core.http_client import client
from views import app


@app.listener('before_server_start')
async def init(_, loop):
    await client.init_session(loop)


@app.listener('after_server_stop')
async def finish(_):
    await client.close_session()


if __name__ == '__main__':
    args = config.get_server_args()
    app.run(**args)
