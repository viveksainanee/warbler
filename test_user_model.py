"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Reaction.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u=User.signup(username="testuser", email="test@test.com", password="HASHED_PASSWORD", image_url="/static/images/default-pic.png")
        u.id = 1
        u2=User.signup(username="testuser2", email="test2@test.com", password="HASHED_PASSWORD", image_url="/static/images/default-pic.png")
        u2.id = 2

        db.session.commit()

        m=Message(id=1,text="test message",user_id=1)
        r=Reaction(user_id=1, message_id=1, reaction_type="sad")
        f=FollowersFollowee(follower_id=1,followee_id=2)
        f2=FollowersFollowee(follower_id=2,followee_id=1)


        db.session.add(m)
        db.session.add(r)
        db.session.add(f)
        db.session.add(f2)

        db.session.commit()

        # User should have 1 message and 1 follower and 1 following
        self.assertEqual(u.messages.count(), 1)
        self.assertEqual(u.followers.count(), 1)
        self.assertEqual(u.following.count(), 1)

        db.session.delete(f)
        db.session.commit()

        # User should have 0 follower and 1 following
        self.assertEqual(u.followers.count(), 0)
        self.assertEqual(u.following.count(), 1)

        db.session.delete(f2)
        db.session.commit()

        # User should have 0 follower and 0 following
        self.assertEqual(u.followers.count(), 0)
        self.assertEqual(u.following.count(), 0)



        #testing attributes
        self.assertNotEqual(u.password,"HASHED_PASSWORD")
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.image_url, "/static/images/default-pic.png")
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.bio, None)
        self.assertEqual(u.header_image_url, "/static/images/warbler-hero.jpg")
        self.assertEqual(u.location, None)


        #test get_reactions
        self.assertEqual(len(u.get_reactions("sad")), 1)
        self.assertFalse(u.get_reactions("angry"))
        self.assertFalse(u.get_reactions("smile"))
        self.assertFalse(u.get_reactions("laugh"))

        #test get my messages
        self.assertEqual(len(u.get_my_messages()), 1)

        
        # test auth 
        u= User.authenticate(u.username, "HASHED_PASSWORD")
        self.assertTrue(u)

        u= User.authenticate(u.username, "asdfasdf")
        self.assertFalse(u)







        





    
    def tearDown(self):
        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()
        Reaction.query.delete()

