import os
import telebot
from telebot.types import (BotCommand, InlineKeyboardMarkup,
                           InlineKeyboardButton, ForceReply)
from dotenv import load_dotenv
from sql_db import DataBase, TIME_PERIODS

load_dotenv()
TEL_TOKEN = os.environ.get('TEL_TOKEN')
bot = telebot.TeleBot(TEL_TOKEN)

# Set up bot menu commands
bot.set_my_commands([
    BotCommand("/new", "New spend"),
    BotCommand("/overview", "Spending overview"),
    BotCommand("/delete", "Delete last spend"),
    BotCommand("/categories", "Set up categories")
])


# Set up actions on global and menu commands
@bot.message_handler(commands=['start', 'help'])
def start(message):
    db = DataBase(message.from_user.id)
    if not db.check_user_exist():
        db.categories_db_initialization()
    db.close()
    bot.send_message(
        message.from_user.id,
        'Welcome to a spending bot. Here you easily can record your daily '
        'spending in a custom categories and track your personal finance. We '
        'already added 4 basic categories. Check it out and adjust categories '
        'list as you want (you could delete old and add new categories).\n\n'
        '*Set up categories* here /categories\n'
        '*Add new spend* here /new\n'
        '*Delete wrong entry* here /delete\n'
        '*Display your spending records* and total amounts of spending for '
        'different periods here /overview\n\n'
        'At any moment you have quick access to these operations via ↙ Menu '
        'button in the left bottom corner of your screen.',
        parse_mode='Markdown')


@bot.message_handler(commands=['new'])
def new_spend(message):
    db = DataBase(message.from_user.id)
    category_select = InlineKeyboardMarkup(row_width=2)
    category_select.add(*[InlineKeyboardButton(
                        text=cat,
                        callback_data=f'spend {cat}')
                        for cat in db.read_categories()])
    db.close()
    bot.send_message(
        message.chat.id,
        'Choose category to add a new spend',
        reply_markup=category_select
        )


@bot.message_handler(commands=['overview'])
def overview(message):
    db = DataBase(message.chat.id)
    if db.check_user_exist(table='spendings'):
        duration_select = InlineKeyboardMarkup()
        duration_select.add(InlineKeyboardButton(
                            text='Get overview from the start of this month',
                            callback_data='overview this'))
        duration_select.add(InlineKeyboardButton(
                            text='Get overview for the 7 last days',
                            callback_data='overview 7'))
        duration_select.add(InlineKeyboardButton(
                            text='Get overview for the 30 last days',
                            callback_data='overview 30'))
        bot.send_message(
            message.chat.id,
            'Select the period for which you want to get an overview '
            'of your spending',
            reply_markup=duration_select
            )
    else:
        bot.send_message(
            message.chat.id,
            "You haven't got any spending entries yet. "
            "Try to make a new one /new")
    db.close()


@bot.message_handler(commands=['delete'])
def erase_spend(message):
    db = DataBase(message.chat.id)
    if db.check_user_exist(table='spendings'):
        id, time, cat, amount = [*db.last_spend()]
        category_manage = InlineKeyboardMarkup()
        category_manage.add(InlineKeyboardButton(
                            text='Delete this last spend',
                            callback_data=f'erase {id}'))
        bot.send_message(
            message.chat.id,
            f'_Your last spend was_:\n{time} | {cat} | `{amount}€`',
            reply_markup=category_manage,
            parse_mode='Markdown'
            )
    else:
        bot.send_message(
            message.chat.id,
            'You do not have any spending records.')
    db.close()


@bot.message_handler(commands=['categories'])
def category_setting(message):
    db = DataBase(message.chat.id)
    if not db.check_user_exist():
        db.categories_db_initialization()
        bot.send_message(
            message.chat.id,
            'You deleted all your categories. Here are your default.'
            )
    category_manage = InlineKeyboardMarkup(row_width=2)
    category_manage.add(*[InlineKeyboardButton(
                        text=f'✂ {cat}',
                        callback_data=f'del {cat}')
                        for cat in db.read_categories()])
    category_manage.add(InlineKeyboardButton(
                        text='Add new category',
                        callback_data='add_category'))
    db.close()
    bot.send_message(
        message.chat.id,
        'Here are your current categories. Push the button ✂ to delete one '
        '(spending, associated with this category will remain). You could add '
        'new custom category thru "Add new category" button. These categories '
        'will be available at a new spend.',
        reply_markup=category_manage
        )


# Set up actions on inline-buttons commands
@bot.callback_query_handler(func=lambda call: call.data.startswith('spend'))
def provide_amount(call):
    message = f'New spend at: {call.data.split()[-1]}'
    reply = ForceReply(input_field_placeholder='Write amount here')
    bot.send_message(call.message.chat.id, message, reply_markup=reply)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('overview'))
def overview_from_db(call):
    try:
        db = DataBase(call.message.chat.id)
        period = call.data.split()[-1]
        table = '\n'.join(db.read_spendings(period))
        header = (f'_Your spendings in {TIME_PERIODS[period][1]}           _\n'
                  '*Date&Time* *|*   *Category&Amount*\n'
                  '-----------------------------------------------------\n')
        total = (f'Total spending in {TIME_PERIODS[period][1]}: '
                 f'*{db.get_sum(period)}€*\n'
                 '-----------------------------------------------------\n')
        owerview = '\n'.join(db.get_sum_categories(period))
        answer = header + table
        second_answer = total + owerview
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            answer,
            parse_mode='Markdown')
        bot.send_message(
            call.message.chat.id,
            second_answer,
            parse_mode='Markdown')
        db.close()
    except TypeError:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "You haven't got any spending entries yet. "
            "Try to make a new one /new")


@bot.callback_query_handler(func=lambda call: call.data.startswith('erase'))
def delete_from_db(call):
    db = DataBase(call.message.chat.id)
    if db.delete_spend(call.data.split()[-1]):
        message = 'The spend was deleted'
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, message)
    db.close()


@bot.callback_query_handler(func=lambda call: call.data == 'add_category')
def new_category(call):
    message = ('Give a name to a new category in your personal list. '
               'It should be one word. All categories consisting two and more '
               'separate words will be croped to a first one. You could '
               'illustrate your category with any emoji from keyboard if you '
               'wish, but do not use space between it. '
               'Example: 😉*MyCategory*.')
    reply = ForceReply(input_field_placeholder='Write name here')
    bot.send_message(call.message.chat.id, message, reply_markup=reply)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('del'))
def delete_category(call):
    db = DataBase(call.message.chat.id)
    category = call.data.split()[-1]
    if db.delete_category(category):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            f'Category *{category}* deleted',
            parse_mode='Markdown')
        db.close()
        category_setting(call.message)


# Set up reactions on a text messages
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.reply_to_message:
        operation = message.reply_to_message.text
        if operation.startswith('New spend at'):
            category = operation.split()[-1]
            spend_to_db(message, category)
        if operation.startswith('Give a name to a new category'):
            add_category_to_db(message)
    else:
        bot.send_message(
            message.chat.id,
            "I don't understand you. Please, use the ↙ Menu.")


# Individual functions
def spend_to_db(message, category):
    db = DataBase(message.chat.id)
    amount = message.text.replace(',', '.')
    try:
        amount = int(amount)
    except ValueError:
        try:
            amount = float(amount)
        except ValueError:
            bot.send_message(
                message.chat.id,
                'This is not a number. No record has been made. Examples of '
                'a correct amount: 5 or 0.5 or 25.65 or 44,80.')
            db.close()
            return
    if db.new_spending(category, amount):
        total = ('Your total spendings since the start of this '
                 f'month: *{db.get_sum("this")}€*')
        bot.send_message(
            message.chat.id,
            f'A spending entry in the *{category}* category for '
            f'*{amount}€* is done.\n{total}',
            parse_mode='Markdown')
    db.close()


def add_category_to_db(message):
    db = DataBase(message.chat.id)
    category = message.text.split()[0]
    if db.add_category(category):
        bot.send_message(
            message.chat.id,
            f'New category: *{category}* added to your list ',
            parse_mode='Markdown')
        db.close()
        category_setting(message)


if __name__ == '__main__':
    db = DataBase()
    db.create_database()
    db.close()
    bot.polling(none_stop=True, interval=0)
