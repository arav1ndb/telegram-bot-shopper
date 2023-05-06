from typing import Final
from telegram import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
import pandas as pd
import prettytable as pt

TOKEN: Final = "6026142184:AAE1AGVwwXq5AKSx0YhM2Hiobv8kWQjAdiI"
BOT_USERNAME: Final = "@Aravind's shopping bot"

print('Starting up bot...')

state = 0 #0 - shopping,1 - payment,2 - 

inventory = pd.DataFrame(
    {
        "itemId":[1,2,3,4,5],
        "name":['sting','good day ','hide n seek','amul chocobar','kit kat'],
        "quantity":[35,50,30,8,100],
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


def handle_response(text: str) -> list:
    # Create your own response logic
    proc: str = text.lower()

    if 'inventory' in proc:
        inv = "The items currently present in the inventory : \n\n"
        table = pt.PrettyTable(['Items','Price','Availability'])
        for i,k in inventory.iterrows():
            if k['quantity']>=15:
                avl = 'Yes'
            elif k['quantity'] >=5:
                avl = 'Low Stock'
            else:
                avl = 'None'
            table.add_row([str(k['name']),str(k['price']),avl])
        inv+= f'<pre>{table}</pre>'
        inv+= '\n\nPlease select the items you wish to buy in the form of <b>select item1-q1, item2-q2...</b>'
        return inv,'HTML'
    
    if 'select' in proc or 's' in proc:
        proc = proc.replace('  ',' ')
        proc = proc.replace('select ','')
        items = proc.split(', ')
        print(items)
        bill = '<b>The item bill</b>'
        tp=0
        billTable = pt.PrettyTable(['Items','Quantity','Total price'])
        for it in items:
            item,q = it.split('-')
            print(item,q)
            row = inventory.loc[(inventory['name']==item)]
            tp+=int(q)*int(row['price'].iloc[0])
            billTable.add_row([str(row['name'].iloc[0]),q,int(q)*int(row['price'].iloc[0])])
        billTable.add_row(['Total Amt','-',tp])
        bill+= f'<pre>{billTable}</pre>'
        print(bill)
        return bill,'HTML'

    return str('echo'),'None'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    response, parsemode = handle_response(text)

    # Reply normal if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response, parse_mode=parsemode)


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