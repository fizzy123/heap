from datetime import datetime
from heap import db

class Source(db.Model):
    __tablename__ = 'sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    url = db.Column(db.String(), nullable=False)
    items = db.relationship('Item', backref='source')
    updated = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    refresh_token = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name=None, user_id=None, url=None, refresh_token=None):
        self.name = name
        self.user_id = user_id
        self.url = url
        self.refresh_token = refresh_token

    def dictify(self):
        return {
            'id': self.id,
            'owner': self.user_id,
            'name': self.name,
            'url': self.url,
            'updated': self.updated.isoformat(),
            'refresh_token': self.refresh_token
        }

    def __repr__(self):
        return '<Source %r>' % self.name
