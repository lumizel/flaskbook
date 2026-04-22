import json
import os
from pathlib import Path
from flask import Flask
from flask_migrate import Migrate

# 1. 파일(모듈)을 'conf_module'이라는 별명으로 가져옵니다.
from api import config as conf_module 
from .models import db
from . import api as api_blueprint

def create_app():
    config_name = os.environ.get("CONFIG", "local")
    app = Flask(__name__)
    
    # 2. 'conf_module'(파일) 안에 있는 'config'(딕셔너리)를 명확하게 지칭합니다.
    # 이렇게 쓰면 절대 모듈과 헷갈리지 않습니다.
    app.config.from_object(conf_module.config[config_name])

    # JSON schema 로딩
    config_json_path = Path(__file__).parent / "config" / "json-schemas"
    if config_json_path.exists():
        for p in config_json_path.glob("*.json"):
            with open(p) as f:
                json_name = p.stem
                schema = json.load(f)
            app.config[json_name] = schema

    db.init_app(app)
    app.register_blueprint(api_blueprint, url_prefix="/v1")
    return app

app = create_app()
Migrate(app, db)