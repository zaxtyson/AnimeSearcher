from core.cache import clear_expired_keys
from core.config import config
from core.http_client import client
from utils.log import logger
from utils.ws_handler import ws_log_handler
from views import app

app.add_task(clear_expired_keys)


@app.listener('before_server_start')
async def init(_, loop):
    await client.init_session(loop)
    logger.addHandler(ws_log_handler)


@app.listener('after_server_stop')
async def finish(_):
    await client.close_session()


if __name__ == '__main__':
    args = config.get_server_args()
    app.run(**args)
