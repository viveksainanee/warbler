"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, FollowersFollowee, Reaction, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testuser",
                                     image_url=None)

        self.testuser4 = User.signup(username="testuser4",
                                     email="test4@test.com",
                                     password="testuser",
                                     image_url=None)
        self.testuser.id = 1
        self.testuser2.id = 2
        self.testuser4.id = 4
        db.session.commit()

        self.f = FollowersFollowee(follower_id=1, followee_id=2)
        self.f2 = FollowersFollowee(follower_id=2, followee_id=1)
        self.m = Message(id=1, text="test message", user_id=2)
        self.r = Reaction(user_id=1, message_id=1, reaction_type="sad")

        db.session.add_all([self.f, self.f2, self.m, self.r])
        db.session.commit()

    def test_signup(self):
        """Can use signup?"""
        with self.client as c:

            # test get signup
            resp = c.get("/signup")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Join Warbler today.', resp.data)

            # test post signup

            resp = c.post("/signup", data={"username": "testuser3",
                                           "email": "test3@test.com", "password": "testuser"})

            #  Make sure it redirects
            self.assertEqual(resp.status_code, 302)

    def test_login(self):
        """Can login?"""
        with self.client as c:

            # test login get
            resp = c.get("/login")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Welcome back.', resp.data)

            # test post login

            resp = c.post(
                "/login", data={"username": "testuser", "password": "testuser"})

            #  Make sure it redirects
            self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        """Can logout?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test logout get
            resp = c.get("/logout")
            self.assertEqual(resp.status_code, 302)

    def test_list_users(self):
        """Can list users?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test get
            resp = c.get('/users')
            self.assertIn(b'card-bio', resp.data)

            # test on person
            resp = c.get('/users?q=testuser')
            self.assertIn(b'testuser', resp.data)

    def test_show_user(self):
        """Can show user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test get
            resp = c.get(f'/users/{self.testuser.id}')
            self.assertIn(b'testuser', resp.data)
            self.assertIn(b'Edit Profile', resp.data)

    def test_following_user(self):
        """Can show following user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test get
            resp = c.get(f'/users/{self.testuser.id}/following')
            self.assertIn(b'testuser2', resp.data)

    def test_followers_user(self):
        """Can show followers user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test get
            resp = c.get(f'/users/{self.testuser.id}/followers')
            self.assertIn(b'testuser2', resp.data)

    def test_reaction_user(self):
        """Can show reacted?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test get
            resp = c.get(f'/users/{self.testuser.id}/reactions')
            self.assertIn(b'test message', resp.data)

    def
