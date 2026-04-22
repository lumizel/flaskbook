import os
from flask import Flask
from api import api
from api.config import config

config_name = os.environ.get('CONFIG', 'local')

app = Flask(__name__)
app.config.from_object(config[config_name])
# 블루프린트를 앱에 등록
app.register_blueprint(api)