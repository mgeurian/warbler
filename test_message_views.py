import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):

    def setUp(self):

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser", email="test@test.com", password="testuser", image_url=None)
        self.testuser_id = 1212
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        with self.client as c:
            with c.session_transaction() as sesh:
                sesh[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sesh:
                sesh[CURR_USER_KEY] = 12121212

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_show(self):

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )
        
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            m = Message.query.get(1234)

            resp = c.get(f'/messages/{m.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))
    
    def test_message_delete(self):

        msg = Message(id=1234, text="test message delete", user_id=self.testuser_id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sesh:
                sesh[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            msg1 = Message.query.get(1234)
            self.assertIsNone(msg1)

    def text_unauthorized_message_delete(self):

        user = User.signup(username="unauthorized-user", email="testuser@test.com", password="password", image_url=None)
        user.id = 56789

        msg = Message(id=1234, text="text unauthorized message delete", user_id=self.textuser_id)
        db.session.add_all([user, msg])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sesh:
                sesh[CURR_USER_KEY] = 56789

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            msg = Message.query.get(1234)
            self.assertIsNotNone(msg)

    def test_message_delete_no_authentication(self):

        msg = Message(id=1234, text="test messag delete no authentication", user_id=self.testuser_id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            msg1 = Message.query.get(1234)
            self.assertIsNotNone(msg1)
