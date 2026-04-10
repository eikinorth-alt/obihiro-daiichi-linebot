from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, PostbackAction,
    PostbackEvent, FlexSendMessage
)
import os
import json

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

# メニュー返信の内容
REPLIES = {
    "診療科一覧": "【診療科一覧】\n総合診療科／消化器内科／循環器内科／透析内科／緩和ケア科／外科／麻酔科/整形外科／歯科・歯科口腔外科",
    "受付・受診の流れ": "【受診の流れ】\n①正面入口の受付へ\n②保険証・紹介状をご提示\n③診療申込書・問診票を記入\n④受付票を受け取り待合室でお待ちください\n⑤診察後、黄色クリアファイルを会計へ\n⑥自動精算機でお支払い",
    "受付時間・診療時間": "【受付時間】\n■総合診療科：新患8:30〜10:00／再来8:30〜11:00\n■消化器内科：8:30〜11:00\n■外科：8:30〜11:30\n■整形外科：毎週水13:00〜17:00\n■麻酔科：月13:00〜15:00、火〜金8:30〜11:00\n■歯科口腔外科：8:30〜11:00（完全予約制）\n土・日・祝は休診",
    "アクセス・駐車場": "【アクセス】\n〒080-0014 北海道帯広市西四条南15丁目17番地3\nJR帯広駅より徒歩約5分\n駐車場：敷地内あり（無料）\nバリアフリー対応",
    "人間ドック・健康診断": "【人間ドック・健康診断】\n各種健康診断・人間ドックを実施しています。\n詳細はお電話またはホームページをご確認ください。\n📞 0155-25-3121",
    "お問い合わせ": "【お問い合わせ】\n📞 代表電話：0155-25-3121\n受付時間：平日8:30〜／土曜8:30〜11:30\n🌐 https://www.zhi.or.jp/d/",
}

# キーワード→メニューキーのマッピング
KEYWORDS = {
    "診療科": "診療科一覧", "内科": "診療科一覧", "外科": "診療科一覧",
    "整形": "診療科一覧", "歯科": "診療科一覧", "透析": "診療科一覧",
    "受付": "受付・受診の流れ", "受診": "受付・受診の流れ", "流れ": "受付・受診の流れ",
    "時間": "受付時間・診療時間", "何時": "受付時間・診療時間", "休診": "受付時間・診療時間",
    "アクセス": "アクセス・駐車場", "駐車": "アクセス・駐車場", "住所": "アクセス・駐車場",
    "健診": "人間ドック・健康診断", "ドック": "人間ドック・健康診断", "検診": "人間ドック・健康診断",
    "電話": "お問い合わせ", "問い合わせ": "お問い合わせ",
}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    # キーワード一致チェック
    reply = None
    for kw, key in KEYWORDS.items():
        if kw in text:
            reply = REPLIES[key]
            break

    if reply:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    else:
        # デフォルト返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="ご連絡ありがとうございます。\n下のメニューからお選びいただくか、お電話にてお問い合わせください。\n📞 0155-25-3121"
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)