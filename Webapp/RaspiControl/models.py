from RaspiControl import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phonenumber = db.Column(db.Integer, unique=True, nullable=False)
    provider = db.Column(db.String(60), unique=False, nullable=False)

    def get_reset_token(self, expires_sec=1800): # 30 minutes until token expires
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):    
        s = Serializer(app.config["SECRET_KEY"])
        print("s:", s)
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')" 

class Appliances(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    appliance_1 = db.Column(db.Boolean, default=False)