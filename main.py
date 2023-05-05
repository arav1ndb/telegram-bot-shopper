from typing import Final
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
import pandas as pd
import prettytable as pt


TOKEN: Final = "6026142184:AAE1AGVwwXq5AKSx0YhM2Hiobv8kWQjAdiI"
BOT_USERNAME: Final = "@Aravind's shopping bot"

print('Starting up bot...')

inventory = pd.DataFrame(
    {
        "itemId":[1,2,3,4,5],
        "name":['Sting','Good Day biscuts','Hide n Seek','Amul Chocobar','Kit Kat'],
        "quantity":[35,50,30,20,100],
        "price":[20,10,30,15,25],
        "tags":[['snack','cool drink'],['snack','biscuts'],['snack','biscuts'],['snack','ice cream'],['snack','chocholates']]
    }
)

options = [['inventory','history']]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! \nWelcome to Aravind\'s Shopping bot for all your shopping needs and more!!')
    await update.message.reply_text('Click \'inventory\' to check out all the items present and \'history\' to see your previous purchases',
                    reply_markup=ReplyKeyboardMarkup(options, one_time_keyboard=True, input_field_placeholder="select an option"
                        ),)
    

# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


# Lets us use the /custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')


def handle_response(text: str) -> str:
    # Create your own response logic
    proc: str = text.lower()
    if 'inventory' in proc or 'i' in proc :
        inv = "The items currently present in the inventory are \n\n"
        table = pt.PrettyTable(['Items','Quantity'])
        for i,k in inventory.iterrows():
            table.add_row([str(k['name']),str(k['quantity'])])
        inv+= f'<pre>{table}</pre>'
        return inv
    # proc= " \|title1\|title2\| \n \|\-\-\-\|\-\-\-\| \n \|r1\|r11\| \n \|r2\|r222626\|"
    # proc ="<pre>| Tables   |      Are      |  Cool |\n|----------|:-------------:|------:|\n| col 1 is |  left-aligned | $1600 |\n| col 2 is |    centered   |   $12 |\n| col 3 is | right-aligned |    $1 |</pre>"
    return str(proc+' echo')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    # if message_type == 'group':
    #     # Replace with your bot username
    #     if BOT_USERNAME in text:
    #         new_text: str = text.replace(BOT_USERNAME, '').strip()
    #         response: str = handle_response(new_text)
    #     else:
    #         return  # We don't want the bot respond if it's not mentioned in the group
    # else:
    response: str = handle_response(text)

    # Reply normal if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response, parse_mode='HTML')


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)