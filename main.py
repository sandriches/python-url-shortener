from datetime import date
from flask import Flask, request, Response, redirect
from flask_sqlalchemy import SQLAlchemy
import string, secrets

# TODO - tests

SHORT_URL_LENGTH=5
MAX_LENGTH_URL=50

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config["DEBUG"] = True


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.string(MAX_LENGTH_URL))
    shortened_url = db.Column(db.string(SHORT_URL_LENGTH))
    hits = db.Column(db.Integer)
    created_on = db.Column(db.DateTime)

    # TODO - check best practice for repr
    def __repr__(self):
        return "(%s, %s, %s, %s, %s)" % (self.id, self.original_url, self.shortened_url, self.hits, self.created_on)
        # return '%s %s %s %s %s' % (
        #     self.__class__.__name__, self.urlconf_name, self.app_name,
        #     self.namespace, self.regex.pattern)

def isShortenedUrl(shortcode):
    # Check DB for url, if so return original url, else return false
    return "https://www.google.com"

def isAlreadyShortened(long_url):
    # TODO
    # return False
    return "https://www.google.com"

def shortenUrl(long_url):
    shortenedUrl = ("").join(secrets.choice(string.ascii_letters + string.digits) for _ in range(SHORT_URL_LENGTH))
    db.session.add(Url(1, long_url, shortenedUrl))
    db.session.commit()
    return shortenedUrl

# TODO - lookup info from DB
def lookupStats(shortcode):
    db.session.query(Url).filter_by(shortened_url == shortcode)
    # Url.query.filter(shortened_url == shortcode)
    return {"hits": 1, "url": "some_url.com", "createdOn": date(year=2022, month=6, day=26)}


@app.route('/shorten', methods=['POST'])
def shorten():
    if (request.args['URL']):
        alreadyShortenedUrl = isAlreadyShortened(request.args['URL'])
        if (alreadyShortenedUrl):
            # TODO - add redirect to existing url
            return redirect(location=alreadyShortenedUrl, code=303)

        # Check if url is already shortened - TODO
        return Response(status=201, response="New location: " + shortenUrl(request.args['URL']))
    return "no url m8"


@app.route('/urls/<url>', methods=['GET'])
def getUrls(url):
    originalUrl = isShortenedUrl(url)
    if not originalUrl:
        # Change to 404 when done
        return Response(status=204, response="URL doesn't exist")
    # Add redirect
    return redirect(originalUrl, code=307)


@app.route('/stats/<shortcode>')
# TODO - error handling
def getStats(shortcode):
    return lookupStats(shortcode)


if __name__ == '__main__':
    app.run()
