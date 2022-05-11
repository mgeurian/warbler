import os
from socket import MSG_EOR
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
  def setUp(self):
    db.drop_all()
    db.create_all()

    self.uid = 12345
    u = User.signup("testing", "testing@test.com", "password", None)
    u.id = self.uid
    db.session.commit()

    self.u = User.query.get(self.uid)
    self.client = app.test_client()
    
  def tearDown(self):
    res = super().tearDown()
    db.session.rollback()
    return res
  
  def test_message_model(self):
    msg=Message(text="warble warble warble", user_id=self.uid)

    db.session.add(msg)
    db.session.commit()

    self.assertEqual(len(self.u.messages), 1)
    self.assertEqual(self.u.messages[0].text, "warble warble warble")

  def test_message_likes(self):
    msg1 = Message(text="warble like you mean it", user_id=self.uid)

    msg2 = Message(text="warble like you don't care", user_id=self.uid)

    user1 = User.signup("yetanothertest", "t@email.com", "password", None)
    uid = 111
    user1.id = uid
    db.session.add_all([msg1, msg2, user1])
    db.session.commit()

    user1.likes.append(msg1)
    db.session.commit()

    allLikes = Likes.query.filter(Likes.user_id == uid).all()
    self.assertEqual(len(allLikes), 1)
    self.assertEqual(allLikes[0].message_id, msg1.id)