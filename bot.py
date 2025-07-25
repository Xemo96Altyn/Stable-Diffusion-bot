import telebot
import requests
import json
import io
import base64
from PIL import Image
from telebot import types

bot = telebot.TeleBot("##############################")

userStep = {}
userPrompt = {}
userNegPrompt = {}
userSteps = {}
userCheckpoint = {}
userWidth = {}
userHeight = {}
userSeed = {}
userHires = {}
userResult = {}
userImg = {}
userDenoise = {}
userMode = {}
info_dict = None

@bot.message_handler(commands=["старт"])  # создаем команду
def start(message):
    try:       
        if message.chat.id not in userHeight:
            userWidth[message.chat.id] = 512
            userHeight[message.chat.id] = 512
        if message.chat.id not in userSeed:
            userSeed[message.chat.id] = -1
        if message.chat.id not in userDenoise:
            userDenoise[message.chat.id] = 0.75

        userStep[message.chat.id] = "стартовое сообщение"
        userMode[message.chat.id] = "txt2img"
        file = open("users.txt", "r+")
        fileread = file.readlines()
        fileread = [str[:-1] for str in fileread]
        if (str(message.chat.id) in fileread) == False:
            file.write(str(message.chat.id) + "\n")
        file.close()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать")
        btn2 = types.KeyboardButton("Разрешение")
        btn3 = types.KeyboardButton("Сид")
        btn4 = types.KeyboardButton("Деноиз")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(
            message.chat.id,
            f"привет {message.from_user.first_name}, я умею генерировать приколы. выбери формат (для img2img отправь изображение):", reply_markup=markup)
    except Exception as e:
        bug_report(message, e, "start()")
        start(message)

@bot.message_handler(
    func=lambda message: message.chat.id == 796658653
    and message.text.find("ообщение всем") != -1
)
def admin(message):
    file = open("users.txt", "r+")
    fileread = file.readlines()
    fileread = [str[:-1] for str in fileread]
    text = message.text[15:]
    for i in fileread:
        bot.send_message(i, text)
    file.close()

@bot.message_handler(commands=["лоры"])
def loras(message):
    bot.send_message(message.chat.id, '''доступные лоры:

##############
##############
##############
##############
##############
##############

лоры можно вставлять в любое место запроса''', parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id not in userStep)
def default_handler(message):
    start(message)


@bot.message_handler(content_types=["photo"])
def img2img(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("img2img")
        btn2 = types.KeyboardButton("CLIP")
        btn3 = types.KeyboardButton("QR")
        markup.add(btn1, btn2, btn3)
        userStep[message.chat.id] = "фото"
        userWidth[message.chat.id] = message.photo[-1].width
        userHeight[message.chat.id] = message.photo[-1].height
        userImg[message.chat.id] = base64.b64encode(
            bot.download_file(bot.get_file(message.photo[-3].file_id).file_path)
        ).decode("utf-8")
        bot.send_message(message.chat.id, "что хочешь сделать?", reply_markup=markup)
    except Exception as e:
        bug_report(message, e, "img2img()")
        start(message)


@bot.message_handler(func=lambda message: userStep[message.chat.id] == "фото")
def img2img2(message):
    try:
        if message.text == "CLIP":
            userWidth[message.chat.id] = 512
            userHeight[message.chat.id] = 512
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "думаю...", reply_markup=markup)
            clip_payload = {"image": userImg[message.chat.id], "model": "clip"}
            response = requests.post(
                url="http://127.0.0.1:7860/sdapi/v1/interrogate", json=clip_payload
            )
            r = response.json()
            userResult[message.chat.id] = r["caption"]
            bot.send_message(
                796658653, f"{message.from_user.first_name} запросил это:"
            )
            bot.send_message(796658653, userResult[message.chat.id])
            bot.send_message(
                message.chat.id,
                f"описание фотографии от нейронки (пробую угадать что изображено и стиль): {userResult[message.chat.id]}",
            )
            start(message)
        elif message.text == "QR":
            userMode[message.chat.id] = "QR"
            bot.send_message(message.chat.id, "сделаю твой куар код красивым по твоему промпту (читабельный может получиться не с первого раза, рекомендую НЕ использовать встроенный в телефон - он говно). хороший сайт для создания картинки для бота - https://qrcode.antfu.me")
            askCheckpoint(message)
        else:
            userMode[message.chat.id] = "img2img"
            askCheckpoint(message)
    except Exception as e:
        bug_report(message, e, "img2img2()")
        start(message)



@bot.message_handler(
    func=lambda message: userStep[message.chat.id] == "стартовое сообщение"
    and message.text == "Начать"
)
def askCheckpoint(message):
    try:
        markup = types.ReplyKeyboardRemove()
        userStep[message.chat.id] = "выбор чекпоинта"
        keyboard = [
            [
                types.InlineKeyboardButton(text="1", callback_data="1"),
                types.InlineKeyboardButton(text="2", callback_data="2"),
                types.InlineKeyboardButton(text="3", callback_data="3"),
            ],
            [
                types.InlineKeyboardButton(text="4", callback_data="4"),
                types.InlineKeyboardButton(text="5", callback_data="5"),
                types.InlineKeyboardButton(text="6", callback_data="6"),
            ]
        ]
        markup = types.InlineKeyboardMarkup(keyboard)
        bot.send_message(message.chat.id, """выбери чекпоинт:
        1. Реализм (люди)
        2. Реализм (объекты)

    они все умеют делать не только людей, но и любые другие объекты в том числе, но лучше всего будет выходить именно то, на чем основан датасет
    для просмотра лор: /лоры""", reply_markup=markup)
    except Exception as e:
        bug_report(message, e, "askCheckpoint()")
        start(message)


@bot.message_handler(
    func=lambda message: userStep[message.chat.id] == "стартовое сообщение"
    and message.text == "Деноиз"
)
def denoise(message):
    userStep[message.chat.id] = "деноиз"
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "Denoising Strength отвечает за то, насколько сильно исходное изображение будет изменено (работает только при img2img). значения: от 0 до 1, где 0 - изображение никак не поменяется (по стандарту стоит 0.75):",
        reply_markup=markup,
    )
    bot.send_message(message.chat.id, f"текущее значение: {userDenoise[message.chat.id]}")

@bot.message_handler(func=lambda message: userStep[message.chat.id] == "деноиз")
def denoise2(message):
    try:
        userDenoise[message.chat.id] = float(message.text)
        bot.send_message(message.chat.id, "сохранено")
        start(message)
    except:
        bot.send_message(message.chat.id, "ты чет не то написал")
        start(message)

@bot.message_handler(
    func=lambda message: userStep[message.chat.id] == "стартовое сообщение"
    and message.text == "Сид"
)
def seed(message):
    userStep[message.chat.id] = "выбор сида"
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "сид работает также, как и в майне - один запрос с одним сидом будут выдавать всегда тот же результат. можно использовать если понравилось вся картинка, но рука не в том месте, или хочется поправить что-то определенное. сид всегда положителен, либо -1, если хотите использовать случайный. напиши сид для генерации:",
        reply_markup=markup,
    )
    bot.send_message(message.chat.id, f"текущее значение: {userSeed[message.chat.id]}")


@bot.message_handler(func=lambda message: userStep[message.chat.id] == "выбор сида")
def seed2(message):
    try:
        userSeed[message.chat.id] = int(message.text)
        bot.send_message(message.chat.id, "сид сохранен")
        start(message)
    except:
        bot.send_message(
            message.chat.id,
            "сид должен быть любым положительным числом, либо -1 для случайного",
        )


@bot.message_handler(
    func=lambda message: userStep[message.chat.id] == "стартовое сообщение"
    and message.text == "Разрешение"
)
def res(message):
    userStep[message.chat.id] = "выбор разрешения"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Стандартное")
    btn2 = types.KeyboardButton("Вертикальное")
    btn3 = types.KeyboardButton("Горизонтальное")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        "выбери разрешение картинки:",
        reply_markup=markup,
    )
    bot.send_message(message.chat.id, f"текущее значение: {userWidth[message.chat.id]}x{userHeight[message.chat.id]}")


@bot.message_handler(
    func=lambda message: userStep[message.chat.id] == "выбор разрешения"
)
def res2(message):
    if message.text == "Стандартное":
        userWidth[message.chat.id] = 512
        userHeight[message.chat.id] = 512
        bot.send_message(message.chat.id, "разрешение сохранено")
        start(message)
    elif message.text == "Вертикальное":
        userWidth[message.chat.id] = 512
        userHeight[message.chat.id] = 768
        bot.send_message(message.chat.id, "разрешение сохранено")
        start(message)
    elif message.text == "Горизонтальное":
        userWidth[message.chat.id] = 768
        userHeight[message.chat.id] = 512
        bot.send_message(message.chat.id, "разрешение сохранено")
        start(message)


@bot.callback_query_handler(func=lambda call: userStep[call.message.chat.id] == "выбор чекпоинта")
def requestPrompt(call):
    try:
        userStep[call.message.chat.id] = "запрос промпта"

        if call.data == "1":
            userCheckpoint[call.message.chat.id] = "photon_v1.safetensors [ec41bd2a82]"
        elif call.data == "2":
            userCheckpoint[call.message.chat.id] = "realisticVisionV51_v51VAE.safetensors [15012c538f]"

        markup = types.ReplyKeyboardRemove()
        bot.send_message(
            call.message.chat.id,
            "пришли запрос на генерацию (на английском):",
            reply_markup=markup,
        )
    except Exception as e:
        bug_report(call.message, e, "requestPrompt()")
        start(call.message)


@bot.message_handler(func=lambda message: userStep[message.chat.id] == "запрос промпта")
def requestNeg(message):
    userStep[message.chat.id] = "запрос нег промпта"
    userPrompt[message.chat.id] = message.text
    bot.send_message(
        message.chat.id,
        "укажи негативный запрос (то, чего на картинке ты НЕ хочешь видеть):",
    )


@bot.message_handler(func=lambda message: userStep[message.chat.id] == "запрос нег промпта")
def requestSteps(message):
    userStep[message.chat.id] = "запрос шагов"
    userNegPrompt[message.chat.id] = message.text
    bot.send_message(message.chat.id, "теперь укажи количество шагов (до 50):")

@bot.message_handler(func=lambda message: userStep[message.chat.id] == "запрос шагов")
def generation(message):
    try:
        userStep[message.chat.id] = "генерация"
        try:
            userSteps[message.chat.id] = int(message.text)
        except:
            pass
        if userSteps[message.chat.id] > 50:
            bot.send_message(message.chat.id, "сказано же для дураков")
            start(message)
        
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "генерирую приколы...", reply_markup=markup)
        payload = {
            "prompt": userPrompt[message.chat.id],
            "steps": userSteps[message.chat.id],
            "negative_prompt": ("FastNegativeV2,  aid291, extra fingers, blurry face, extra limbs, lowres, bad anatomy, " + userNegPrompt[message.chat.id]),
            "sampler_name": "Euler a",
            "width": userWidth[message.chat.id],
            "height": userHeight[message.chat.id],
            "seed": userSeed[message.chat.id],
            "denoising_strength": userDenoise[message.chat.id],
            "enable_hr": True,
            "hr_upscaler": "R-ESRGAN 4x+",
        }

        override_settings = {
            "sd_model_checkpoint": userCheckpoint[message.chat.id],
            "CLIP_stop_at_last_layers": 2,
        }
        payload["override_settings"] = override_settings 
        
        if userMode[message.chat.id] == "img2img":
            payload["init_images"] = [userImg[message.chat.id]]
            payload["script_name"] = "SD upscale"
            payload["script_args"] = [None, 64, 5, 1]
            response = requests.post(
                url="http://127.0.0.1:7860/sdapi/v1/img2img", json=payload
            )
        elif userMode[message.chat.id] == "QR":
            payload["alwayson_scripts"] = {
                "controlnet": {
                    "args": [
                        {
                            "input_image": userImg[message.chat.id],
                            "model": "QRPattern_v2_9500 [2d8d5750]",
                            "weight": 0.55,
                            "guidance_end": 0.7
                        }
                    ]
                }
            }
            response = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        else:
            response = requests.post(
                url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload
            )
        r = response.json()
        info_dict = json.loads(r["info"])
        userResult[message.chat.id] = Image.open(
            io.BytesIO(base64.b64decode(r["images"][0]))
        )

        bot.send_message(
            796658653, "{0.first_name} запросил это:".format(message.from_user)
        )
        bot.send_message(796658653, userMode[message.chat.id])
        bot.send_message(796658653, userCheckpoint[message.chat.id])
        bot.send_message(796658653, userPrompt[message.chat.id])
        bot.send_photo(796658653, userResult[message.chat.id])
        bot.send_message(
            message.chat.id,
            f"""{userMode[message.chat.id]}
Запрос: `{userPrompt[message.chat.id]}`
Отрицательный запрос: `{userNegPrompt[message.chat.id]}`
Шаги: `{userSteps[message.chat.id]}`
Сид: `{info_dict["seed"]}`""", parse_mode="Markdown")
        bot.send_photo(message.chat.id, userResult[message.chat.id])
        regen(message)
    except Exception as e:
        bug_report(message, e, "generation()")
        start(message)

def regen(message):
    userStep[message.chat.id] = "запрос повтора генерации"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)
    bot.send_message(
        message.chat.id,
        "сгенерировать заново (используя те же параметры)?",
        reply_markup=markup,
    )

@bot.message_handler(func=lambda message: userStep[message.chat.id] == "запрос повтора генерации")
def regen2(message):
    if message.text in ["Да", "да"]:
        generation(message)
    else:
        start(message)

def bug_report(message, e, where):
    bot.send_message(message.chat.id, f"ошибка: {e}, *уже отправил репорт игорю*", parse_mode="Markdown")
    bot.send_message(796658653, f'''У {message.from_user.first_name} ошибка: {e} *в {where}*''', parse_mode="Markdown")
    
    bot.send_message(796658653, f"{userMode[message.chat.id]}", parse_mode="Markdown")
    if userCheckpoint[message.chat.id]:
        bot.send_message(796658653, f"Чекпоинт: `{userCheckpoint[message.chat.id]}`", parse_mode="Markdown")
    else:
        bot.send_message(796658653, "чекпоинта нет")

    if userPrompt[message.chat.id]:
        bot.send_message(796658653, f"промпт: `{userPrompt[message.chat.id]}`", parse_mode="Markdown")
    else:
        bot.send_message(796658653, "промпта нет")

    if userNegPrompt[message.chat.id]:
        bot.send_message(796658653, f"негпромпт: `{userNegPrompt[message.chat.id]}`", parse_mode="Markdown")
    else:
        bot.send_message(796658653, "негпромпта нет")
    
    try:
        bot.send_message(796658653, f"ответ SD: {info_dict}")
    except:
        bot.send_message(796658653, "ответа SD нет")

@bot.message_handler(commands=["secret"])
def secret(message):
    bot.send_photo(
        message.chat.id,
        "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Peter_Griffin.png/220px-Peter_Griffin.png",
    )


bot.polling(none_stop=True)
