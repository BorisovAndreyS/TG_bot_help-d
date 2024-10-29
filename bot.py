import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, Updater

from credentials import ChatGPT_TOKEN, TG_token
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

import logging


#
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Определяем состояния для разных меню
MENU_MAIN, MENU_OPTION1, MENU_OPTION2, MENU_OPTION3 = range(4)

chat_gpt = ChatGptService(ChatGPT_TOKEN)

commands_menu = {
        'start': 'Главное меню',
        'echo': 'ЭХО - БОТ',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'cancel': 'Прекратить работу'
        # Добавить команду в меню можно так:
        # 'command': 'button text'

    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # dialog.mode = 'main'
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, commands_menu)
    return MENU_MAIN

# Задача 1. Две строки отвечают за функцию ЭХО,
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы находитесь в меню ЭХО Бот.\n"
        "Отправьте любое сообщение для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )
    return MENU_OPTION1



# Задача 2. Рандомный Факт
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы находитесь в меню Рандомный факт.\n"
        "/random для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )
    await handle_random(update, context)
    return MENU_OPTION2

# Задача 3. ChatGPT интерфейс
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    await update.message.reply_text(
        "Вы находитесь в меню gpt.\n"
        "Пишите запросы для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )
    return MENU_OPTION3
async def handle_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Загрузить Промпт
    Загрузить картинку
    Отправить сообщение в чат
    получить сообщение и отправить пользователю
    :param update:
    :param context:
    :return:
    '''

    text = update.message.text
    chat_gpt.set_prompt('gpt')
    #answer = await chat_gpt.send_message_list()
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return MENU_OPTION3


async def handle_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
# Логика обработки сообщений в меню echo
    await update.message.reply_text(update.message.text)
    return MENU_OPTION1

async def handle_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
# Логика обработки сообщений в меню опции 2
#     await update.message.reply_text(f"Вы выбрали опцию 2 и отправили: {update.message.text}")
# Загрузили Промпт
    prompt = load_prompt('random')
    # Отправляем картинку
    await send_image(update, context, 'random')

    # Получаем тект
    text = load_message('random')
    # Отпраяем текст об ожидании
    message = await send_text(update, context, text)
    # получаем ответ от чата ГПТ
    answer = await chat_gpt.send_question(prompt, text)
    # меняем сообещение
    await message.edit_text(answer)
    return MENU_OPTION2



#функция возврата в главное меню
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return MENU_MAIN

def main():
    # Настройка обработки команд и состояния разговора
    app = ApplicationBuilder().token(TG_token).build()

    conv_handler = ConversationHandler(
        #начальная точка входа
        entry_points=[CommandHandler('start', start)],
        states={
            MENU_MAIN: [
                CommandHandler('echo', echo),
                CommandHandler('random', random),
                CommandHandler('gpt', gpt),
            ],
            MENU_OPTION1: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_echo),
                CommandHandler('back', back_to_main)
            ],
            MENU_OPTION2: [
                CommandHandler('random', handle_random),
                CommandHandler('back', back_to_main)
            ],
            MENU_OPTION3: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt),
                CommandHandler('back', back_to_main)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()
