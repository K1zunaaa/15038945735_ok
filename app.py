import os
import re
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, request,send_from_directory
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import Dial, VoiceResponse

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションを作成
app = Flask(__name__)

# 特殊文字やアンダースコアを除去する正規表現
alphanumeric_only = re.compile("[\W_]+")

# 電話番号の形式を検証するための正規表現
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

# Twilioの電話番号を環境変数から取得
twilio_number = os.environ.get("TWILIO_CALLER_ID")

# 最新のユーザーIDをメモリに保存する辞書
IDENTITY = {"identity": "Admin-Center"}

# ルートURLにアクセスされた際にindex.htmlを返す
@app.route("/")
def index():
    return app.send_static_file("index.html")

# トークンを生成して返すAPIエンドポイント
@app.route("/token", methods=["GET"])
def token():
    # 環境変数からTwilioのアカウント情報を取得
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    application_sid = os.environ["TWILIO_TWIML_APP_SID"]
    api_key = os.environ["API_KEY"]
    api_secret = os.environ["API_SECRET"]

    # ランダムなユーザー名を生成し、記号を削除してIDとして保存
    identity = twilio_number
    IDENTITY["identity"] = identity

    # アクセストークンを生成し、ユーザーIDを設定
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Voice Grantを作成し、トークンに追加（着信許可）
    voice_grant = VoiceGrant(
        outgoing_application_sid=application_sid,
        incoming_allow=True,
    )
    token.add_grant(voice_grant)

    # トークンをJWT形式に変換
    token = token.to_jwt()

    # トークンとユーザーIDをJSON形式で返す
    return jsonify(identity=identity, token=token)

# 音声通話に対応するAPIエンドポイント
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    # 発信先がTwilioの電話番号の場合、着信として処理
    if request.form.get("To") == twilio_number:
        dial = Dial()
        # 最後に生成されたクライアントIDに接続
        dial.client(IDENTITY["identity"])
        resp.append(dial)
    
    # 発信先が指定されている場合、外部に発信する処理
    elif request.form.get("To"):
        dial = Dial(caller_id=twilio_number)
        
        # 電話番号が数字と記号のみで構成されているか確認
        if phone_pattern.match(request.form["To"]):
            dial.number(request.form["To"])
        else:
            dial.client(request.form["To"])
        resp.append(dial)
    
    # 発信先がない場合のメッセージ
    else:
        resp.say("Thanks for calling!")

    # TwiML形式の応答をXMLとして返す
    return Response(str(resp), mimetype="text/xml")

# レポートページの画面・バック側処理
@app.route("/report",methods=["POST","GET"])
def report():
    if request.method == "POST":
        return "レポートを作成しました！（本来はDBに情報格納）"

    if request.method == "GET":
        return send_from_directory('static', 'report.html')

# ログインページの画面・バック側処理
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        return "ログインの処理が走る"
    
    if request.method == "GET":
        return send_from_directory('static', 'login.html')
    
# 新規アカウント登録ページの画面・バック側処理
@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        return "新規アカウントの処理が走る"
    
    if request.method == "GET":
        return send_from_directory('static', 'register.html')

    # アプリケーションを実行
if __name__ == "__main__":
    app.run()
