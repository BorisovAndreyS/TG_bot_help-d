from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import ChatGPT_TOKEN, TG_token
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     dialog.mode = 'main'
#     text = load_message('main')
#     await send_image(update, context, 'main')
#     await send_text(update, context, text)
#     await show_main_menu(update, context, {
#         'start': 'Главное меню',
#         'random': 'Узнать случайный интересный факт 🧠',
#         'gpt': 'Задать вопрос чату GPT 🤖',
#         'talk': 'Поговорить с известной личностью 👤',
#         'quiz': 'Поучаствовать в квизе ❓'
#         # Добавить команду в меню можно так:
#         # 'command': 'button text'
#
#     })


# dialog = Dialog()
# dialog.mode = None
# Переменные можно определить, как атрибуты dialog

#Две строки отвечают за функцию ЭХО,
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text(update, context, update.message.text)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Загрузили Промпт
    prompt = load_prompt('random')
    #Отправляем картинку
    await send_image(update, context, 'random')

    #Получаем тект
    text = load_message('random')
    #Отпраяем текст об ожидании
    message = await send_text(update, context, text)
    #получаем ответ от чата ГПТ
    answer = await chat_gpt.send_question(prompt, text)
    #меняем сообещение
    await message.edit_text(answer)

chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(TG_token).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
# app.add_handler(CommandHandler('start', start))
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))
#обработчик команды random
app.add_handler(CommandHandler('random', random))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
# app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()
