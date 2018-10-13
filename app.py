import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message, Reaction, Thread, DM

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.data['username'],
                password=form.data['password'],
                email=form.data['email'],
                image_url=form.data['image_url'] or None,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.data['username'],
                                 form.data['password'])

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash('Logged out successfully.', 'success')
    return redirect("/login")


##############################################################################
# General user routes:

#### DELETE AFTER IF NOT NEEDED ############
# @app.route('/getcurrentuser')
# def get_curr_user():
#     return jsonify({'user': session[CURR_USER_KEY]})


@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    reactions_number = len(user.reacted_messages)
    return render_template('users/show.html', user=user, reactions_number=reactions_number)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    reactions_number = len(user.reacted_messages)

    return render_template('users/following.html', user=user, reactions_number=reactions_number)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    reactions_number = len(user.reacted_messages)

    return render_template('users/followers.html', user=user, reactions_number=reactions_number)


@app.route('/users/<int:user_id>/reactions')
def users_reactions(user_id):
    """Show list of reactions of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    messages = user.reacted_messages

    sad = g.user.get_reactions("sad")
    smile = g.user.get_reactions("smile")
    laugh = g.user.get_reactions("laugh")
    angry = g.user.get_reactions("angry")

    reaction_types = {"fa-smile": smile,
                      "fa-sad-cry": sad,
                      "fa-laugh-squint": laugh,
                      "fa-angry": angry}

    return render_template('users/reactions.html', user=user, messages=messages, reaction_types=reaction_types, reactions_number=len(messages))


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get_or_404(follow_id)
    g.user.following.append(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followee = User.query.get(follow_id)
    g.user.following.remove(followee)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    # if user is logged in
    if g.user:
        # if they subbmited the form
        # user = User.query.get_or_404(session[CURR_USER_KEY])
        form = UserEditForm(obj=g.user)

        if form.validate_on_submit():
            # validate password
            if User.authenticate(g.user.username, request.form["password"]):
                g.user.username = request.form["username"]
                g.user.email = request.form["email"]
                g.user.image_url = request.form["image_url"] or None
                g.user.header_image_url = request.form["header_image_url"] or None
                g.user.bio = request.form["bio"] or None
                db.session.commit()
                flash("Sucessfully updated", "success")
                return redirect(f"users/{g.user.id}")
            else:
                flash("Wrong password!", "danger")
                return redirect("/users/profile")
        else:
            return render_template("/users/edit.html", form=form, user_id=g.user.id)
    else:
        flash('Please login', "info")
        redirect("/login")


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.data['text'])
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

##############################################################################
# Reaction routes:


@app.route('/addreaction', methods=["POST"])
def add_reaction():
    """Add reaction to DB"""
    if not g.user:
        flash("Unauthorized to complete action", "danger")
        return redirect("/")

    reaction_type = request.json["type"]
    msg_id = request.json["msgId"]
    reaction = Reaction(user_id=g.user.id, message_id=msg_id,
                        reaction_type=reaction_type)
    db.session.add(reaction)
    db.session.commit()
    return jsonify({'msg': 'Added Reaction!'})


@app.route('/deletereaction', methods=["DELETE"])
def delete_reaction():
    """Delete reaction to DB"""
    if not g.user:
        flash("Unauthorized to complete action", "danger")
        return redirect("/")
    reaction_type = request.json["type"]
    msg_id = request.json["msgId"]
    reaction = Reaction.query.get((g.user.id, msg_id, reaction_type))
    db.session.delete(reaction)
    db.session.commit()
    return jsonify({'msg': 'Deleted Reaction!'})

##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followees
    """

    if g.user:
        following_ids = [f.id for f in g.user.following] + [g.user.id]

        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        sad = g.user.get_reactions("sad")
        smile = g.user.get_reactions("smile")
        laugh = g.user.get_reactions("laugh")
        angry = g.user.get_reactions("angry")

        my_msgs = g.user.get_my_messages()

        reaction_types = {"fa-smile": smile,
                          "fa-sad-cry": sad,
                          "fa-laugh-squint": laugh,
                          "fa-angry": angry}

        return render_template('home.html', messages=messages, reaction_types=reaction_types, my_msgs=my_msgs)

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# Thread and DM pages


@app.route('/threads')
def list_threads():
    """Page with listing of threads.
    """
    # query the threads where I'm user 1
    my_user1_threads = Thread.query.filter(Thread.user1_id == g.user.id).all()
    # query the threads where I'm user 2
    my_user2_threads = Thread.query.filter(Thread.user2_id == g.user.id).all()
    return render_template('threads.html', my_user1_threads=my_user1_threads, my_user2_threads=my_user2_threads)

    # get all the users talk to me
    # get all the users i'm talking to

    # for in the combined list

    # look up their thread
    # put it in [[user, thread], [user, thread]]


@app.route('/threads/add/<int:user_id>', methods=['POST'])
def add_thread(user_id):
    """Page to add a thread. """
    # if this user id combo exists
    thread = Thread.query.filter(
        Thread.user1_id == user_id, Thread.user2_id == g.user.id).all()

    thread2 = Thread.query.filter(
        Thread.user2_id == user_id, Thread.user1_id == g.user.id).all()

    if thread:
        return redirect(f'threads/{thread[0].id}')

    if thread2:
        return redirect(f'threads/{thread2[0].id}')

    # else:
    if (user_id < g.user.id):
        new_thread = Thread(user1_id=user_id, user2_id=g.user.id)
    else:
        new_thread = Thread(user1_id=g.user.id, user2_id=user_id)
    db.session.add(new_thread)
    db.session.commit()
    return redirect(f'threads/{new_thread.id}')


@app.route('/threads/<int:thread_id>')
def show_thread(thread_id):
    """Page to see a thread. """
    thread = Thread.query.get(thread_id)
    if g.user.id == thread.user1_id or g.user.id == thread.user2_id:
        if (g.user.id == thread.user1_id):
            other_username = thread.user2.username
        else:
            other_username = thread.user1.username

        return render_template("show-thread.html", thread=thread, other_username=other_username)
    else:
        flash('Unauthorized', 'danger')
        return redirect('/')


@app.route('/threads/<int:thread_id>/dm/add', methods=["POST"])
def add_dm(thread_id):
    """adds a dm"""
    thread = Thread.query.get(thread_id)
    text = request.json["text"]
    dm = DM(text=text, thread_id=thread_id, author=g.user.id)
    db.session.add(dm)
    db.session.commit()
    all_dms = [[dm.text, dm.author] for dm in thread.dms]
    return jsonify(all_dms)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
