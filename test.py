from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    ref_id = msg.split()[1] if len(msg.split()) > 1 else ""
    
    print('who pressed:', update.effective_chat.id)
    print('who referred:', ref_id)



if __name__ == '__main__':
    app = ApplicationBuilder().token('').build()

    app.add_handler(CommandHandler("start", start))

    print('Starting bot...')

    app.run_polling()