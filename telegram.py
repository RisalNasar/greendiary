

import logging
import json
import datetime


import common.v2.core as core




def sendTelegramMessage(message, chatID, apiKey, parse_mode="Markdown", disableNotification=False):
    locallogger = logging.getLogger(f'{__name__}.sendTelegramMessage')
    locallogger.info(f"Sending Telegram Message: {message}")
    responses = {}
    headers = {'Content-Type': 'application/json',
                'Proxy-Authorization': 'Basic base64'}
    data_dict = {'chat_id': chatID,
                    'text': message,
                    'parse_mode': parse_mode,
                    'disable_notification': False}
    data = json.dumps(data_dict)
    url = f'https://api.telegram.org/bot{apiKey}/sendMessage'
    try:
        response = core.getResponseFromURL(url=url, method='POST', headers=headers,  proxies=None, data=data, verify=False, timeout=120, loggingPrefix=locallogger.name, maxRetry=3)
    except Exception as e:
        response = None
    return response




def sendTelegramPhoto(chatID, apiKey, filePath):
    locallogger = logging.getLogger(f'{__name__}.sendTelegramPhoto')
    responses = {}
    data_dict = {
        'chat_id': chatID,
    }
    files = {
        'photo': open(filePath, 'rb')
    }
    url = f'https://api.telegram.org/bot{apiKey}/sendPhoto'
    try:
        response = core.getResponseFromURL(url=url, method='POST',  proxies=None, data=data_dict, verify=False, timeout=120, loggingPrefix=locallogger.name, maxRetry=3, files=files)
    except Exception as e:
        response = None
    return response



def sendHeartBeat(messageText, apiKey, chatID):
    nowTime = datetime.datetime.now()
    timeString = nowTime.strftime("%H:%M:%S  %d-%b-%Y")
    finalMessageText = f"{timeString}: {messageText}"
    response = sendTelegramMessage(message=finalMessageText, chatID=chatID, apiKey=apiKey)     





































