import telegram
from telegram.ext import Updater
import pandas as pd
import numpy as np

# Initialize the bot
bot = telegram.Bot(token='6026142184:AAE1AGVwwXq5AKSx0YhM2Hiobv8kWQjAdiI')
TOKEN = '6026142184:AAE1AGVwwXq5AKSx0YhM2Hiobv8kWQjAdiI'
# Define the inventory dataframe
inventory_df = pd.DataFrame({'item_id': [1, 2, 3],
                             'item_name': ['Item 1', 'Item 2', 'Item 3'],
                             'item_price': [10, 20, 30],
                             'item_stock': [5, 10, 15]})

# Define the user history dataframe
user_history_df = pd.DataFrame(columns=['user_id', 'item_id', 'item_name', 'item_price', 'points_earned'])

# Define the user points dictionary
user_points = {}

# Define the cart dictionary
cart = {}

# Function to handle the /start command
def start(update, context):
    user_id = update.effective_user.id
    if user_id not in user_points:
        user_points[user_id] = 0
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, welcome to our store!")

# Function to handle the /inventory command
def inventory(update, context):
    inventory_text = "Here is our inventory:\n\n"
    for _, row in inventory_df.iterrows():
        inventory_text += f"{row['item_name']} - ${row['item_price']} - Stock: {row['item_stock']}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=inventory_text)

# Function to handle the /cart command
def show_cart(update, context):
    user_id = update.effective_user.id
    if user_id not in cart:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your cart is empty.")
        return
    cart_text = "Here is your cart:\n\n"
    total_price = 0
    for item_id, quantity in cart[user_id].items():
        item = inventory_df.loc[inventory_df['item_id'] == item_id].iloc[0]
        cart_text += f"{item['item_name']} - ${item['item_price']} - Quantity: {quantity}\n"
        total_price += item['item_price'] * quantity
    cart_text += f"\nTotal price: ${total_price}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=cart_text)

# Function to handle the /add command
def add_to_cart(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide the item ID and quantity.")
        return
    try:
        item_id = int(args[0])
        quantity = int(args[1])
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input.")
        return
    if item_id not in inventory_df['item_id'].tolist():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Item not found.")
        return
    item = inventory_df.loc[inventory_df['item_id'] == item_id].iloc[0]
   
    if quantity <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid quantity.")
        return
    if item['item_stock'] < quantity:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Insufficient stock.")
        return
    if user_id not in cart:
        cart[user_id] = {}
    if item_id not in cart[user_id]:
        cart[user_id][item_id] = 0
    cart[user_id][item_id] += quantity
    inventory_df.loc[inventory_df['item_id'] == item_id, 'item_stock'] -= quantity
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{quantity} {item['item_name']} added to cart.")

# Function to handle the /remove command
def remove_from_cart(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 2:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide the item ID and quantity.")
        return
    try:
        item_id = int(args[0])
        quantity = int(args[1])
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input.")
        return
    if item_id not in inventory_df['item_id'].tolist():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Item not found.")
        return
    if quantity <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid quantity.")
        return
    if user_id not in cart or item_id not in cart[user_id]:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Item not found in cart.")
        return
    if cart[user_id][item_id] < quantity:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid quantity.")
        return
    item = inventory_df.loc[inventory_df['item_id'] == item_id].iloc[0]
    cart[user_id][item_id] -= quantity
    inventory_df.loc[inventory_df['item_id'] == item_id, 'item_stock'] += quantity
    if cart[user_id][item_id] == 0:
        del cart[user_id][item_id]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{quantity} {item['item_name']} removed from cart.")

# Function to handle the /checkout command
def checkout(update, context):
    user_id = update.effective_user.id
    if user_id not in cart:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your cart is empty.")
        return
    total_price = 0
    for item_id, quantity in cart[user_id].items():
        item = inventory_df.loc[inventory_df['item_id'] == item_id].iloc[0]
        total_price += item['item_price'] * quantity
        user_history_df = user_history_df.append({'user_id': user_id,
                                                  'item_id': item['item_id'],
                                                  'item_name': item['item_name'],
                                                  'item_price': item['item_price'],
                                                  'points_earned': item['item_price'] / 10},
                                                 ignore_index=True)
    if user_id not in user_points:
        user_points[user_id] = 0
    user_points[user_id] += total_price / 10
    cart[user_id] = {}
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have successfully purchased items for a total of {total_price:.2f}.\n\n"
             f"You have earned {total_price / 10:.2f} points.\n\n"
             f"Your current points balance is {user_points[user_id]:.2f}.")
    user_history_df.to_csv("user_history.csv", index=False)
    inventory_df.to_csv("inventory.csv", index=False)

# Function to handle the /points command
def points(update, context):
    user_id = update.effective_user.id
    if user_id not in user_points:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You do not have any points yet.")
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have {user_points[user_id]:.2f} points.")

# Function to handle the /usepoints command
def use_points(update, context):
    user_id = update.effective_user.id
    args = context.args
    if len(args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide the amount of points you want to use.")
        return
    try:
        points_to_use = float(args[0])
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input.")
        return
    if user_id not in user_points:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You do not have any points yet.")
        return
    if points_to_use <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid amount of points.")
        return
    if user_points[user_id] < points_to_use:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Insufficient points.")
        return
    user_points[user_id] -= points_to_use
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have used {points_to_use:.2f} points.\n\n"
                                                                     f"Your current points balance is {user_points[user_id]:.2f}.")

# Function to load the inventory dataframe from a CSV file
def load_inventory_df():
    try:
        inventory_df = pd.read_csv("inventory.csv")
    except FileNotFoundError:
        # Create an empty inventory dataframe with columns "item_id", "item_name", "price", and "stock"
        inventory_df = pd.DataFrame(columns=["item_id", "item_name", "price", "stock"])
    return inventory_df

# Function to load the user history dataframe from a CSV file
def load_user_history_df():
    try:
        user_history_df = pd.read_csv("user_history.csv")
    except FileNotFoundError:
        # Create an empty user history dataframe with columns "user_id", "item_id", "item_name", "price", "quantity", and "points"
        user_history_df = pd.DataFrame(columns=["user_id", "item_id", "item_name", "price", "quantity", "points"])
    return user_history_df

# Function to load the user points dictionary from a CSV file
def load_user_points():
    try:
        with open("user_points.pkl", "rb") as f:
            user_points = pickle.load(f)
    except FileNotFoundError:
        user_points = {}
    return user_points

# Function to save the inventory dataframe to a CSV file
def save_inventory_df(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Function to save the user history dataframe to a CSV file
def save_user_history_df(user_history_df):
    user_history_df.to_csv("user_history.csv", index=False)

# Function to save the user points dictionary to a pickle file
def save_user_points(user_points):
    with open("user_points.pkl", "wb") as f:
        pickle.dump(user_points, f)

# Main function to run the bot
def main():
    # Load the inventory dataframe, user history dataframe, and user points dictionary
    inventory_df = load_inventory_df()
    user_history_df = load_user_history_df()
    user_points = load_user_points()

    # Create a telegram bot object
    updater = Updater(TOKEN,UpdateQueue(request=request))
    dispatcher = updater.dispatcher

    # Add handlers for the /start, /help, /inventory, /add, /remove, /cart, /checkout, /points, and /usepoints commands
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    inventory_handler = CommandHandler("inventory", inventory)
    add_handler = CommandHandler("add", add_to_cart)
    remove_handler = CommandHandler("remove", remove_from_cart)
    cart_handler = CommandHandler("cart", cart)
    checkout_handler = CommandHandler("checkout", checkout)
    points_handler = CommandHandler("points", points)
    use_points_handler = CommandHandler("usepoints", use_points)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(inventory_handler)
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(remove_handler)
    dispatcher.add_handler(cart_handler)
    dispatcher.add_handler(checkout_handler)
    dispatcher.add_handler(points_handler)
    dispatcher.add_handler(use_points_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until it is stopped manually or by the server
    updater.idle()

    # Save the inventory dataframe, user history dataframe, and user points dictionary
    save_inventory_df(inventory_df)
    save_user_history_df(user_history_df)
    save_user_points(user_points)

if __name__ == "__main__":
    main()
