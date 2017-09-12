from heap import db

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    url = db.Column(db.String(), nullable=False)
    read = db.Column(db.Boolean(), default=False, nullable=False)
    starred = db.Column(db.Boolean(), default=False, nullable=False)
    x_frame_options = db.Column(db.Boolean(), default=False, nullable=False)

    def get_owner(self):
        return self.source.owner

#pylint: disable=too-many-arguments
    def __init__(self, url, source=None, read=False, starred=False, x_frame_options=False):
        self.url = url
        self.source = source
        self.read = read
        self.starred = starred
        self.x_frame_options = x_frame_options

    def dictify(self):
        return {
            'id': self.id,
            'owner': self.source.owner.id,
            'source': self.source.id,
            'url': self.url,
            'read': self.read,
            'starred': self.starred,
            'x_frame_options': self.x_frame_options
        }

    def __repr__(self):
        return '<Item %r>' % self.url
