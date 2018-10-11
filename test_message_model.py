"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from datetime import datetime

from models import db, User, Message, FollowersFollowee, Reaction

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Reaction.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        u=User.signup(username="testuser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/default-pic.png")
        u.id = 1

        db.session.commit()

        m=Message(id=1,text="test message",user_id=1)

        db.session.add(m)

        db.session.commit()

        # User should have 1 message and 1 follower and 1 following

        self.assertEqual(u.messages.count(), 1)


        #testing attributes
        self.assertEqual(m.text,"test message")
        self.assertEqual(m.user_id, 1)
        self.assertTrue(m.timestamp<=datetime.utcnow())


    
    def tearDown(self):
        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Reaction.query.delete()

