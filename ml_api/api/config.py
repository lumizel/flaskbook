import os
from pathlib import Path

basedir = Path(__file__).parent.parent.parent

class LocalConfig:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'images.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INCLUDED_EXTENTION = [".png", ".jpg"]
    DIR_NAME = "handwriting_pics"

# 이 딕셔너리의 이름이 'config'여야 위에서 conf_module.config로 부를 수 있습니다.
config = {
    "local": LocalConfig,
}