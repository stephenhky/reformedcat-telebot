
import logging
import os
import re
import asyncio
import json

from dotenv import load_dotenv
import telebot
from reformedcatutils.biblebooks import books2idx, otbookdict, ntbookdict

from utils.retrieval import retrieve_single_verse, retrieve_verses


logging.basicConfig(level=logging.INFO)

load_dotenv()

# Telebot API Key
api_key = os.getenv('APIKEY')
bot = telebot.TeleBot(api_key, threaded=False)

# Retrieval URL
retrieval_api_url = os.getenv('RETRIEVALAPI')


@bot.message_handler(commands=['help'])
def help(message):
    logging.info(message)

    returntext = '\n'.join(
        [
            '/greet : say Hello!',
            '/index : abbreviation of all books in the Bible',
            '/otindex : abbreviation of all books in the Old Testament',
            '/ntindex : abbreviation of all books in the New Testament',
            '/rb : display verses with given book, start chapter, start verse, (end chapter, end verse)'
        ]
    )
    bot.send_message(message.chat.id, returntext)


@bot.message_handler(commands=['index'])
def show_books_index(message):
    logging.info(message)
    returntext = '\n'.join(
        '{}: {}'.format(key, bookname) for key, bookname in otbookdict.items()
    ) + '\n' + \
    '\n'.join(
        '{}: {}'.format(key, bookname) for key, bookname in ntbookdict.items()
    )
    bot.reply_to(message, returntext)


@bot.message_handler(commands=['otindex'])
def show_otbooks_index(message):
    logging.info(message)
    returntext = '\n'.join(
        '{}: {}'.format(key, bookname) for key, bookname in otbookdict.items()
    )
    bot.reply_to(message, returntext)


@bot.message_handler(commands=['ntindex'])
def show_ntbooks_index(message):
    logging.info(message)
    returntext = '\n'.join(
        '{}: {}'.format(key, bookname) for key, bookname in ntbookdict.items()
    )
    bot.reply_to(message, returntext)


@bot.message_handler(commands=['greet'])
def greet(message):
    logging.info(message)
    bot.reply_to(message, 'Hey, how is it going?')


@bot.message_handler(regexp='[Hh]ello*')
def hello(message):
    logging.info(message)
    bot.send_message(message.chat.id, "Hello!")


@bot.message_handler(regexp='[Bb]ye[!]?')
def sayonara(message):
    logging.info(message)
    bot.send_message(message.chat.id, "Have a nice day!")


@bot.message_handler(commands=['rb'])
def handling_stockcorrelation_message(message):
    logging.info(message)
    stringlists = re.sub('\s+', ' ', message.text).split(' ')[1:]

    book = stringlists[0]
    if not (book in books2idx):
        bot.reply_to(message, 'Unknown book abbreviation: {}'.format(book))

    startchapter = stringlists[1]
    startverse = stringlists[2]
    try:
        startchapter = int(startchapter)
        startverse = int(startverse)
    except ValueError:
        bot.reply_to(message, 'Invalid chapter or verse: {}:{}'.format(startchapter, startverse))

    if len(stringlists) >= 5:
        endchapter = stringlists[3]
        endverse = stringlists[4]
        try:
            endchapter = int(endchapter)
            endverse = int(endverse)
        except ValueError:
            bot.reply_to(message, 'Invalid chapter or verse: {}:{}'.format(endchapter, endverse))
        result = asyncio.run(
            retrieve_verses(
                retrieval_api_url,
                book,
                startchapter,
                startverse,
                endchapter,
                endverse,
                'ESVBible',
                'EnglishTraditional'
            )
        )
    else:
        result = asyncio.run(
            retrieve_single_verse(
                retrieval_api_url,
                book,
                startchapter,
                startverse,
                'ESVBible',
                'EnglishTraditional'
            )
        )

    returntext = '{} ({} {})'.format(result['text'], result['bookname'], result['verseref'])
    bot.reply_to(message, returntext)


def lambda_handler(event, context):
    message = json.loads(event['body'])
    logging.info(message)
    print(message)
    if message.get('polling', False):
        bot.polling()
        return {
            'statusCode': 200,
            'body': 'Lambda executed with polling'
        }
    else:
        update = telebot.types.Update.de_json(message)
        logging.info(update)
        print(update)
        bot.process_new_messages([update.message])
        return {
            'statusCode': 200,
            'body': 'Lambda executed as a webhook'
        }


if __name__ == '__main__':
    bot.polling()

# Reference: how to set up webhook: https://aws.plainenglish.io/develop-your-telegram-chatbot-with-aws-api-gateway-dynamodb-lambda-functions-410dcb1fb58a
