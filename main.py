import os
from datetime import date
from flask import Flask, request, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import string, secrets

# TODO - tests

SHORT_URL_LENGTH=5
MAX_LENGTH_URL=50

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)
app.config["DEBUG"] = True


class Url(db.Model):
    original_url = db.Column(db.String(MAX_LENGTH_URL), primary_key=True)
    shortened_url = db.Column(db.String(SHORT_URL_LENGTH))
    hits = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # TODO - check best practice for repr
    def __repr__(self):
        return "(Original Url: %s, Shortened Url: %s, Hits:  %s, Created At: %s)" % (self.original_url, self.shortened_url, self.hits, self.created_at)

db.create_all()

# Response here is the part of the query we need
def query_db(field, filterby, response="all"):
    if (response == "all"):
        result = db.session.query(getattr(Url,field)==filterby).all()
        # result = Url.query.filter(getattr(Url,field)==filterby).all()
    else:
        result = db.session.query(getattr(Url,response)).filter(getattr(Url,field)==filterby).all()
    return result

def add_db(original_url, shortened_url):
    new_url = Url(original_url=original_url, shortened_url=shortened_url, hits=0)
    db.session.add(new_url)
    db.session.commit()

def isShortenedUrl(shortcode):
    result = query_db("shortened_url", shortcode, "original_url")
    if result:
        return "".join(result[0])
    return False

def lookupExistingUrl(long_url):
    result = query_db("original_url", long_url, "shortened_url")
    if result:
        return "".join(result[0])
    return False

def shortenUrl(long_url):
    shortenedUrl = ("").join(secrets.choice(string.ascii_letters + string.digits) for _ in range(SHORT_URL_LENGTH))
    return shortenedUrl

# TODO - lookup info from DB
def lookupStats(shortcode):
    return query_db("shortened_url", shortcode)


@app.route('/shorten', methods=['POST'])
def shorten():
    # Check if request has correct params
    if (request.args['URL']):
        # Check if already exists
        alreadyShortenedUrl = lookupExistingUrl(request.args['URL'])
        if (alreadyShortenedUrl):
            return Response(status=303, response="Location: /urls/" + alreadyShortenedUrl)
            # return redirect(location=alreadyShortenedUrl, code=303)

        # Shorten and add to DB
        shortenedUrl = shortenUrl(request.args['URL'])
        add_db(request.args['URL'], shortenedUrl)
        return Response(status=201, response="New location: " + shortenedUrl)

    # Error handling - no url
    return Response(status=404, response="no url m8")


@app.route('/urls/<url>', methods=['GET'])
def getUrls(url):
    originalUrl = isShortenedUrl(url)
    if not originalUrl:
        # Change to 404 when done
        return Response(status=204, response="URL doesn't exist")
    # Add redirect
    # TODO - update hits
    return Response(status=307, response="Original URL: " + originalUrl)
    # return redirect(originalUrl, code=307)


@app.route('/stats/<shortcode>')
# TODO - error handling
def getStats(shortcode):
    return lookupStats(shortcode)


if __name__ == '__main__':
    app.run()
