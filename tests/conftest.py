import os
import shutil
import pytest

from apps.app import create_app, db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag


@pytest.fixture
def fixture_app():
    # 설정 처리
    # 테스트용의 config를 사용하기 위해서 인수에 testing을 지정한다
    app = create_app('testing')

    # 데이터베이스를 이용하기 위한 선언
    app.app_context().push()

    # 테스트용 데이터베이스의 테이블을 작성
    with app.app_context():
        db.create_all()

    # 테스트용의 이미지 업로드 디렉토리를 작성
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 테스트 실행
    yield app

    # 클린업 처리
    # user 테이블의 레코드를 삭제
    User.query.delete()

    # user_image 테이블의 레코드를 삭제
    UserImage.query.delete()

    # user_image_tags 테이블의 레코드를 삭제
    UserImageTag.query.delete()

    #테스트용의 이미지 업로드 디렉토리 삭제
    shutil.rmtree(app.config['UPLOAD_FOLDER'])

    db.session.commit()

@pytest.fixture
def client(fixture_app):
    #flask의 테스트용 클라이언트 반환
    return fixture_app.test_client()

@pytest.fixture
def app_data():
    return 3