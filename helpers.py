import string, secrets
from globals import SHORT_URL_LENGTH

def shortenUrl(long_url):
    shortenedUrl = ("").join(secrets.choice(string.ascii_letters + string.digits) for _ in range(SHORT_URL_LENGTH))
    return shortenedUrl

def row2dict(row):
    newDict = {}
    for column in row.__table__.columns:
        newDict[column.name] = str(getattr(row, column.name))

    return newDict