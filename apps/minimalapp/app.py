import logging
import os

from flask import Flask, render_template, url_for, current_app, g, request, redirect,flash, make_response, session
from email_validator import validate_email, EmailNotValidError
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = '2AZSMss3P5QPbcY2hBsJ'
# 로그 레벨을 설정
app.logger.setLevel(logging.DEBUG)
# 리다이렉트를 중단하지 않도록
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# DebugToolbarExtension 애플리케이션 설정
toolbar = DebugToolbarExtension(app)

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail 확장을 등록한다
mail = Mail(app)


@app.route("/")
def index():
    return "Hello, Flaskbook!"

# 'name'으로 통일하는 경우
@app.route("/hello/<name>", 
           endpoint="hello-endpoint", 
           methods=['GET', 'POST'])
def hello(name): 
    return f"Hello, {name}!"

# flask2부터는 @app.get('/hello'), @app.post('/hello')라고 기술하는 것이 가능
#  @app.get('/hello')
# @app.post('/hello')
# def hello():
#   return 'hello, world'

@app.route('/name/<name>')
def show_name(name):
    # 변수를 템플릿 엔진에게 건냄
    return render_template('index.html', name=name)

with app.test_request_context():
    print(url_for('index'))
    print(url_for('hello-endpoint', name='world'))
    print(url_for('show_name', name='ak',page='1'))

ctx = app.app_context()
ctx.push()

print(current_app.name)
# >> app.minimalapp.app

# 전역 임시 영역에 값을 설정한다
g.connection = 'connection'
print(g.connection)

with app.test_request_context("/users?updated=true"):
    # true가 출력
    print(request.args.get('updated'))


@app.route("/contact")
def contact():
    # 응답 객체 취득
    response = make_response(render_template('contact.html'))
    # 쿠키 설정
    response.set_cookie('flaskbok key', 'flaskbook value')

    # 세션 설정
    session['username'] = 'ymy'
    return response

@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # 폼 데이터 가져오기
        username = request.form['username']
        email = request.form['email']
        description = request.form['description']

        # 입력 체크
        is_valid = True

        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False

        if not email:
            flash("메일 주소는 필수입니다")
            is_valid = False
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                flash("메일 주소의 형식으로 입력해 주세요")
                is_valid = False

        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False

        # 검증 실패 시 contact 페이지로 다시 보냄
        if not is_valid:
            return redirect(url_for("contact"))
        
        # 검증 통과 시 성공 메시지 세팅 후 리다이렉트
        flash('문의를 해주셔서 감사합니다.')
        return redirect(url_for("contact_complete"))
    
            # 이메일을 보낸다
        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username,
            description=description,
            )
    # GET 요청 시(리다이렉트 된 후) 완료 페이지 렌더링
    return render_template("contact_complete.html")

def send_email(to, subject, template, **kwargs):
    """메일을 송신하는 함수"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
