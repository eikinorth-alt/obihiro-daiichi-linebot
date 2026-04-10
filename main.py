from flask import Flask, request, abort
import os
import json
import hmac
import hashlib
import base64
import requests as req

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

REPLIES = {
    "診療科一覧": "【診療科一覧】\n総合診療科／消化器内科・内視鏡内科／循環器内科／透析内科／漢方内科／緩和ケア内科／外科・消化器外科／乳腺外科／肛門外科／脳神経外科／整形外科／リハビリテーション科／麻酔科（完全予約制）／歯科・歯科口腔外科（完全予約制）",
    "受付・受診の流れ": "【受診の流れ】\n①正面入口の受付へ\n②保険証・紹介状をご提示\n③診療申込書・問診票を記入\n④受付票を受け取り待合室でお待ちください\n⑤診察後、黄色クリアファイルを会計へ\n⑥自動精算機でお支払い",
    "受付時間・診療時間": "【受付時間】\n■総合診療科：新患8:30〜10:00／再来8:30〜11:00\n■消化器内科：8:30〜11:00\n■外科：8:30〜11:30\n■脳神経外科：8:30〜11:00（月・水は〜10:00）\n■整形外科：毎週水13:00〜17:00\n■麻酔科：月13:00〜15:00、火〜金8:30〜11:00\n■歯科口腔外科：8:30〜11:00（完全予約制）\n土・日・祝は休診",
    "アクセス・駐車場": "【アクセス】\n〒080-0014 北海道帯広市西四条南15丁目17番地3\nJR帯広駅より徒歩約5分\n駐車場：敷地内あり（無料）\nバリアフリー対応",
    "人間ドック・健康診断": "【人間ドック・健康診断】\n各種健康診断・人間ドックを実施しています。\n詳細はお電話またはホームページをご確認ください。\n📞 0155-25-3121",
    "お問い合わせ": "【お問い合わせ】\n📞 代表電話：0155-25-3121\n受付時間：平日8:30〜／土曜8:30〜11:30\n🌐 https://www.zhi.or.jp/d/",
}

KEYWORDS = {
    "診療科": "診療科一覧", "内科": "診療科一覧", "外科": "診療科一覧",
    "整形": "診療科一覧", "歯科": "診療科一覧", "透析": "診療科一覧",
    "受付": "受付・受診の流れ", "受診": "受付・受診の流れ", "流れ": "受付・受診の流れ",
    "時間": "受付時間・診療時間", "何時": "受付時間・診療時間", "休診": "受付時間・診療時間",
    "アクセス": "アクセス・駐車場", "駐車": "アクセス・駐車場", "住所": "アクセス・駐車場",
    "健診": "人間ドック・健康診断", "ドック": "人間ドック・健康診断", "検診": "人間ドック・健康診断",
    "電話": "お問い合わせ", "問い合わせ": "お問い合わせ",
}

def verify_signature(body, signature):
    hash = hmac.new(
        CHANNEL_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode("utf-8") == signature

def reply_message(reply_token, text):
    req.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
        },
        json={
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": text}]
        }
    )

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    if not verify_signature(body, signature):
        abort(400)

    events = json.loads(body).get("events", [])
    for event in events:
        if event.get("type") != "message":
            continue
        if event.get("message", {}).get("type") != "text":
            continue

        text = event["message"]["text"].strip()
        reply_token = event["replyToken"]

        matched = None
        for kw, key in KEYWORDS.items():
            if kw in text:
                matched = key
                break

        if matched:
            reply_message(reply_token, REPLIES[matched])
        else:
            reply_message(
                reply_token,
                "ご連絡ありがとうございます。\n下のメニューからお選びいただくか、お電話にてお問い合わせください。\n📞 0155-25-3121"
            )

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)app.run(host="0.0.0.0", port=port)
