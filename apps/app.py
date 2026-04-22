from pathlib import Path
from flask import Flask, render_template
from apps.crud import views as crud_views
from flask_migrate import Migrate
from apps.database import db, login_manager
from flask_wtf.csrf import CSRFProtect
from apps.config import config
from apps.detector.models import UserImage


# login manager 속성에 미로그인 시 리다이렉트하는 엔드포인트를 지정
login_manager.login_view = "auth.signup"
# login_mwssage 속성에 로그인 후에 표시할 메시지를 지정
# 여기에서는 아무것도 표시하지 않도록 공백으로 지정
login_manager.login_message = ""



csrf = CSRFProtect()

def create_app(config_key):
    # 플라크스 인스턴스 생성
    app = Flask(__name__)
    # config key에 매치하는 환경의 config 클래스를 읽어 들인다
    app.config.from_object(config[config_key])

    # 앱의 config 설정을 한다
    app.config.from_mapping(
        SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",
        SQLALCHEMY_DATABASE_URI=
            f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # SQL을 콘솔 로그에 출력하는 설정
        SQLALCHEMY_ECHO=True,
        WTF_CSRF_SECRET_KEY = 'AuwzyszU5sugKN7KZs6f',
        )
    
    csrf.init_app(app)
    # 커스텀 오류 화면 등록
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # SQLAlchemy와 앱을 연계한다
    db.init_app(app)
    # Migrate와 앱을 연계한다
    Migrate(app, db)
    
    from apps.crud import models

    # crud 패키지로부터 views를 import한다
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # login_manager를 앱과 연계
    login_manager.init_app(app)


    from apps.auth import views as auth_view
    app.register_blueprint(auth_view.auth, url_prefix="/auth")

    # 이제부터 작성하는 detector 패키질로부터 views를 import해야한다
    from apps.detector import views as dt_views

    # register_blueprint를 사용해 views의 dt를 앱에 등록한다
    app.register_blueprint(dt_views.dt)
    return app


def page_not_found(e):
    """404 Not Found"""
    return render_template('404.html'), 404

def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template('500.html'), 500
