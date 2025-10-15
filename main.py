from telebot import TeleBot, types

bot = TeleBot('8089918683:AAGh2C4XUnM-MLZDFVzU5jr4zojSZxUTSgQ')
user_states = {}

print('bot started...)')

@bot.message_handler(commands=['start'])

class UserData:
    def __init__(self):
        self.step = 0
        self.choices = {}

@bot.message_handler(commands=['start'])
def start(msg):
    main_text = (
        "Вас вітає команда Градос Констракшн — надійного забудовника з фокусом на якість і довіру.\n\n"
        "Ми будуємо ЖК «Біла Сакура» у місті Перечин, Закарпатська область.\n"
        "Тут ви можете:\n"
        "• дізнатися більше про ЖК\n"
        "• обрати квартиру\n"
        "• залишити заявку та отримати персональну пропозицію"
    )

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("🔁 Зворотній зв'язок", callback_data="feedback"))
    markup.add(types.InlineKeyboardButton("📞 Контакт менеджера", callback_data="manager"))
    markup.add(types.InlineKeyboardButton("🏙 Детальніше про ЖК", callback_data="about_jk"))

    bot.send_message(msg.chat.id, main_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if user_id not in user_states:
        user_states[user_id] = UserData()
    data = call.data

    if data == "feedback":
        user_states[user_id] = UserData()
        send_question1(call)
    elif data in ["1к", "2к", "3к", "commercial"]:
        user_states[user_id].choices["type"] = data
        send_question2(call)
    elif data == "next2":
        send_question3(call)
    elif data.startswith("q2_"):
        toggle_checklist(user_id, "q2", data[3:])
        send_question2(call, edit=True)
    elif data == "next3":
        send_summary(call)
    elif data.startswith("q3_"):
        toggle_checklist(user_id, "q3", data[3:])
        send_question3(call, edit=True)
    elif data == "restart":
        user_states[user_id] = UserData()
        send_question1(call)
    elif data == "continue":
        bot.send_message(call.message.chat.id, "Як нам звертатися до Вас?")
        user_states[user_id].step = "ask_name"
    elif data == "manager":
        bot.send_message(call.message.chat.id, "Менеджер Герман: +380ХХХ00900ХХ")
    elif data == "about_jk":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🏢 Опис компанії", callback_data="about_company"))
        markup.add(types.InlineKeyboardButton("🏘 Опис ЖК", callback_data="about_complex"))
        markup.add(types.InlineKeyboardButton("Файл презентації", callback_data="presentation"))
        markup.add(types.InlineKeyboardButton("Головне меню", callback_data="main_menu"))
        bot.send_message(call.message.chat.id, "Виберіть:", reply_markup=markup)
    elif data == "main_menu":
        start(call.message)

@bot.message_handler(
    func=lambda m: user_states.get(m.from_user.id, None) and user_states[m.from_user.id].step == "ask_name")
def handle_name(msg):

    user_states[msg.from_user.id].choices["name"] = msg.text
    bot.send_message(msg.chat.id, "Надішліть номер телефону:")
    user_states[msg.from_user.id].step = "ask_phone"

@bot.message_handler(
    func=lambda m: user_states.get(m.from_user.id, None) and user_states[m.from_user.id].step == "ask_phone")
def handle_phone(msg):

    user_states[msg.from_user.id].choices["phone"] = msg.text
    bot.send_message(msg.chat.id, "Дякуємо! Менеджер зателефонує Вам.\nГоловне меню.")
    start(msg)

def send_question1(call):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("1-кімнатна квартира", callback_data="1к"))
    markup.add(types.InlineKeyboardButton("2-кімнатна квартира", callback_data="2к"))
    markup.add(types.InlineKeyboardButton("3-кімнатна квартира", callback_data="3к"))
    markup.add(types.InlineKeyboardButton("Комерційне приміщення", callback_data="commercial"))

    bot.send_message(call.message.chat.id, "Питання 1/3: Оберіть тип нерухомості:", reply_markup=markup)

def send_question2(call, edit=False):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    opts = [
        ("Можливість розтермінування", "installment"),
        ("Програма кредитування 'єОселя'", "credit"),
        ("Якісне оздоблення", "finish"),
    ]
    selected = user_states[user_id].choices.get("q2", set())
    for name, key in opts:
        checked = "✅ " if key in selected else ""
        markup.add(types.InlineKeyboardButton(f"{checked}{name}", callback_data=f"q2_{key}"))
    markup.add(types.InlineKeyboardButton("Перейти далі", callback_data="next2"))
    text = "Питання 2/3: Що ще важливо для Вас при купівлі?"
    if edit:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

def send_question3(call, edit=False):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    opts = [
        ("Дитячий майданчик у дворі", "playground"),
        ("Школа/садок поруч", "school"),
        ("Велика кількість паркомісць", "parking"),
    ]
    selected = user_states[user_id].choices.get("q3", set())
    for name, key in opts:
        checked = "✅ " if key in selected else ""
        markup.add(types.InlineKeyboardButton(f"{checked}{name}", callback_data=f"q3_{key}"))
    markup.add(types.InlineKeyboardButton("Перейти далі", callback_data="next3"))
    text = "Питання 3/3: Яка інфраструктура важлива для Вас?"
    if edit:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

def send_summary(call):
    user_id = call.from_user.id
    data = user_states[user_id].choices
    text = (
        "Опитування завершено!\n"
        "Ви обрали:\n"
        f"- Тип: {data.get('type')}\n"
        f"- Опції: {', '.join(data.get('q2', []))}\n"
        f"- Інфраструктура: {', '.join(data.get('q3', []))}\n"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Продовжити", callback_data="continue"))
    markup.add(types.InlineKeyboardButton("Вибрати знову", callback_data="restart"))
    bot.send_message(call.message.chat.id, text, reply_markup=markup)

def toggle_checklist(user_id, key, value):
    choices = user_states[user_id].choices
    if key not in choices:
        choices[key] = set()
    if value in choices[key]:
        choices[key].remove(value)
    else:
        choices[key].add(value)

bot.polling()