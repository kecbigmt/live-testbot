import requests, json, re

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from janome.tokenizer import Tokenizer
t = Tokenizer()

app = Flask(__name__)

line_bot_api = LineBotApi("xkIkdXiJirxcL5cMticl4/KB+IUdmHeQVIoP8piCf6rCIZkXxj55VgoIwoAzjOAuHF2FiSd7VHSf8ezUdrhzgJ1pNjUFLaI6RWLEWM11U54CevJYcH8OQHemO0UZGnHDNQsTZCzhURjvobDkb18dkQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("ea93952db0d7dbe1d0a2957f6925b1af")

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    if event.message.text=="天気":
        city_code = 130010
        url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city={}'.format(city_code)
        headers = {"content-type":"application/json"}
        r = requests.get(url, headers=headers)
        data = r.json()
        text = data['description']['text']
    elif event.message.text == "にゃあ":
        text = "わん"
    elif re.match("^http", event.message.text):
        url = 'https://graph.facebook.com/'
        payload = {'id':event.message.text}
        r = requests.get(url, params=payload)
        if r.status_code==requests.codes.ok:
            data = r.json()
            text = "コメント数:{0}\nシェア数:{1}".format(data['share']['comment_count'],data['share']['share_count'])
        else:
            text = r.headers['WWW-Authenticate']
    elif re.match("(僕|私|俺|ぼく|わたし|おれ)は(誰|だれ)", event.message.text):
        profile = line_bot_api.get_profile(event.source.user_id)
        text = "{0}\n{1}\n{2}\n{3}".format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)
    else:
        text = ""
        for token in t.tokenize(event.message.text):
            tmp = token + '\n'
            text += tmp
        #text = event.message.text + "って言ったね"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )

if __name__ == "__main__":
    app.run()
