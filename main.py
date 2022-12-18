import logging
import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
import configparser
import os
import sys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued."""
    message = """
    Hi! You can use this command to get the usage of this bot.
    /list : list of command
    /help : usage instructions

    """
    update.message.reply_text(message)

def list_command(update, context):
    """list of command"""
    usage = """
    /help
    /add
    /date
    /month
    /year
    /show_date
    /show_month
    /show_year
    /all

    """
    update.message.reply_text(usage)

def help(update, context):
    """Send a message with usage instructions."""
    usage = """
    Welcome to the expense tracker bot!

    Hi there! I'm a personal finance bot that develop by Liew Chun Kit, I can help you track your expenses. Here's how to use me:

    - To add a new expense, use the /add command followed by the date (in YYYY-MM-DD format), a description (using _ to combine the word), and the amount (in dollars). For example: "/add 2022-12-18 Food_Order 200"
    - To see your expenses for a specific date, use the /date command followed by the date. For example: "/expenses_by_date 2022-12-18"
    - To see your total expenses for the month, use the /month command followed by the month and year. For example: "/expenses_by_month 2022-12"
    - To see your total expenses for the year, use the /year command followed by the year. For example: "/expenses_by_year 2022"
    - To see your expenses record for a specific date, use the /show_date command followed by the date. For example: "/show_date 2022-12-18"
    - To see your expenses record for a the month, use the /show_month command followed by the date. For example: "/show_month 2022-12"
    - To see your expenses record for a the year, use the /show_year command followed by the date. For example: "/show_year 2022"
    - To see all the expenses record, use the /all command. For example: "/all"

    I hope this helps!

    """
    update.message.reply_text(usage)

def add_expense(update, context):
    """Save an expense."""
    # Extract the date, description, and expense from the user input
    expense_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\w+)\s+(\d+(?:,\d+)*(?:\.\d+)?)")
    expense_match = expense_pattern.search(update.message.text)

    if expense_match:
        date = expense_match.group(1)
        description = expense_match.group(2)
        expense = float(expense_match.group(3))
    else:
        update.message.reply_text("Invalid expense format. Please use YYYY-MM-DD DESCRIPTION AMOUNT.")
        return

    # Read the Excel file
    df = pd.read_excel("expenses.xlsx")

    # Append the new expense to the DataFrame
    df = pd.concat([df, pd.DataFrame.from_records([{"date": date, "description": description, "expense": expense}])])

    # Save the updated DataFrame to the Excel file
    df.to_excel("expenses.xlsx", index=False)

    # Confirm the expense has been saved
    update.message.reply_text("Expense saved.")

def show_expenses_chunk(update, context):
    """Show all expenses on chunk."""
    # Read the Excel file
    df = pd.read_excel("expenses.xlsx")

    # Convert the DataFrame to a dictionary
    expenses = df.to_dict(orient="records")

    # Build the message
    message = "Expenses:\n"
    for expense in expenses:
        message += "- {}: {} ({})\n".format(expense["date"], expense["description"], expense["expense"])

    # Send the message in chunks
    for chunk in chunks(message, 1024):
        update.message.reply_text(chunk)

def chunks(string, chunk_size):
    """Split a string into chunks of the specified size."""
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]

def expenses_by_date(update, context):
    """Calculate total expenses for a specified date."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY-MM-DD.")
        return

    expenses(update, context, date)

def expenses_by_month(update, context):
    """Calculate total expenses for a specified month."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}-\d{2}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY-MM.")
        return

    expenses(update, context, date)

def expenses_by_year(update, context):
    """Calculate total expenses for a specified year."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY.")
        return

    expenses(update, context, date)

def expenses(update, context, date):
    # Read the Excel file
    df = pd.read_excel("expenses.xlsx")

    # Filter expenses for the specified date
    expenses_by_date = df[df['date'].str.startswith(date)]

    # Calculate the total expenses for the specified date
    total_expenses = expenses_by_date["expense"].sum()

    # Return the total expenses
    update.message.reply_text(f"Total expenses for {date}: {total_expenses}")

def show_expenses_by_date(update, context):
    """Show expenses for a specified date."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY-MM-DD.")
        return

    show(update, context, date)

def show_expenses_by_month(update, context):
    """Show expenses for a specified month."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}-\d{2}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY-MM.")
        return

    show(update, context, date)

def show_expenses_by_year(update, context):
    """Show expenses for a specified year."""
    # Extract the date from the user input
    date_pattern = re.compile(r"\d{4}")
    date_match = date_pattern.search(update.message.text)

    if date_match:
        date = date_match.group()
    else:
        update.message.reply_text("Invalid date format. Please use YYYY.")
        return

    show(update, context, date)

def show(update, context, date):
    # Read the Excel file
    df = pd.read_excel("expenses.xlsx")

    # Filter expenses for the specified date
    expenses_by_date = df[df['date'].str.startswith(date)]

    expenses = expenses_by_date.to_dict(orient="records")

    # Build the message
    message = "Expenses:\n"
    for expense in expenses:
        message += "- {}: {} ({})\n".format(expense["date"], expense["description"], expense["expense"])

    # Send the message in chunks
    for chunk in chunks(message, 4096):
        update.message.reply_text(chunk)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Check if the Excel file exists
    if not os.path.exists("expenses.xlsx"):
        # Create an empty Excel file
        df = pd.DataFrame(columns=["date", "description", "expense"])
        df.to_excel("expenses.xlsx", index=False)

    """Start the bot."""

    """ Conten in config.txt should be
    [telegram]
    bot_token = YOUR_BOT_TOKEN
    """
    # Check if the config file exists
    if not os.path.exists("config.txt"):
        print("Config file not exists!! Creating for you")
        # Create the config file
        config = configparser.ConfigParser()
        config["telegram"] = {"bot_token": "YOUR_BOT_TOKEN"}
        with open("config.txt", "w") as config_file:
            config.write(config_file)
        # Exit the program
        sys.exit()

    # Read the config file
    config = configparser.ConfigParser()
    config.read("config.txt")
    
    # Extract the bot token from the config file
    bot_token = config.get("telegram", "bot_token")

    updater = Updater(bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", list_command))
    dp.add_handler(CommandHandler("help", help))
    # show total expenses by specifi time
    dp.add_handler(CommandHandler("date", expenses_by_date))
    dp.add_handler(CommandHandler("month", expenses_by_month))
    dp.add_handler(CommandHandler("year", expenses_by_year))
    # show all expenses record
    dp.add_handler(CommandHandler("all", show_expenses_chunk))
    # dp.add_handler(CommandHandler("show_expenses_chunk", show_expenses_chunk))
    # show expenses record by time
    dp.add_handler(CommandHandler("show_date", show_expenses_by_date))
    dp.add_handler(CommandHandler("show_month", show_expenses_by_month))
    dp.add_handler(CommandHandler("show_year", show_expenses_by_year))
    # add expenses record
    dp.add_handler(CommandHandler("add", add_expense))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()