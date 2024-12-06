import string
import random

from core import ebenevobot
from data import db_handler

bot = ebenevobot.bot
who_game_db = db_handler.who_game_db
query = db_handler.query

party_mode = True

keywords = {
    "да": "пизда",
    "нет": "пидора ответ",
    "молодец": "соси конец"
}

def clean_message(message):
    # Убираем знаки препинания
    message = message.translate(str.maketrans('', '', string.punctuation))
    # Убираем лишние слова
    words_to_remove = ["чат", "я", "и"]
    for word in words_to_remove:
        message = message.replace(word, "")
    # Убираем лишние пробелы
    message = ' '.join(message.split())
    return message

@bot.message_handler(commands=['party'])
def add_user_to_party(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''  # last_name может быть None

    # Проверка, существует ли пользователь в базе данных
    if not who_game_db.contains(query.user_id == user_id):
        # Если пользователь не существует, добавляем его в базу данных
        who_game_db.insert({'user_id': user_id, 'username': username, 'first_name': first_name, 'last_name': last_name})
        bot.reply_to(message, f"вас будут тегать")
    else:
        bot.reply_to(message, f"уже в списке")

@bot.message_handler(commands=['noparty'])
def add_user_to_party(message):
    user_id = message.from_user.id

    if who_game_db.contains(query.user_id == user_id):
        who_game_db.remove(query.user_id == user_id)
        bot.reply_to(message, f"вас не будут тегать")
    else:
        bot.reply_to(message, f"тебя и так не трогали")

@bot.message_handler(commands=['partyoff'])
def party_off(message):
    party_mode = False
    bot.reply_to(message, f"Режим теганья выключен")    

@bot.message_handler(commands=['partyon'])
def party_on(message):
    party_mode = True
    bot.reply_to(message, f"Режим теганья включен")


def play_who_game(message, text):
    cleaned_message = clean_message(text.lower())
    if cleaned_message in ["кто", "мы"]:
        random_user= random.choice(who_game_db.all())
        if not random_user['username']:
            mention_link = f"tg://user?id={random_user['user_id']}"
            bot.reply_to(message, f"[{random_user['first_name']} {random_user['last_name']}]({mention_link})!"
                                  f"\nЧтобы выйти - /noparty"
                                  f"\nЧтобы играть - /party", parse_mode='Markdown') 
        else:
            bot.reply_to(message, f"@{random_user['username']}"
                                  f"\nЧтобы выйти - /noparty"
                                  f"\nЧтобы играть - /party") 

@bot.message_handler(content_types=['photo'])
def handle_photo_message(message):        
    if not party_mode:
        return

    if not message.caption:
        return
    
    play_who_game(message, message.caption)

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):   
    for keyword, response in keywords.items():
        if keyword == message.text.lower():
            if(keyword == "молодец" and message.from_user.id == 80207393):
                bot.reply_to(message, "спасибо")
            else:
                bot.reply_to(message, response)
            break  # Выходим из цикла после первого совпадения    

    if not party_mode:
            return

    play_who_game(message, message.text)