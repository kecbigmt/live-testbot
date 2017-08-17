import requests, json, re, os

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    MessageTemplateAction,
    URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

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
        content = TextSendMessage(text=text)
    elif event.message.text == "にゃあ":
        text = "わん"
        content = TextSendMessage(text=text)
    elif event.message.text == "カルーセル":
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URITemplateAction(
                    label='Go to line.me', uri='https://line.me'),
                PostbackTemplateAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackTemplateAction(
                    label='ping with text', data='ping',
                    text='ping'),
                MessageTemplateAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=carousel_template)
        content = template_message
    elif re.match("^http", event.message.text):
        url = 'https://graph.facebook.com/'
        payload = {'id':event.message.text}
        r = requests.get(url, params=payload)
        if r.status_code==requests.codes.ok:
            data = r.json()
            text = "コメント数:{0}\nシェア数:{1}".format(data['share']['comment_count'],data['share']['share_count'])
        else:
            text = r.headers['WWW-Authenticate']
        content = TextSendMessage(text=text)
    elif re.match("(僕|私|俺|ぼく|わたし|おれ)は(誰|だれ)", event.message.text):
        profile = line_bot_api.get_profile(event.source.user_id)
        text = "{0}\n{1}\n{2}\n{3}".format(profile.display_name, profile.user_id, profile.picture_url, profile.status_message)
        content = TextSendMessage(text=text)
    else:
        text = event.message.text + "って言ったね"
        content = TextSendMessage(text=text)
    line_bot_api.reply_message(
        event.reply_token,
        content
    )

if __name__ == "__main__":
    app.run()
