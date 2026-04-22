# **이미지 전처리 흐름(그레이스케일 → 크롭 → 8×8 → 16계조 → 벡터화)**
# ============================================
# 라이브러리 import
# ============================================

from pathlib import Path  # 파일/디렉터리 경로 처리

import numpy as np  # 수치 계산 및 배열 처리
from flask import current_app  # Flask 설정(config) 접근
from PIL import Image  # 이미지 파일 처리

# ============================================
# 이미지 → 그레이스케일 변환
# ============================================


def get_grayscale(filenames: list[str]):
    """
    손글씨 문자 이미지 파일을 하나씩 읽어서
    그레이스케일(L 모드) 이미지로 변환하여 반환하는 제너레이터 함수
    """

    # Flask 설정에서 이미지가 저장된 디렉터리 이름 가져오기
    dir_name = current_app.config["DIR_NAME"]

    # 현재 파일 위치 기준으로 이미지 디렉터리 경로 생성
    dir_path = Path(__file__).resolve().parent.parent / dir_name

    # 파일명 리스트를 순회하며 하나씩 이미지 처리
    for filename in filenames:
        # 이미지 파일 열기 → 흑백(그레이스케일) 변환
        img = Image.open(dir_path / filename).convert("L")

        # yield를 사용하여 이미지 하나씩 반환
        yield img


# ============================================
# 이미지 축소 및 명암 정규화 (8x8, 16계조)
# ============================================


def shrink_image(
    img, offset=5, crop_size: int = 8, pixel_size: int = 255, max_size: int = 16
):
    """
    입력 이미지를 다음 단계로 전처리하는 함수

    1) 숫자가 있는 영역만 추출(crop)
    2) 8x8 픽셀로 리사이즈
    3) 색상 반전 (흰 배경 → 검은 배경)
    4) 명암값을 0~16 범위로 정규화
    """

    # PIL 이미지를 numpy 배열로 변환
    img_array = np.asarray(img)

    # 픽셀 값이 255(완전 흰색)가 아닌 영역 찾기 (가로)
    h_indxis = np.where(img_array.min(axis=0) < 255)

    # 픽셀 값이 255가 아닌 영역 찾기 (세로)
    v_indxis = np.where(img_array.min(axis=1) < 255)

    # 숫자가 존재하는 최소/최대 좌표
    h_min, h_max = h_indxis[0].min(), h_indxis[0].max()
    v_min, v_max = v_indxis[0].min(), v_indxis[0].max()

    # 숫자 영역의 가로/세로 길이
    width, hight = h_max - h_min, v_max - v_min

    # ============================================
    # 가로/세로 비율에 따라 crop 영역 계산
    # ============================================

    if width > hight:
        # 가로가 더 긴 경우
        center = (v_max + v_min) // 2
        left = h_min - offset
        upper = (center - width // 2) - 1 - offset
        right = h_max + offset
        lower = (center + width // 2) + offset
    else:
        # 세로가 더 긴 경우
        center = (h_max + h_min + 1) // 2
        left = (center - hight // 2) - 1 - offset
        upper = v_min - offset
        right = (center + hight // 2) + offset
        lower = v_max + offset

    # ============================================
    # 이미지 crop 및 8x8 리사이즈
    # ============================================

    img_croped = img.crop((left, upper, right, lower)).resize((crop_size, crop_size))

    # 색상 반전 (배경 흰색 → 숫자 밝게)
    img_data256 = pixel_size - np.asarray(img_croped)

    # ============================================
    # 명암값 정규화 (0~16)
    # ============================================

    min_bright, max_bright = img_data256.min(), img_data256.max()

    img_data16 = (img_data256 - min_bright) / (max_bright - min_bright) * max_size

    return img_data16  # (8, 8) 형태의 numpy 배열 반환


# ============================================
# 모델 입력용 데이터 생성
# ============================================


def get_shrinked_img(filenames: list[str]):
    """
    여러 개의 손글씨 이미지를
    모델 입력용 (N, 64) numpy 배열로 변환하는 함수
    """

    # 빈 테스트 데이터 배열 생성
    img_test = np.empty((0, 64))

    # 그레이스케일 이미지 하나씩 처리
    for img in get_grayscale(filenames):
        # 이미지 축소 및 정규화
        img_data16 = shrink_image(img)

        # (8, 8) → (1, 64) 형태로 변환하여 누적
        img_test = np.r_[img_test, img_data16.astype(np.uint8).reshape(1, -1)]

    return img_test  # 최종 모델 입력 데이터 반환