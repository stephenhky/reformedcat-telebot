
import json

import requests


async def retrieve_single_verse(url, book, chapter, verse, translation, booknameset):
    payload = json.dumps({
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "translation": translation,
        "booknameset": booknameset
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


async def retrieve_verses(url, book, startchapter, startverse, endchapter, endverse, translation, booknameset):
    payload = json.dumps({
        "book": book,
        "startchapter": startchapter,
        "startverse": startverse,
        "endchapter": endchapter,
        "endverse": endverse,
        "translation": translation,
        "booknameset": booknameset
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)
