
import logging
import shodan
import sys
import time



def shodanAPIWrap(apiKey, proxies):
    numberOfTries = 0
    while True:
        locallogger = logging.getLogger(f"{__file__}.shodanAPIWrap")
        api = None
        try:
            api = shodan.Shodan(apiKey, proxies=proxies)
            break
        except Exception as e:
            numberOfTries = numberOfTries + 1
            locallogger.exception(f"Number of tries: {numberOfTries}; Exception details: {e}")
            if numberOfTries >=4:
                locallogger.error(f"Issue with Shodan API.....")
                sys.exit(1)
            time.sleep(5)
    return api

























