import datetime
import time
import os
import random
import dotenv
from threading import Thread
import telebot
import mysql.connector
from mysql.connector import Error

# Environment variables set in .env file
dotenv.load_dotenv()
username = os.getenv('EMAIL')
password = os.getenv('PASS')
seconds_between_checks = 600  

TOKEN = os.getenv('TOKEN')
print(TOKEN)
print(username)
print(password)

# Telegram Bot setup
bot = telebot.TeleBot(TOKEN)

# Dictionary to store user dates
userdates = {}

kaz_date = "Please enter the desired date in the format: DD:MM:YYYY. Example: 01:01:2024"
rus_date = "Please enter the date in the format DD:MM:YYYY. Example: 01:01:2024"
nokaz = "🚫Unfortunately, this date is taken, and if it becomes available, we will send you a message."
norus = "Unfortunately, this is not a free date, we will notify you if it becomes available."
erkaz = "Your date is free, you can register right now!"
error = "Incorrect date format!"

available_dates = []
keys_to_delete = []

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='bot_db'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
    except Error as e:
        print(f"Error: {e}")
    return connection

def insert_user_info(user_id, user_date):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO User_info (user_id, user_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_date=%s", (user_id, user_date, user_date))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def delete_user_info(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM User_info WHERE user_id=%s", (user_id,))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def get_user_dates():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    user_dates = {}
    try:
        cursor.execute("SELECT user_id, user_date FROM User_info")
        rows = cursor.fetchall()
        for row in rows:
            user_dates[row['user_id']] = row['user_date']
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return user_dates

userdates = get_user_dates()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"Hello, {name}! 👋 \n I will help you choose a date <b> to get a visa </b>. Enter the command /all to get current empty dates. \n Enter the command /my to check the date you selected", parse_mode="HTML")
    bot.reply_to(message, kaz_date)

@bot.message_handler(commands=['rus'])
def send_welcome_rus(message):
    bot.reply_to(message, rus_date)

@bot.message_handler(commands=['all'])
def admin(message):
    available_dates_from_db = load_available_dates_from_db()
    bot.reply_to(message, '📅Свободные даты в настоящее время: \n ' + '\n'.join(available_dates_from_db), parse_mode='HTML')

@bot.message_handler(commands=['my'])
def my(message):
    user_id = message.from_user.id
    if user_id in userdates:
        if userdates[user_id] in available_dates:
            bot.reply_to(message, f"☀ The date choosen: {userdates[user_id]} is not available for registration!")
        else:
            bot.reply_to(message, f"Таңдаған выбранная вами дата: {userdates[user_id]} недоступна для регистрации! Но мы сообщим вам, когда она станет доступной.")
    else:
        bot.reply_to(message, "Please forward me the date first so I can check its availability.")

@bot.message_handler(content_types=['text'])
def echo_message(message):
    try:
        user_date = datetime.datetime.strptime(message.text, '%d:%m:%Y').strftime('%d:%m:%Y')
        userdates[message.from_user.id] = user_date
        if user_date in available_dates:
            bot.reply_to(message, erkaz)
            available_dates.remove(user_date)
        else:
            bot.reply_to(message, nokaz)
            insert_user_info(message.from_user.id, user_date)
    except ValueError:
        bot.reply_to(message, error)

def schedule_updates(driver):
    logged_in = False
    while True:
        try:
            update_available_dates(driver, logged_in)
        except Exception as e:
            print(f"Error during scheduled update: {e}")
        time.sleep(seconds_between_checks)
        logged_in = True

def load_available_dates_from_db():
    connection = create_connection()
    cursor = connection.cursor()
    dates = []
    try:
        cursor.execute("SELECT date FROM Available_dates")
        rows = cursor.fetchall()
        dates = [row[0] for row in rows]
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
    return dates

# Initialize the driver and start the update thread
from parsing import start_driver

driver = start_driver()
update_thread = Thread(target=schedule_updates, args=(driver,))
update_thread.start()

bot.polling(none_stop=True)
