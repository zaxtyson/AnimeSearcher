from api.router import *
from web.views import storage, statistic

app.register_blueprint(storage.mod)
app.register_blueprint(statistic.mod)
