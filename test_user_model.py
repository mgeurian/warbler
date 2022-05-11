"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "testuser1@email.com", "password", None)
        user1id = 11111
        u1.id = user1id

        u2 = User.signup("user2", "testuser2@email.com", "password", None)
        user2id = 22222
        u2.id = user2id

        db.session.commit()

        u1 = User.query.get(user1id)
        u2 = User.query.get(user2id)

        self.u1 = u1
        self.user1id = user1id

        self.u2 = u2
        self.user2id = user2id

        self.client= app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="testuser@test.com",
            username="testuser",
            password="password"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):	
        self.assertEqual(repr(self.u1), "<User #11111: user1, testuser1@email.com>")	
        self.assertEqual(repr(self.u2), "<User #22222: user2, testuser2@email.com>")

    def test_signup(self):	
        u3_test = User.signup("user3signup", "testuser3@email.com", "password", None)	
        userid = 99999	
        u3_test.id = userid	
        db.session.commit()	
        user_test = User.query.get(userid)	
        self.assertIsNotNone(u3_test)	
        self.assertEqual(u3_test.username, "user3signup")	
        self.assertEqual(u3_test.email, "testuser3@email.com")	
        self.assertNotEqual(u3_test.password, "hubabaloo")	
        self.assertTrue(u3_test.password.startswith("$2b$"))	

    def test_invalid_username_on_signup(self):	
        bad_user = User.signup(None, "bad@email.com", "password", None)	
        userid = 88888	
        bad_user.id = userid	
        with self.assertRaises(exc.IntegrityError) as context:	
            db.session.commit()	

    def test_invalid_email_on_signup(self):	
        bad_email = User.signup("noemailprovided", None, 'password', None)	
        userid = 66666
        bad_email.id = userid	
        with self.assertRaises(exc.IntegrityError) as context:	
            db.session.commit()	
            
    def test_invalid_password_on_signup(self):	
        with self.assertRaises(ValueError) as context:	
            User.signup("testnullpassword", "test@email.com", "", None)	
        with self.assertRaises(ValueError) as context:	
            User.signup("testnopassword", "test@email.com", None, None)