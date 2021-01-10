import os
import json
import re
import sys
import requests
from re import Match
from flask import Flask, abort, request
from jinja2 import Environment, FileSystemLoader, select_autoescape
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ImageMessage, MessageEvent, TextMessage,
                            TextSendMessage, BubbleContainer, TemplateSendMessage, CarouselContainer, CarouselTemplate, CarouselColumn, FlexSendMessage)

app = Flask(__name__)

#ここ他の人に見せたら大変なことになる。
YOUR_CHANNEL_ACCESS_TOKEN = ""
YOUR_CHANNEL_SECRET = ""

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("handle_message:", event)
    text = event.message.text
    mes,y = search(text)
    #ボタンを押して選ぶ感じ
    if (text.startswith('余りもの')) or (text.startswith('あまりもの')) or (text.startswith('残り物')) or (text.startswith('のこりもの')) or (text.startswith('料理')) or (text.startswith('りょうり')):
        mes = ask(text)
        messages = (
            TextSendMessage(text='なにがあまってますか？'),
            mes,
        )

    elif y == 0:
        messages = (
            TextSendMessage(text='{}ならこちらがおすすめです！'.format(text)),
            mes,
            #FlexSendMessage(container_obj)
        )
    else:
        print("kimi")
        mes = ask(text)
        messages = (
            TextSendMessage(text='すみません、わからなかったです。食材名をカタカナやひらがな、漢字にしてみてください。私のおすすめはこちらです。'),
            mes,
        )
        print("kimi2")

    reply_message(event,messages)
def ask(event):
    notes = [CarouselColumn(thumbnail_image_url="https://1.bp.blogspot.com/-qP_6EsaI5sg/XXXOoEKxn7I/AAAAAAABUwg/47xXcIV-bvAbc1cWZT4u9R-_XNGJ5p1aQCLcBGAs/s1600/marukajiri_kyuuri_boy.png",
                            title="きゅうりで一品",
                            text="きゅうりで一品つくりませんか？",
                            actions=[{"type": "uri","label": "サイトURL","uri": "https://recipe.rakuten.co.jp/search/きゅうり/"}]),

             CarouselColumn(thumbnail_image_url="https://1.bp.blogspot.com/-dLi5SjTQD7w/W_UGBPlGt-I/AAAAAAABQUo/N_xuwCPVY0A93YmzQGfsyS_bX7XRI1hmgCLcBGAs/s800/vegetable_cabbage2.png",
                            title="キャベツで一品",
                            text="おぉーっと、ポテンシャルが高いキャベツだ！これを使って何か作れないかな？",
                            actions=[
                                {"type": "uri","label": "サイトURL","uri": "https://recipe.rakuten.co.jp/search/きゃべつ/"}]),

             CarouselColumn(thumbnail_image_url="https://4.bp.blogspot.com/-6Mq74jWtOxM/WKFjCFW3FYI/AAAAAAABBso/1VoQZiuoax0ja_sdNdOStH5KYYUcG4BvQCLcB/s800/golden_egg.png",
                            title="たまごで一品",
                            text="意外と腐らせてしまうたまご！あーもったいない・・・おいしいレシピに交換しようぜ！",
                            actions=[
                                {"type": "uri","label": "サイトURL","uri": "https://recipe.rakuten.co.jp/search/たまご/"}])]

    messages = TemplateSendMessage(
        alt_text='余りもので一品',
        template=CarouselTemplate(columns=notes),
    )

    return messages

#食材名(text)がスプレッドシートがあったらそのURL(url)を取得してtextをかえす関数

def url_get(food):
    url = ""

    headers = {
        'x-rapidapi-host': "",
        'x-rapidapi-key': ""
        }
    #apiでいろいろ取得
    response = requests.request("GET", url, headers=headers)

    json = response.json()
    #print(json)

    #配列でそれぞれ食材名とurlがはいっている。
    h_name=[]
    h_url=[]
    for h in json['result']['small']:
        h_name.append(h['categoryName'])
        h_url.append(h['categoryUrl'])
    #print(h_name)
    #print(h_url)
    
    #以下で名前を検索して帰ってきた値からurlをだす
    if food in h_name:
        food_in = h_name.index(food)
        food_url = h_url[food_in]
    else:
        food_url = "この食べ物は検索できないよ！"

    return food_url


def search(text):
    url = url_get(text)
    x = "この食べ物は検索できないよ！"
    if x is not url:
        y=0

        notes = [CarouselColumn(thumbnail_image_url="https://1.bp.blogspot.com/-TwMp7OGG7vo/VHPgDGneExI/AAAAAAAApOk/DomNzAjFxEg/s800/job_chef_man.png",
                                title="{}で一品！！".format(text),
                                text="{}で一品をつくれちゃいます！".format(text),
                                actions=[{"type": "uri","label": "サイトURL","uri": "{}".format(url)}]),]


        #messages = TemplateSendMessage(
        #    alt_text='{}ならこちらがおすすめです！'.format(text),
        #    template=CarouselTemplate(columns=notes),
        #)
        messages = TemplateSendMessage(
            alt_text='余りもので一品',
            template=CarouselTemplate(columns=notes),
        )
        #messages = TextSendMessage(text='{}ならこちらがおすすめです！'.format(url))
            #FlexSendMessage(container_obj)

    else:
        y=1
        messages = (
            TextSendMessage(text='すみません、わからなかったです。食材名をカタカナやひらがな、漢字にしてみてください。私のおすすめはこちらです。'),
            )
            #FlexSendMessage(container_obj)
    return messages, y
def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages=messages
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
