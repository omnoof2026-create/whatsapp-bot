from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "change_this_token")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
GRAPH_API_VERSION = "v23.0"

LOCATION = (
    "📍 موقع تشيك شاك برجر:\n"
    "عدن - البريقة - السوق القديم.\n\n"
    "وتوجد نقطة يومية في مركز بانافع، عند محل جوزال للعبايات."
)

FEMALE_ORDERS = "773847365"
MALE_ORDERS = "782721262"

user_sessions = {}


def get_session(sender):
    if sender not in user_sessions:
        user_sessions[sender] = {
            "step": "main",
            "order": []
        }
    return user_sessions[sender]


def reset_session(sender):
    user_sessions[sender] = {
        "step": "main",
        "order": []
    }


def main_menu():
    return (
        "أهلًا وسهلًا بك في *تشيك شاك برجر* 🍔❤️\n\n"
        "كيف نقدر نخدمك؟\n\n"
        "1️⃣ 🍔 الطلبات\n"
        "2️⃣ 📍 الموقع\n"
        "3️⃣ 🎉 الحفلات والمناسبات\n"
        "4️⃣ 📞 أرقام التواصل\n\n"
        "أرسل رقم الخيار."
    )


def burger_menu():
    return (
        "🍔 *اختر نوع البرجر:*\n\n"
        "1️⃣ 🧀 برجر بالجبن\n"
        "2️⃣ 🍔 برجر بدون جبن\n\n"
        "أرسل رقم الخيار."
    )


def burger_type_menu():
    return (
        "🌶️ *اختر نوع البرجر:*\n\n"
        "1️⃣ 🌶️ سبايسي\n"
        "2️⃣ 😋 عادي\n\n"
        "أرسل رقم الخيار."
    )


def products_menu():
    return (
        "🍔 *تشيك شاك برجر*\n\n"
        "اختر الصنف الذي تريده:\n\n"
        "1️⃣ 🍔 برجر\n"
        "2️⃣ 🌯 فاهيتا\n"
        "3️⃣ 🍗 زنجر\n\n"
        "أرسل رقم الخيار."
    )


def order_summary(sender):
    order = get_session(sender)["order"]

    if not order:
        return "السلة فارغة حاليًا 🛒"

    text = "🧾 *ملخص طلبك:*\n\n"

    for index, item in enumerate(order, 1):
        text += f"{index}️⃣ {item}\n"

    return text


def handle_message(sender, text):
    text = text.strip().lower()
    session = get_session(sender)

    if text in ["0", "الغاء", "إلغاء", "الغاء الطلب", "إلغاء الطلب"]:
        reset_session(sender)
        return "تم إلغاء الطلب وإعادة القائمة الرئيسية 👍\n\n" + main_menu()

    if text in [
        "منيو",
        "menu",
        "القائمة",
        "ابدأ",
        "start",
        "السلام عليكم"
    ]:
        reset_session(sender)
        return main_menu()

    if session["step"] == "main":

        if (
            text == "1"
            or "طلب" in text
            or "اطلب" in text
            or "أريد" in text
        ):
            session["step"] = "products"
            return products_menu()

        if (
            text == "2"
            or "موقع" in text
            or "وين" in text
            or "مكان" in text
        ):
            return LOCATION

        if (
            text == "3"
            or "حفلة" in text
            or "عرس" in text
            or "زواج" in text
            or "مدرسة" in text
        ):
            return (
                "🎉 *طلبات المناسبات والحفلات*\n\n"
                "أكيد 👍\n"
                "نحن متخصصون في طلبيات الأفراح والحفلات "
                "والأعراس والمناسبات والمدارس والطلبات الخاصة.\n\n"
                "للطلب والتنسيق تواصل معنا."
            )

        if (
            text == "4"
            or "رقم" in text
            or "تواصل" in text
        ):
            return (
                "📞 *أرقام التواصل والطلبات:*\n\n"
                f"👩 طلبات البنات: {FEMALE_ORDERS}\n"
                f"👨 طلبات الرجال: {MALE_ORDERS}"
            )

        return main_menu()

    if session["step"] == "products":

        if text == "1" or "برجر" in text:
            session["step"] = "burger_choice"
            return burger_menu()

        if text == "2" or "فاهيتا" in text:
            session["order"].append("🌯 فاهيتا")
            session["step"] = "after_product"

            return (
                "تم اختيار 🌯 *فاهيتا* 👍\n\n"
                + order_summary(sender)
                + "\n\n"
                "1️⃣ ➕ إضافة طلب\n"
                "2️⃣ ✅ متابعة الطلب"
            )

        if text == "3" or "زنجر" in text:
            session["order"].append("🍗 زنجر")
            session["step"] = "after_product"

            return (
                "تم اختيار 🍗 *زنجر* 👍\n\n"
                + order_summary(sender)
                + "\n\n"
                "1️⃣ ➕ إضافة طلب\n"
                "2️⃣ ✅ متابعة الطلب"
            )

        return products_menu()

    if session["step"] == "burger_choice":

        if text == "1" or "جبن" in text:
            session["order"].append("🧀 برجر بالجبن")
            session["step"] = "burger_type"
            return burger_type_menu()

        if text == "2":
            session["order"].append("🍔 برجر بدون جبن")
            session["step"] = "burger_type"
            return burger_type_menu()

        return burger_menu()

    if session["step"] == "burger_type":

        if text == "1" or "سبايسي" in text:
            session["order"][-1] += " — 🌶️ سبايسي"

        elif text == "2" or "عادي" in text:
            session["order"][-1] += " — 😋 عادي"

        else:
            return burger_type_menu()

        session["step"] = "after_product"

        return (
            "تم إضافة الطلب إلى السلة ✅\n\n"
            + order_summary(sender)
            + "\n\n"
            "1️⃣ ➕ إضافة طلب\n"
            "2️⃣ ✅ متابعة الطلب"
        )

    if session["step"] == "after_product":

        if text == "1" or "إضافة" in text:
            session["step"] = "products"
            return products_menu()

        if (
            text == "2"
            or "تأكيد" in text
            or "متابعة" in text
        ):
            session["step"] = "confirm"

            return (
                order_summary(sender)
                + "\n\n"
                "هل تريد تأكيد الطلب؟\n\n"
                "1️⃣ ✅ تأكيد\n"
                "2️⃣ ❌ إلغاء"
            )

        return (
            order_summary(sender)
            + "\n\n"
            "1️⃣ ➕ إضافة طلب\n"
            "2️⃣ ✅ متابعة الطلب"
        )

    if session["step"] == "confirm":

        if text in [
            "1",
            "نعم",
            "تأكيد",
            "تأكيد الطلب"
        ]:
            session["step"] = "customer_name"

            return (
                "ممتاز ❤️\n\n"
                "أرسل اسمك من فضلك لاستكمال الطلب."
            )

        if text == "2":
            reset_session(sender)
            return "تم إلغاء الطلب 🗑️\n\n" + main_menu()

        return (
            "لإتمام الطلب أرسل:\n"
            "1️⃣ ✅ تأكيد\n"
            "2️⃣ ❌ إلغاء"
        )

    if session["step"] == "customer_name":

        session["customer_name"] = text
        session["step"] = "customer_address"

        return (
            "شكرًا لك ❤️\n\n"
            "الآن أرسل *موقع/عنوان التوصيل* 📍"
        )

    if session["step"] == "customer_address":

        session["customer_address"] = text

        order_text = "\n".join(
            f"- {item}"
            for item in session["order"]
        )

        customer_name = session.get(
            "customer_name",
            "غير محدد"
        )

        reset_session(sender)

        return (
            "✅ *تم استلام طلبك بنجاح!*\n\n"
            f"👤 الاسم: {customer_name}\n"
            f"📍 العنوان: {text}\n\n"
            "🍔 *الطلب:*\n"
            f"{order_text}\n\n"
            "سيتواصل معك فريق تشيك شاك برجر "
            "لاستكمال الطلب والتنسيق ❤️\n\n"
            f"📞 طلبات البنات: {FEMALE_ORDERS}\n"
            f"📞 طلبات الرجال: {MALE_ORDERS}"
        )

    return main_menu()


@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json(silent=True) or {}

    try:

        message = (
            data["entry"][0]
            ["changes"][0]
            ["value"]["messages"][0]
        )

        sender = message["from"]

        if message["type"] == "text":

            text = message["text"]["body"]

            reply = handle_message(
                sender,
                text
            )

            send_message(
                sender,
                reply
            )

    except Exception as e:
        print("Error:", e)

    return "OK", 200


def send_message(to, message):

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=20
    )

    print(
        "WhatsApp response:",
        response.status_code,
        response.text
    )


@app.route("/", methods=["GET"])
def home():
    return "Cheek Shack Burger Bot is running!"


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
