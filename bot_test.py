import logging
import queue
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Определяем состояния разговора
ITEM, QUANTITY, CONFIRM = range(3)

# Настройка Google Sheets API
"""scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('path/to/your/credentials.json', scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Your Google Sheet Name").sheet1"""

# Определяем функцию для обработки команды /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Привет! Я бот для заказа канцелярских товаров. Пожалуйста, укажите, что вам нужно.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ITEM

# Определяем функцию для обработки ввода товара
def item(update: Update, context: CallbackContext) -> int:
    context.user_data['item'] = update.message.text
    update.message.reply_text('Укажите количество.')
    return QUANTITY

# Определяем функцию для обработки ввода количества
def quantity(update: Update, context: CallbackContext) -> int:
    context.user_data['quantity'] = update.message.text
    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        f'Вы хотите заказать {context.user_data["quantity"]} единиц {context.user_data["item"]}. Подтвердите.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CONFIRM

# Определяем функцию для обработки подтверждения
def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'да':
        # Отправляем данные в Google Таблицу
        row = [context.user_data['item'], context.user_data['quantity']]
        sheet.append_row(row)
        update.message.reply_text('Ваш заказ успешно размещен!', reply_markup=ReplyKeyboardRemove())
        # Уведомляем определенного пользователя
        context.bot.send_message(chat_id='YOUR_NOTIFICATION_CHAT_ID', text=f'Новый заказ: {context.user_data["quantity"]} единиц {context.user_data["item"]}')
    else:
        update.message.reply_text('Заказ отменен.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Определяем функцию для обработки ошибок
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Вставьте сюда ваш токен API
    update_queue = queue.Queue()
    updater = Updater("7715212560:AAHOTS0r1Eu3UGnshUaL_T7s3bs_vqLSM4A", update_queue)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ITEM: [MessageHandler(filters.text & ~filters.command, item)],
            QUANTITY: [MessageHandler(filters.text & ~filters.command, quantity)],
            CONFIRM: [MessageHandler(filters.regex('^(Да|Нет)$'), confirm)]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
