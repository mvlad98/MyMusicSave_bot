import telebot
import configparser
from Hadler import Handler



#Get conf.ini
conf = configparser.ConfigParser()
conf.read('conf.ini')

#Telegram token and bot configuraton
token=conf.get('Token','token')
bot=telebot.TeleBot(token)

#Bot handler list user
users_handler={}



@bot.message_handler(commands=['start'])
def start(m):
    if not f"{m.chat.id}" in users_handler:
        handler = Handler(bot)
        users_handler[f"{m.chat.id}"] = handler

    handler = users_handler[f"{m.chat.id}"]
    handler.LanguageInit(m.from_user.id)
    handler.Start(m)

@bot.message_handler(content_types=['text'])
def handler_text(m):
    if not f"{m.chat.id}" in users_handler:
        handler = Handler(bot)
        users_handler[f"{m.chat.id}"] = handler

    handler=users_handler[f"{m.chat.id}"]
    handler.LanguageInit(m.from_user.id)
    handler.Text(m)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if not f"{call.message.chat.id}" in users_handler:
        handler = Handler(bot)
        users_handler[f"{call.message.chat.id}"] = handler

    handler = users_handler[f"{call.message.chat.id}"]
    handler.LanguageInit(call.from_user.id)
    handler.CallBacks(call)




if __name__ == '__main__':
    while True:
        try:
            #handler.Restart()
            bot.polling(none_stop=True, interval=3)
        except Exception as e:
            print(f"Exception -> {e}\n")