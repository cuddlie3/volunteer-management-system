
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from volunteers.models import Volunteer

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram import KeyboardButton

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


# Состояния регистрации
FULL_NAME, FULL_NAME_EN, PHONE, ID_DOCUMENT, STUDY_PLACE, ADDRESS, LANGUAGES, EMERGENCY = range(8)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Добро пожаловать в Volio!\n\n"
        "Это система управления волонтёрами.\n\n"
        "Давайте зарегистрируем вас.\n\n"
        "Введите ваше ФИО:"
    )

    return FULL_NAME


# ФИО
async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["full_name"] = update.message.text

    await update.message.reply_text(
        "Отлично!\n\n"
        "Теперь введите ваше ФИО на английском языке "
        "(как в удостоверении):"
    )

    return FULL_NAME_EN


# ФИО на английском
async def get_full_name_en(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["full_name_en"] = update.message.text

    button = KeyboardButton(
        "📱 Отправить номер телефона",
        request_contact=True
    )

    keyboard = [[button]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "📱 Теперь отправьте ваш номер телефона.\n\n"
        "Нажмите кнопку ниже:",
        reply_markup=reply_markup
    )

    return PHONE
# Телефон
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.contact:

        context.user_data["phone"] = update.message.contact.phone_number

    else:

        context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "🪪 Теперь прикрепите фотографию "
        "или PDF вашего удостоверения личности."
    )

    return ID_DOCUMENT


# Документ
async def get_id_document(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.photo:

        file_id = update.message.photo[-1].file_id
        context.user_data["id_document"] = file_id

    elif update.message.document:

        file_id = update.message.document.file_id
        context.user_data["id_document"] = file_id

    else:

        await update.message.reply_text(
            "Пожалуйста, отправьте фотографию "
            "или PDF документа."
        )

        return ID_DOCUMENT

    await update.message.reply_text(
        "🎓 Где вы сейчас учитесь?\n\n"
        "Например:\n"
        "KIMEP University"
    )

    return STUDY_PLACE


# Место учёбы
async def get_study_place(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["study_place"] = update.message.text

    await update.message.reply_text(
        "🏠 Введите ваш домашний адрес:"
    )

    return ADDRESS


# Адрес
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["address"] = update.message.text

    await update.message.reply_text(
        "🌐 Какие языки вы знаете?\n\n"
        "Например:\n"
        "Казахский — родной\n"
        "Русский — свободно\n"
        "Английский — B2"
    )

    return LANGUAGES


# Языки
async def get_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["languages"] = update.message.text

    await update.message.reply_text(
        "🚨 Укажите экстренный контакт.\n\n"
        "Например:\n"
        "Мама — +7 777 123 45 67"
    )

    return EMERGENCY


# Экстренный контакт
async def get_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["emergency"] = update.message.text

    data = context.user_data

    await update.message.reply_text(
        "✅ Регистрация завершена!\n\n"
        f"👤 ФИО: {data['full_name']}\n"
        f"🌐 ФИО на английском: {data['full_name_en']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🎓 Учёба: {data['study_place']}\n"
        f"🏠 Адрес: {data['address']}\n"
        f"🌐 Языки: {data['languages']}\n"
        f"🚨 Экстренный контакт: {data['emergency']}\n\n"
        "Спасибо за регистрацию! ❤️"
    )

    return ConversationHandler.END


# Отмена регистрации
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "❌ Регистрация отменена."
    )

    return ConversationHandler.END


def main():

    app = Application.builder().token(TOKEN).build()

    registration = ConversationHandler(

        entry_points=[
            CommandHandler("start", start)
        ],

        states={

            FULL_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_full_name
                )
            ],

            FULL_NAME_EN: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_full_name_en
                )
            ],

            PHONE: [
                MessageHandler(
                    filters.CONTACT | (filters.TEXT & ~filters.COMMAND),
                    get_phone
                )
            ],

            ID_DOCUMENT: [
                MessageHandler(
                    filters.PHOTO | filters.Document.ALL,
                    get_id_document
                )
            ],

            STUDY_PLACE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_study_place
                )
            ],

            ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_address
                )
            ],

            LANGUAGES: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_languages
                )
            ],

            EMERGENCY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_emergency
                )
            ],
        },

        fallbacks=[
            CommandHandler("cancel", cancel)
        ]
    )

    app.add_handler(registration)

    print("Volio запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()