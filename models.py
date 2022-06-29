from main import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from globals import MAX_LENGTH_URL, SHORT_URL_LENGTH

db = SQLAlchemy(app)

# TODO - simplify DB calls. one function for a query, then chain queries together where longer, more specific
# tasks are required

class Url(db.Model):
    original_url = db.Column(db.String(MAX_LENGTH_URL), primary_key=True)
    shortened_url = db.Column(db.String(SHORT_URL_LENGTH))
    hits = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "'{\"url\": \"%s\", \"shortcode\": \"%s\", \"hits\":  \"%s\", \"created at\": \"%s\"}'" % (self.original_url, self.shortened_url, self.hits, self.created_at)

db.create_all()

# First the field that we are searching for, then the match that we want to filter by, then the response (piece of data) that we need
def query_db(field, filterby, response="all"):
    if (response == "all"):
        result = Url.query.filter(getattr(Url,field)==filterby).first()
    else:
        result = db.session.query(getattr(Url,response)).filter(getattr(Url,field)==filterby).all()
    return result

# TODO - wrap in try/catch
def add_db(original_url, shortened_url):
    new_url = Url(original_url=original_url, shortened_url=shortened_url, hits=0)
    db.session.add(new_url)
    db.session.commit()

def add_to_hits(original_url):
    db.session.query(Url).filter(Url.original_url == original_url).update({'hits': Url.hits + 1})
    db.session.commit()
