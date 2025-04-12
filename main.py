from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# 環境変数から取得（後でRenderで設定）
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def translate_to_english(text):
    url = 'https://api-free.deepl.com/v2/translate'
    data = {
        'auth_key': DEEPL_API_KEY,
        'text': text,
        'target_lang': 'EN'
    }
    response = requests.post(url, data=data)
    return response.json()['translations'][0]['text']

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    original_text = event.message.text
    translated_text = translate_to_english(original_text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=translated_text)
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)        