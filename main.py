from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数からトークンとシークレットを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # LINEからの署名
    signature = request.headers.get('X-Line-Signature')
    # リクエストボディ
    body = request.get_data(as_text=True)

    print("※ Signature:", signature)
    print("※ Request body:", body)

    # 署名検証
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("※ 署名検証エラー")
        abort(400)
    except Exception as e:
        print(f"※ その他エラー: {e}")
        abort(400)

    return 'OK', 200

# メッセージイベント受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_text = f"あなたのメッセージ：{event.message.text}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

