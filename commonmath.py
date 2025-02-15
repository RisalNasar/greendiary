

import random
import string



def getRandomAlphaNumericString(length):
    stringValue = ''
    length = int(length)
    stringValue = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))
    return stringValue
    









