from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# デバッグ用出力（デプロイ後ログに出る）
print("Access Token:", LINE_CHANNEL_ACCESS_TOKEN)
print("Channel Secret:", LINE_CHANNEL_SECRET)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running!", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    print("※ Signature:", signature)
    print("※ Request body:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("※ 署名検証エラー")
        abort(400)
    except Exception as e:
        print(f"※ その他エラー: {e}")
        abort(400)

    return 'OK', 200

import requests  # これもファイルの上のほうに追加しておいてね！

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    # 言語判定（ja なら日本語、en なら英語）
    try:
        detected_lang = detect(user_text)
    except:
        detected_lang = "unknown"

    if detected_lang == "ja":
        target_lang = "EN"
    elif detected_lang == "en":
        target_lang = "JA"
    else:
        # 不明な言語ならそのまま返す
        reply_text = "翻訳できる言語（日本語・英語）ではありません。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return

    # DeepL APIに送信
    headers = {
        "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
    }
    data = {
        "text": user_text,
        "target_lang": target_lang
    }
    response = requests.post("https://api-free.deepl.com/v2/translate", headers=headers, data=data)

    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        reply_text = f"翻訳結果: {translated_text}"
    else:
        reply_text = "翻訳中にエラーが発生しました。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

    # エラーハンドリングと返信
    try:
        translated_text = result["translations"][0]["text"]
    except Exception as e:
        translated_text = "翻訳に失敗しました。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=translated_text)
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
