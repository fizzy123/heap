from heap import app
from .ui import ui_blueprint
from .feed import feed_blueprint
app.register_blueprint(ui_blueprint)
app.register_blueprint(feed_blueprint, url_prefix='/feed')
