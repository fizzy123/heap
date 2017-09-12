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

    def __init__(self, name, owner, url):
        self.name = name
        self.owner = owner
        self.url = url

    def dictify(self):
        return {
            'id': self.id,
            'owner': self.owner.id,
            'name': self.name,
            'url': self.url,
            'updated': self.updated.isoformat()
        }

    def __repr__(self):
        return '<Source %r>' % self.name
