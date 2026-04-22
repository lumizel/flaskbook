# 베이스 이미지의 지정
FROM python:3.10.7

# apt-get의 version을 갱신하고 SQLite3의 설치
# (OpenCV 실행을 위한 libgl1 패키지를 슬쩍 추가했습니다. 안 넣으면 나중에 에러나요!)
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev libgl1-mesa-glx libglib2.0-0

# 컨테이너 워킹 디렉토리의 지정
WORKDIR /user/src/

# 디렉토리 파일의 복사 (사용자님 요청 경로 그대로 유지)
# 주의: 복사 대상 앞에 /를 붙여야 정확히 해당 위치로 들어갑니다.
COPY ./apps/ /user/src/apps/
COPY ./local.sqlite /user/src/local.sqlite
COPY ./requirements.txt /user/src/requirements.txt
COPY ./model.pt /user/src/model.pt

# pip의 version 갱신
RUN pip install --upgrade pip

# 리눅스용 Pytorch 및 OpenCV 설치
RUN pip install torch torchvision opencv-python

# 필요한 라이브러리를 컨테이너 내의 환경에 설치
RUN pip install -r /user/src/requirements.txt

# 'building...'를 표시하는 처리
RUN echo 'building...'

# 필요한 각 환경 변수를 설정
ENV FLASK_APP "apps.app:Create_app(local)"
ENV IMAGE_URL "/storage/images/"

# 특정 네트워크 포트를 컨테이너가 실행 시에 리슨
EXPOSE 5001

# docker run 실행 시에 실행되는 처리
# 수정사항: CMD와 대괄호 사이는 한 칸 띄워야 하고, 문법상 공백을 분리해야 합니다.
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5001"]