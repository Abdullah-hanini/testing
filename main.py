import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, code

# Replace YOUR_BOT_TOKEN with your bot's API token
API_TOKEN = "5778807424:AAEzZUbdqOY_k9Ux6IkSzxF5G_6H5Uo_aos"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot and the dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Connect to the database
conn = sqlite3.connect('vouchers.db')
cursor = conn.cursor()

# Create the vouchers table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS vouchers
                  (voucher_code text, redeemed integer)''')

# Create a list of admins
admins = [960684105]  # Replace this with the user IDs of your admins

# Handle the /start command
@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.reply("Welcome to OnlyBot")

# Handle the /store command
@dp.message_handler(commands='store')
async def store(message: types.Message):
    # Split the message into the voucher code and the voucher value
    voucher_code, voucher_value = message.text.split()[1:]

    # Store the voucher in the database
    cursor.execute('INSERT INTO vouchers VALUES (?, ?)', (voucher_code, 0))
    conn.commit()

    await message.reply(f"Voucher {voucher_code} with value {voucher_value} stored successfully!")


# Handle the /redeem command
@dp.message_handler(commands='redeem')
async def redeem(message: types.Message):
    # Split the message into the voucher code
    voucher_code = message.text.split()[1]

    # Check if the voucher exists in the database
    cursor.execute('SELECT * FROM vouchers WHERE voucher_code=?', (voucher_code,))
    result = cursor.fetchone()
    if not result:
        await message.reply(f"Sorry, voucher {voucher_code} does not exist.")
        return

    # Check if the voucher has already been redeemed
    if result[1] == 1:
        await message.reply(f"Sorry, voucher {voucher_code} has already been redeemed.")
        return

    # Create the inline keyboard markup
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Redeem", callback_data=voucher_code))

    # Send the message with the inline keyboard
    await bot.send_message(
        message.chat.id,
        f"Press the button to redeem voucher {voucher_code}",
        reply_markup=markup
    )


# Handle button press
@dp.callback_query_handler(lambda c: c.data == voucher_code)
async def process_callback_button(callback_query: types.CallbackQuery):
    voucher_code = callback_query.data

    # Mark the voucher as redeemed and update the database
    cursor.execute('UPDATE vouchers SET redeemed=1 WHERE voucher_code=?', (voucher_code,))
    conn.commit()

    await bot.send_message(
        callback_query.message.chat.id,
        f"https://t.me/+kIKOmYxXq5hhZDc8"
    )





# Handle the /panel command
@dp.message_handler(commands='panel')
async def panel(message: types.Message):
    # Check if the user is an admin
    if message.from_user.id not in admins:
        await message.reply("Sorry, you do not have permission to access the admin panel.")
        return

    # Get a list of all vouchers
    cursor.execute('SELECT * FROM vouchers')
    vouchers = cursor.fetchall()

    # Format the vouchers as a list of strings
    voucher_strings = []
    for voucher in vouchers:
        voucher_code, redeemed = voucher
        redeemed_text = "redeemed" if redeemed else "not redeemed"
        voucher_strings.append(f"{voucher_code}: {redeemed_text}")

    # Send the list of vouchers to the user
    if voucher_strings:
        voucher_list = "\n".join(voucher_strings)
        await message.reply(f"Here are all the vouchers:\n{voucher_list}")
    else:
        await message.reply("There are no vouchers stored.")

if __name__ == '__main__':
    # Start the bot
    executor.start_polling(dp)