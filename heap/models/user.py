from passlib.hash import bcrypt
from heap import db, app
from sqlalchemy_utils import PasswordType

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(
        PasswordType(
            # The returned dictionary is forwarded to the CryptContext
            onload=lambda **kwargs: dict(
                schemes=app.config['PASSWORD_SCHEMES'],
                **kwargs
            ),
        ),
        unique=False,
        nullable=False,
    )
    sources = db.relationship('Source', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.encrypt(password)

    def dictify(self):
        return {
            'id': self.id,
            'email': self.email
        }

    def __repr__(self):
        return '<User %r>' % self.email

    @staticmethod
    def verify(email, password):
        user = User.query.filter(User.email==email).first()
        return user.password == password
