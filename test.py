# import below, to work Telegram Bot with Django Rest Framework properly
# start

import sys

sys.dont_write_bytecode = True

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

django.setup()

from app import models

from asgiref.sync import sync_to_async
# end


from telegram import (
    Update,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

import datetime
import core

TELEGRAM_BOT_TOKEN = ""  # test token

(MENU_STATE,
 GAME_STATE,
 SCORE_STATE,
 CANDY_STATE,
 ADMIN_STATE,
 ) = range(5)

MAIN_MENU_KEYBOARD = [['🎮 New Game', '🍭 Balance']]


def get_date():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return date


def get_time():
    time = datetime.datetime.now().strftime("%H:%M:%S")
    return time


async def _is_admin(username, password):
    try:
        return models.UserAdmin.objects.filter(username=username, password=password).exists()

    except Exception as e:
        print(e)
        return False


@sync_to_async
def _post_client(user):
    try:
        models.TGClient(
            tg_id=user['id'],
            username=user['username'],
        ).save()

        return True
    except Exception as e:
        print(e)
        return False


@sync_to_async
def _post_candy(user):
    try:
        models.Candy(
            tg_id=user['id'],
            quantity=0,
        ).save()

        return True
    except Exception as e:
        print(e)
        return False


@sync_to_async
def _get_client_candy(user_id):
    return models.Candy.objects.filter(tg_id=user_id).values()


@sync_to_async
def _upd_candy_qty(user_id, qty):
    try:
        models.Candy.objects.filter(tg_id=user_id).update(quantity=qty)

        return True
    except Exception as e:
        print(e)
        return False


@sync_to_async
def _post_game(user_id, game_url, score):
    try:
        models.Games(
            tg_id=user_id,
            game_url=game_url,
            last_score=score,
        ).save()

        return True
    except Exception as e:
        print(e)
        return False


@sync_to_async
def _is_client(user_id):
    return models.TGClient.objects.filter(tg_id=user_id).exists()


@sync_to_async
def _get_client(user_id):
    return models.TGClient.objects.filter(tg_id=user_id).values()


@sync_to_async
def _get_clients():
    return models.TGClient.objects.all().values()


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id
    context.user_data['username'] = user.username

    if not await _is_client(context.user_data['id']):
        await _post_client(context.user_data)
        await _post_candy(context.user_data)

    await update.message.reply_text('🌝 Was-sap, ' + user.first_name + '!')
    await update.message.reply_text(
        'Choose an option:',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False),
    )

    return MENU_STATE


async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id

    await update.message.reply_text("🌝 Send me game url")

    return GAME_STATE


async def game_url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "https://prizes.gamee.com/game-bot/" in url:
        context.user_data["url"] = url
        await update.message.reply_text("🌝 Send me desired score")

        return SCORE_STATE
    else:
        await update.message.reply_text("🌚 Invalid game url")

        return GAME_STATE


async def score_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text

    if score:
        candy_qty = await _get_client_candy(context.user_data['id'])

        if int(candy_qty[0]['quantity']) > 0:
            context.user_data["score"] = score
            try:
                gamee = core.GameeHacker(context.user_data["url"], int(context.user_data["score"]), 0)
                gamee.send_score()
                await update.message.reply_text("🌝 Score updated successfully!")

                await _upd_candy_qty(context.user_data['id'], int(candy_qty[0]['quantity']) - 10)
                await _post_game(context.user_data['id'], context.user_data["url"], context.user_data["score"])

                # print("_" * 50)
                # print(gamee._get_game_data())
                # print("_" * 50)
                # print(gamee._get_user_credentials())
                # print("_" * 50)
                # print(gamee.get_user_summery_pprint())

            except Exception as e:
                print(e)
                await update.message.reply_text("🌚 An error has occurred")

                return MENU_STATE

        else:
            await update.message.reply_text("🌚 You don't have enough Candy")

            return MENU_STATE
    else:
        await update.message.reply_text("🌚 Invalid score!")

        return SCORE_STATE


async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data['id'] = user.id

    candy_qty = await _get_client_candy(context.user_data['id'])

    await update.message.reply_text("🌝 You have " + str(candy_qty[0]['quantity']) + " Candy")

    return GAME_STATE


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


async def is_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = """
🌝 Enter username and password to access admin panel
Example: admin 1234
    """

    await update.message.reply_text(text=txt)

    return ADMIN_STATE


async def give_candy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text.split()
    admin = args[0]
    password = args[1]

    is_admin = await _is_admin(admin, password)

    if is_admin:

        txt = """
🌝 Enter Telegram ID or Username and number of Candy you want to give
Example: @username 10
        """

        await update.message.reply_text(text=txt)

        return CANDY_STATE
    else:
        await update.message.reply_text("🌚 You are not admin!")

        return MENU_STATE


# @_is_admin
async def giveaway_candy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text
    args = args.split()

    if len(args) == 2:
        user_id = args[0]
        qty = args[1]

        if user_id.startswith('@'):
            user_id = user_id[1:]
            client = await _get_client(user_id)
            if client:
                user_id = client[0]['tg_id']
            else:
                await update.message.reply_text("🌚 User not found")

        client_candy = await _get_client_candy(user_id)
        if client_candy:
            client_candy = client_candy[0]
            qty = int(client_candy['quantity']) + int(qty)
            await _upd_candy_qty(user_id, qty)
            await update.message.reply_text("🌝 Candy given successfully")

            return MENU_STATE
        else:
            await update.message.reply_text("🌚 User not found")

            return MENU_STATE


async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cls = ""

    cls = await _get_clients()

    if cls:
        for i in cls:
            _cnd = await _get_client_candy(i['tg_id'])
            _cls += f"""
🌝 Username: {i['username']}
🌝 Telegram ID: {i['tg_id']}
🌝 Candy: {_cnd[0]['quantity']}
🌝 Client Since: {i['created_at'].strftime("%Y-%m-%d %H:%M:%S")}
🌝 Last Candy Given Time/Date: {_cnd[0]['created_at'].strftime("%Y-%m-%d %H:%M:%S")}\n\n
"""

        await update.message.reply_text(text=_cls)
        await update.message.reply_text(text='🌝 Total: ' + str(len(cls)))

        return MENU_STATE

    else:
        await update.message.reply_text(text='🌚 An error has occurred')

        return MENU_STATE


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).read_timeout(100). \
        get_updates_read_timeout(100).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_handler),
            CommandHandler('game', game_handler),
        ],
        states={
            MENU_STATE: [
                MessageHandler(filters.Regex('.*New Game$'), game_handler),
                MessageHandler(filters.Regex('.*Balance$'), balance_handler),
            ],
            GAME_STATE: [
                MessageHandler(filters.Regex('.*New Game$'), game_handler),
                MessageHandler(filters.Regex('.*Balance$'), balance_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, game_url_handler),
            ],
            SCORE_STATE: [
                MessageHandler(filters.Regex('.*New Game$'), game_handler),
                MessageHandler(filters.Regex('.*Balance$'), balance_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, score_handler),
            ],
            CANDY_STATE: [
                MessageHandler(filters.Regex('.*New Game$'), game_handler),
                MessageHandler(filters.Regex('.*Balance$'), balance_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, giveaway_candy_handler),
            ],
            ADMIN_STATE: [
                MessageHandler(filters.Regex('.*New Game$'), game_handler),
                MessageHandler(filters.Regex('.*Balance$'), balance_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, give_candy_handler),
            ],
        },
        fallbacks=[
            CommandHandler('start', start_handler),
            CommandHandler('game', game_handler),
            CommandHandler('balance', balance_handler),
            CommandHandler('get_report', report_handler),
            CommandHandler('give_candy', is_admin_handler),
            MessageHandler(filters.Regex('.*New Game$'), game_handler),
            MessageHandler(filters.Regex('.*Balance$'), balance_handler),
        ],
    )

    app.add_handler(conv_handler)

    app.add_error_handler(error_handler)

    print("updated...")
    app.run_polling()


if __name__ == "__main__":
    main()
