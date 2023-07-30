from datetime import datetime


def getTime():
    now = datetime.now()
    currentTime = now.strftime("%m/%d/%y | %H:%M:%S")
    return currentTime
