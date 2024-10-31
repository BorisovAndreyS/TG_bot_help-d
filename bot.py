import asyncio
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, Updater

from credentials import ChatGPT_TOKEN, TG_token
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

import logging

#
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )

# Определяем состояния для разных меню #Меню выбора персонажа
MENU_MAIN, MENU_ECHO, MENU_RANDOM, MENU_GPT, MENU_TALK, ONE, TWO, THREE, FOUR, FIVE = range(10)


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
    #Это вызывается в момент входа в меню
    await update.message.reply_text(
        "Вы находитесь в меню ЭХО Бот.\n"
        "Отправьте любое сообщение для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )
    return MENU_ECHO


async def handle_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика обработки сообщений в меню echo
    await update.message.reply_text(update.message.text)
    return MENU_ECHO


# Задача 2. Рандомный Факт
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Вход в меню random
    await update.message.reply_text(
        "Вы находитесь в меню Рандомный факт.\n"
        "/random для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )


    await handle_random(update, context)

    return MENU_RANDOM


async def handle_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика обработки сообщений в меню опции 2
    #     await update.message.reply_text(f"Вы выбрали опцию 2 и отправили: {update.message.text}")

    keyboard = [
        [
            InlineKeyboardButton("Еще", callback_data=str(MENU_RANDOM)),
            InlineKeyboardButton("Выйти", callback_data=str(MENU_MAIN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

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
    await message.edit_text(answer, reply_markup=reply_markup)
    return MENU_RANDOM

#Обработка нажатия кнопок в Random
async def random_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == str(MENU_RANDOM):
        # Если пользователь нажал "Еще", мы просто вызываем handle_random снова
        await handle_random(update, context)
    elif query.data == str(MENU_MAIN):
        # Если пользователь нажал "Выйти", мы выходим в главное меню
        await start(update, context)


# Задача 3. ChatGPT интерфейс
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'gpt')
    await update.message.reply_text(
        "Вы находитесь в меню gpt.\n"
        "Пишите запросы для взаимодействия.\n"
        "Или /back для возвращения в главное меню."
    )
    return MENU_GPT

#Обработка меню GPT
async def handle_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Загрузить Промпт
    Загрузить картинку
    Отправить сообщение в чат
    получить сообщение и отправить пользователю

    '''

    text = update.message.text
    chat_gpt.set_prompt('gpt')
    answer = await chat_gpt.add_message(text)
    await send_text(update, context, answer)
    return MENU_GPT



#Меню Talk, Диалог с известной личностью
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Вход в меню Talk

    text_talk = load_message('talk')
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
            InlineKeyboardButton("4", callback_data=str(FOUR)),
            InlineKeyboardButton("5", callback_data=str(FIVE)),
            InlineKeyboardButton("Выход", callback_data=str(MENU_MAIN)),

        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text_talk, reply_markup=reply_markup)

    return MENU_TALK

star_human = {
    '5': ['Курт Кобейн', 'talk_cobain'],
    '6': ['Елизавета II', 'talk_queen'],
    '7': ['Джон Толкиен', 'talk_tolkien'],
    '8': ['Фридрих Ницше', 'talk_nietzsche'],
    '9': ['Стивен Хокинг', 'talk_hawking']
}



async def talk_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработка кнопки talk
    query = update.callback_query
    await query.answer()

    select_key = query.data
    if select_key == str(MENU_MAIN):
        return await back_to_main()

    select_star = star_human.get(select_key)
    if not select_star:
        await send_text(update, context, 'Выбран не верный персонаж')
        return MENU_MAIN

    await send_text(update, context, f'Отличный выбор, буду общаться с тобой как {star_human[query.data][0]} ! \n'
                                     f'Что ты хочешь узнать?')

    await send_image(update, context, select_star[1])
    #Установка состояния выбора
    context.user_data['select_star'] = select_star[1]

    return MENU_TALK




#Функция обработки вызова talk
async def handle_talk(update: Update, context: ContextTypes.DEFAULT_TYPE, star_human_query = None):
    select_prompt = context.user_data['select_star']
    # print(select_prompt)
    if not select_prompt:
        await send_text(update, context, "Произошла ошибка. Пожалуйста, выберите снова.")
        return MENU_TALK

    chat_gpt.set_prompt(select_prompt)
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    await update.message.reply_text(answer)
    return MENU_TALK





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
                CommandHandler('talk', talk),
            ],
            MENU_ECHO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_echo),
                CommandHandler('back', back_to_main)
            ],
            MENU_RANDOM: [
                CommandHandler('random', handle_random),
                CallbackQueryHandler(random_button_handler, pattern="^" + str(MENU_RANDOM) + "$"),
                CallbackQueryHandler(back_to_main, pattern="^" + str(MENU_MAIN) + "$"),
                CommandHandler('back', back_to_main)
            ],
            MENU_GPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt),
                CommandHandler('back', back_to_main)
            ],
            MENU_TALK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_talk),
                CallbackQueryHandler(talk_button_handler, pattern="^(5|6|7|8|9|MENU_MAIN)$"),
                CommandHandler('back', back_to_main)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        per_message=False
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()
