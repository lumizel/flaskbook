# ============================================
# 표준 라이브러리 import
# 내부 모듈 import
# ============================================
import json  # JSON 데이터 파싱용

from flask import Blueprint, jsonify, request  # Flask API 관련 객체

from . import calculation, preparation  # 비즈니스 로직(계산, 준비 단계)

# JSON 검증용 데코레이터 import
from .json_validate import validate_json, validate_schema

# ============================================
# Blueprint 생성
# ============================================

# api Blueprint 생성
# url_prefix="/v1" → 모든 API 경로는 /v1으로 시작
api = Blueprint("api", __name__, url_prefix="/v1")

# ============================================
# 파일 ID 등록 API
# ============================================


@api.post("/file-id")  # POST /v1/file-id
@validate_json  # 요청 데이터가 JSON인지 확인
@validate_schema("check_dir_name")  # JSON schema 검증 (디렉터리 이름 체크)
def file_id():
    """
    손글씨 이미지가 있는 디렉터리를 받아
    이미지 파일명을 DB 등에 등록하는 API
    """
    return preparation.insert_filenames(request)


# ============================================
# 손글씨 인식 확률 계산 API
# ============================================


@api.post("/probabilities")  # POST /v1/probabilities
@validate_json  # JSON 형식 검증
@validate_schema("check_file_id")  # file_id가 유효한지 검증
def probabilities():
    """
    등록된 file_id를 기준으로
    손글씨 숫자 판별 결과를 계산하는 API
    """
    return calculation.evaluate_probs(request)


# ============================================
# JSON Schema 존재 여부 확인 API
# ============================================


@api.post("/check-schema")  # POST /v1/check-schema

# JSON schema의 유무 체크를 하는 데코레이터
@validate_json

# JSON schema 정의가 있는지 확인하는 데코레이터
@validate_schema("check_file_schema")
def check_schema():
    """
    요청 JSON이 지정된 schema를 만족하는지 테스트하는 API
    (디버깅 / 테스트 목적)
    """

    # 요청 body(JSON)를 파이썬 dict로 변환
    data = json.loads(request.data)

    # JSON 내부 값 출력 (서버 콘솔 확인용)
    print(data["file_id"])
    print(data["file_name"])

    # file_name 값 추출
    d = data["file_name"]

    # 성공 메시지 반환
    return f"Successfully get {d}"


# ============================================
# 공통 에러 핸들러
# ============================================


# 400 (Bad Request), 404 (Not Found), 500 (Server Error)
@api.errorhandler(400)
@api.errorhandler(404)
@api.errorhandler(500)
def error_handler(error):
    """
    API 실행 중 발생하는 오류를
    공통 JSON 형태로 반환
    """

    response = jsonify(
        {
            "error_message": error.description["error_message"],  # 오류 메시지
            "result": error.code,  # HTTP 상태 코드
        }
    )

    return response, error.code