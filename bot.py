import telebot
import os


token = os.environ['TG_TOKEN']
bot = telebot.AsyncTeleBot(token)

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


@bot.message_handler(commands=['start', 'help'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(chat_id=message.chat.id, text='Привет, я кот-бот, который очень любит котиков, '
                                                       'шутки и умные мысли!\n'
                                                       'Напиши мне и я поделюсь ими с тобой.\n'
                                                       'Умные мысли приходят сразу,а котики идут подольше,'
                                                       ' у них же лапки!\nПодробнее по /help')
    elif message.text == "/help":
        bot.send_message(chat_id=message.chat.id, text='/pizdec для получения умной (и не очень) мысли\n'
                                                       '/bashim для получения цитат с bash.im\n'
                                                       '/poetory для получения пирожка с poetory.ru: '
                                                       'сайт у них тяжёлый, может быть придётся подождать\n'
                                                       '/cat для получения котика\n')