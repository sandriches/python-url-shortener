import json, os
from flask import Flask, request, Response
from helpers import shortenUrl, row2dict
from globals import MAX_LENGTH_URL

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["DEBUG"] = True

# Prevents circular dependencies
from models import query_db, add_db, add_to_hits

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

def lookupStats(shortcode):
    result = query_db("shortened_url", shortcode)
    return result


@app.route('/shorten', methods=['POST'])
def shorten():
    # Check if request has correct params
    if (request.args.get('URL') and len(request.args.get('URL')) < MAX_LENGTH_URL):
        # Check if already exists
        alreadyShortenedUrl = lookupExistingUrl(request.args['URL'])
        if (alreadyShortenedUrl):
            return Response(status=303, response="Location: /urls/" + alreadyShortenedUrl)

        # Shorten and add to DB
        shortenedUrl = shortenUrl(request.args['URL'])
        add_db(request.args['URL'], shortenedUrl)
        return Response(status=201, response="New location: " + shortenedUrl)

    return Response(status=404, response="Non-existant URL or URL too long. Max length: " + str(MAX_LENGTH_URL))


@app.route('/urls/<url>', methods=['GET'])
def getUrls(url):
    originalUrl = isShortenedUrl(url)
    if not originalUrl:
        return Response(status=404, response="Shortcode URL doesn't exist")

    # Increase hits count
    add_to_hits(originalUrl)
    return Response(status=307, response="Original URL: " + originalUrl)

@app.route('/stats/<shortcode>')
def getStats(shortcode):
    if (isShortenedUrl(shortcode)):
        # Convert to JSON for response
        response = row2dict(lookupStats(shortcode))
        return Response(json.dumps(response), status=200, mimetype='application/json')
    return Response(status=404, response="Url doesn't exist")

@app.errorhandler(404) 
def default_handler(e):
    return Response(status=404, response='Endpoint does not exist')


if __name__ == '__main__':
    app.run()
