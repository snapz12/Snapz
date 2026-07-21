import sqlite3
import os
import base64
from flask import Flask, request, session, redirect, url_for
import time
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask import Flask, render_template, request, redirect, session, jsonify
from flask import Flask, render_template, request, session, jsonify
from flask import *
import smtplib
from email.mime.text import MIMEText
import random
from flask import session
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit, join_room, leave_room
import cloudinary
import cloudinary.uploader
from flask import redirect
from flask import send_from_directory
from flask import request, jsonify

REELS = []

app = Flask(__name__, static_folder="static")
app.secret_key = "snapz123"


socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

cloudinary.config(
    cloud_name="riwhnyql",
    api_key="962575776577664",
    api_secret="krJQRV7ayw1ki57pUdQtjJl0reY",
    secure=True
)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = "snapzofflicial0@gmail.com"
app.config["MAIL_PASSWORD"] = "hmwczqojooyjrvte"
app.config["MAIL_DEFAULT_SENDER"] = "snapzofflicial0@gmail.com"

mail = Mail(app)

def send_otp(receiver_email, otp):

    msg = Message(
        subject="Snapz Password Reset OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[receiver_email]
    )

    msg.body = f"""
Your Snapz OTP is: {otp}

This OTP is valid for 5 minutes.
"""

    mail.send(msg)

conn = sqlite3.connect('snapz.db', check_same_thread=False)
cur = conn.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, name TEXT, bio TEXT, profile_pic TEXT)''')
conn.commit()



UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"]="uploads"


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def init_db():
    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(posts)")
    print(cur.fetchall())

    cur.execute("PRAGMA table_info(reels)")
    print(cur.fetchall())

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE, 
                    password TEXT, 
                    name TEXT, 
                    bio TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    sender TEXT, 
                    receiver TEXT, 
                    message TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT, 
                    image TEXT, 
                    caption TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS reels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT, 
                    video TEXT, 
                    caption TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT, 
                    image TEXT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_to TEXT, 
                    user_from TEXT, 
                    action TEXT, 
                    post_id INTEGER, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')


    cur.execute("""
    CREATE TABLE IF NOT EXISTS followers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      follower_username TEXT,
      followed_username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        post_id INTEGER
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS reel_comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reel_id INTEGER,
        username TEXT,
        comment TEXT
    )
    """)


    conn.commit()
    conn.close()



@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM stories
        WHERE datetime(created_at) <= datetime('now','-24 hours')
    """)

    conn.commit()

    print("Expired stories deleted =", cur.rowcount)

    cur.execute(
        """
        SELECT posts.username,
           posts.image,
           posts.caption,
           users.profile_pic,
           posts.id
        FROM posts
        LEFT JOIN users
        ON posts.username = users.username
        WHERE posts.image NOT LIKE '%.webm'
        AND posts.image NOT LIKE '%.mp4'
        ORDER BY posts.id DESC

        """
    )
    posts = cur.fetchall()
    print("POSTS DATA:")
    print(posts)

    for p in posts:
        print("POST =", p)
    posts_with_likes = []

    for post in posts:

        post_id = post[4]

        cur.execute(
            "SELECT COUNT(*) FROM likes WHERE post_id=?",
            (post_id,)
        )

        like_count = cur.fetchone()[0]


        cur.execute(
            """
            SELECT username, comment
            FROM comments
            WHERE post_id=?
            ORDER BY id ASC
            """,
            (post_id,)
        )

        comments = cur.fetchall()

        posts_with_likes.append(
            post + (like_count, comments)
        )


    cur.execute(
        """
        SELECT username,video,caption
         FROM reels
        ORDER BY id DESC
        """
    )
    reels = cur.fetchall()


    cur.execute("""
        SELECT s1.id, s1.username, s1.image
        FROM stories s1
        WHERE s1.id = (
            SELECT MAX(s2.id)
            FROM stories s2
            WHERE s2.username = s1.username
              AND datetime(s2.created_at) >= datetime('now','-1 day')
        )
    AND datetime(s1.created_at) >= datetime('now','-1 day')
    AND s1.username != ?
    ORDER BY s1.id DESC
    """, (current_user,))

    print("CURRENT USER AT QUERY =", current_user)


    story_circles = cur.fetchall()


    print("RAW STORY CIRCLES =", story_circles)

    print("BEFORE FILTER =", story_circles)

    story_circles = [
    s for s in story_circles
    if s[1].strip() != current_user.strip()
]

    print("FILTERED STORY CIRCLES =", story_circles)

    cur.execute("""
        SELECT id, username, image
        FROM stories
        WHERE username=?
        ORDER BY id DESC
        LIMIT 1
    """, (current_user,))

    my_story = cur.fetchone()




    cur.execute(
        """
        SELECT image
        FROM stories
        WHERE username=?
        AND datetime(created_at) >= datetime('now','-1 day')
        ORDER BY id DESC
        LIMIT 1
        """,
        (current_user,)
    )

    row = cur.fetchone()

    my_story = None

    if row:
        my_story = (
            0,
            current_user,
            row[0]
        )

    my_story_file = row[0] if row else None

    cur.execute("""
        SELECT id, username, image
        FROM stories
        WHERE datetime(created_at) >= datetime('now','-1 day')
        ORDER BY username, id DESC
    """)

    all_stories = cur.fetchall()

    cur.execute("""
        SELECT id,username,image
        FROM stories
        WHERE username!=?
        ORDER BY id DESC
    """, (current_user,))

    friends_stories = cur.fetchall()

    cur.execute("""
        SELECT id, username, image
        FROM stories
        ORDER BY id DESC
    """)

    all_stories = cur.fetchall()


    cur.execute("""
        SELECT id, username, image
        FROM stories
        WHERE datetime(created_at) >= datetime('now','-1 day')
        ORDER BY username, id DESC
    """)

    all_user_stories = cur.fetchall()


    cur.execute("""
        SELECT followed_username
        FROM followers
        WHERE follower_username=?
    """, (current_user,))

    following_users = [row[0].strip() for row in cur.fetchall()]

    conn.close()


    print("POSTS:", posts)
    print("REELS:", reels)
    print("STORY CIRCLES:", story_circles)
    print("POST COUNT:", len(posts))
    print("CURRENT USER =", current_user)
    print("STORY CIRCLES =", story_circles)
    print("ALL STORIES =", all_stories)

    print("MY STORY =", my_story)
    print("STORY CIRCLES =", story_circles)
    print("ALL STORIES =", all_stories)


    return render_template(
        "index.html",
        posts=posts_with_likes,
        reels=reels,
        following_users=following_users,
        my_story=my_story,
        friends_stories=friends_stories,
        story_circles=story_circles,
        all_stories=all_stories,
        current_user=current_user
    )

@app.route("/send_otp", methods=["POST"])
def send_otp():

    email = request.form.get("email")

    otp = str(random.randint(100000, 999999))

    session["signup_otp"] = otp
    session["signup_email"] = email

    msg = Message(
        "Snapz Verification OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body = f"Your OTP is: {otp}"

    mail.send(msg)

    return "OTP Sent Successfully"


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        otp = request.form.get("otp")

        # OTP Check
        if otp != session.get("signup_otp"):
            return "Invalid OTP"

        # Password Match
        if confirm_password and password != confirm_password:
            return "Passwords do not match"

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        # Username exists
        cur.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )

        if cur.fetchone():
            conn.close()
            return "Username already exists"

        # Email exists
        cur.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        if cur.fetchone():
            conn.close()
            return "Email already registered"

        # Insert user
        cur.execute(
            """
            INSERT INTO users
            (
                username,
                name,
                email,
                profile_pic,
                password,
                bio,
                is_online
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                username,
                name,
                email,
                "default.jpg",
                password,
                "",
                0
            )
        )

        conn.commit()
        conn.close()

        session.pop("signup_otp", None)

        return redirect("/login")

    return render_template("signup.html")




@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = sqlite3.connect("snapz.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
        """,(username,password))

        user = cur.fetchone()

        if user:

            cur.execute("""
                UPDATE users
                SET is_online=1
                WHERE username=?
            """,(username,))

            conn.commit()

            session["username"] = user["username"]
            session["name"] = user["name"]
            session["bio"] = user["bio"]
            session["profile_pic"] = user["profile_pic"]

            conn.close()

            return redirect("/")

        conn.close()

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/users")
def users():

    if "username" not in session:
        return redirect("/login")

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            u.username,
            u.profile_pic
        FROM users u

        JOIN messages m
        ON (
            u.username=m.sender
            OR
            u.username=m.receiver
        )

        WHERE
            u.username!=?
        AND
        (
            m.sender=?
            OR
            m.receiver=?
        )
    """, (
        my_username,
        my_username,
        my_username
    ))

    all_users = cur.fetchall()

    friends_data = []

    for user in all_users:

        # Last message
        cur.execute("""
            SELECT
                sender,
                message,
                timestamp
            FROM messages
            WHERE
                (sender=? AND receiver=?)
            OR
                (sender=? AND receiver=?)
            ORDER BY id DESC
            LIMIT 1
        """, (
            my_username,
            user["username"],
            user["username"],
            my_username
        ))

        row = cur.fetchone()

        if row:
            last_message = row["message"]
            last_time = row["timestamp"]
        else:
            last_message = "Tap to chat"
            last_time = ""

        # Unread count
        cur.execute("""
            SELECT COUNT(*)
            FROM messages
            WHERE
                sender=?
            AND
                receiver=?
            AND
                is_seen=0
        """, (
            user["username"],
            my_username
        ))

        unread = cur.fetchone()[0]

        friends_data.append({
            "username": user["username"],
            "profile_pic": user["profile_pic"] or "default.jpg",
            "last_message": last_message,
            "last_time": last_time,
            "unread": unread,
            "online": False
        })

    # Latest chat first
    friends_data.sort(
        key=lambda x: x.get("last_time") or "",
        reverse=True
    )


    conn.close()

    return render_template(
        "users.html",
        friends=friends_data,
        current_user=my_username
    )


def time_ago(timestamp_str):
    if not timestamp_str:
        return "Just now"
    try:
        msg_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - msg_time  

        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{int(minutes)}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{int(hours)}h ago"
        days = hours // 24
        return f"{int(days)}d ago"
    except Exception:
        return "Just now"


@app.route("/chat/<username>", methods=["GET", "POST"])
def chat(username):

    if "username" not in session:
        return redirect("/login")

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    cur.execute("""
	SELECT
	caller,
	receiver,
	call_type,
	status,
	strftime('%I:%M %p', ended_at)
	FROM calls
	WHERE
	(caller=? AND receiver=?)
	OR
	(caller=? AND receiver=?)
	ORDER BY id ASC
    """,(
        session["username"],
	username,
	username,
        session["username"]
    ))

    calls = cur.fetchall()
    # Send message
    if request.method == "POST":

        msg = request.form.get("message", "").strip()

        if msg:

            cur.execute("""
                INSERT INTO messages
                (sender, receiver, message)
                VALUES(?,?,?)
            """, (
                my_username,
                username,
                msg
            ))

            conn.commit()

        conn.close()

        return redirect(f"/chat/{username}")

    # Seen update
    cur.execute("""
        UPDATE messages
        SET is_seen=1
        WHERE sender=?
        AND receiver=?
    """, (
        username,
        my_username
    ))

    conn.commit()

    # User info
    cur.execute("""
        SELECT
        profile_pic,
        is_online,
        last_seen
        FROM users
        WHERE username=?
    """, (username,))

    row = cur.fetchone()

    if row:
        profile_pic = row[0]
        is_online = row[1]
        last_seen = row[2]
    else:
        profile_pic = "default.jpg"
        is_online = 0
        last_seen = ""

    if profile_pic and profile_pic.startswith("http"):
        profile_url = profile_pic
    elif profile_pic:
        profile_url = "/static/images/" + profile_pic
    else:
        profile_url = "/static/images/default.jpg"
# Chat messages
    cur.execute("""
        SELECT
            sender,
            message,
            timestamp,
            is_seen,
            reel_id,
            image,
            audio,
	    video,
            deleted
        FROM messages
        WHERE
            (sender=? AND receiver=?)
            OR
            (sender=? AND receiver=?)
        ORDER BY id ASC
    """, (
        my_username,
        username,
        username,
        my_username
    ))

    rows = cur.fetchall()

    chats = []

    for r in rows:

        chats.append({

            "sender": r[0],
            "message": r[1],
            "time": time_ago(r[2]),
            "is_seen": r[3],
            "reel_id": r[4],
            "image": r[5],
            "audio": r[6],
            "video": r[7],
            "deleted": r[8]
        })

    conn.close()

    return render_template(
        "chat.html",
        chats=chats,
        chat_with=username,
        profile_url=profile_url,
        is_online=is_online,
        last_seen=last_seen,
	calls=calls
    )


@app.route("/chat_messages/<username>")
def chat_messages(username):

    if "username" not in session:
        return jsonify([])

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
	SELECT
	    id,
	    sender,
	    receiver,
	    message,
	    reel_id,
	    is_seen,
	    timestamp,
	    image,
	    audio,
	    deleted,
	    video
	FROM messages
        WHERE
            (sender=? AND receiver=?)
            OR
            (sender=? AND receiver=?)
        ORDER BY id ASC
    """, (
        my_username,
        username,
        username,
        my_username
    ))

    rows = cur.fetchall()
    conn.close()

    data = []

    for row in rows:


        data.append({
            "id": row[0],
            "sender": row[1],
            "receive": row[2],
            "message": row[3],
            "reel_id": row[4],
            "is_seen": row[5],
            "time": time_ago(row[6]),
            "image": row[7],
            "audio": row[8],
            "deleted": row[9],
            "video": row[10]
        })

    return jsonify(data)




@app.route("/send_message/<username>", methods=["POST"])
def send_message(username):

    if "username" not in session:
        return jsonify({"status":"error"})

    message = request.form.get("message","").strip()

    if message == "":
        return jsonify({"status":"empty"})

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages
        (sender,receiver,message)
        VALUES(?,?,?)
    """,(
        session["username"],
        username,
        message
    ))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})



@app.route("/upload", methods=["POST"])
def upload():

    print("UPLOAD START")
    print(request.files)
    print(request.form)

    # Login check
    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "User not logged in"
        }), 401

    # File get
    file = request.files.get("file") or request.files.get("image")

    print("FILE OBJECT =", file)
    print("FILENAME =", file.filename if file else None)


    if not file or file.filename == "":
        return jsonify({
            "status": "error",
            "message": "No file uploaded"
        }), 400

    username = session["username"]
    caption = request.form.get("caption", "")
    upload_type = request.form.get("type", "post")

    print("LOGGED USER =", username)
    print("TYPE =", upload_type)

    # Cloudinary upload
    try:
        result = cloudinary.uploader.upload(file)
        file_url = result["secure_url"]
        print("Cloudinary Upload Success =", file_url)

    except Exception as e:
        print("Cloudinary Error =", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    try:

        # REEL
        if upload_type == "reel":

            cur.execute(
                "INSERT INTO reels(username, video, caption) VALUES(?,?,?)",
                (username, file_url, caption)
            )

        # STORY
        elif upload_type == "story":

            cur.execute(
                "INSERT INTO stories(username, image) VALUES(?,?)",
                (username, file_url)
            )

        # POST
        else:

            cur.execute(
                "SELECT profile_pic FROM users WHERE username=?",
                (username,)
            )

            row = cur.fetchone()
            profile_pic = row[0] if row else "default.jpg"

            cur.execute(
                "INSERT INTO posts(username, image, caption, profile_pic) VALUES(?,?,?,?)",
                (username, file_url, caption, profile_pic)
            )

        conn.commit()

        print("UPLOAD SAVED SUCCESSFULLY")
        print("FILE =", file_url)
        print("CAPTION =", caption)

        return jsonify({
            "status": "ok",
            "url": file_url
        })

    except Exception as e:

        conn.rollback()
        print("DB Error =", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        conn.close()


@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # User Details
    cur.execute("""
        SELECT name, bio, profile_pic
        FROM users
        WHERE username=?
    """, (username,))

    row = cur.fetchone()

    if row:
        name = row[0]
        bio = row[1]
        profile_pic = row[2] if row[2] else "default.jpg"
    else:
        name = username
        bio = ""
        profile_pic = "default.jpg"

    # Posts
    cur.execute("""
        SELECT id, username, image, caption
        FROM posts
        WHERE username=?
        ORDER BY id DESC
    """, (username,))

    posts = cur.fetchall()

    # Reels
    cur.execute("""
        SELECT id, username, video, caption
        FROM reels
        WHERE username=?
        ORDER BY id DESC
    """, (username,))

    reels = cur.fetchall()

    # Posts Count
    cur.execute("""
        SELECT COUNT(*)
        FROM posts
        WHERE username=?
    """, (username,))

    posts_count = cur.fetchone()[0]

    # Reels Count
    cur.execute("""
        SELECT COUNT(*)
        FROM reels
        WHERE username=?
    """, (username,))

    reels_count = cur.fetchone()[0]

    # Followers
    cur.execute("""
        SELECT COUNT(*)
        FROM followers
        WHERE followed_username=?
    """, (username,))

    followers = cur.fetchone()[0]

    # Following
    cur.execute("""
        SELECT COUNT(*)
        FROM followers
        WHERE follower_username=?
    """, (username,))

    following = cur.fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",

        username=username,
        name=name,
        bio=bio,
        profile_pic=profile_pic,

        posts=posts,
        reels=reels,

        posts_count=posts_count,
        reels_count=reels_count,

        followers=followers,
        following=following
    )

@app.route("/reels")
def reels():

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            reels.id,
            reels.username,
            reels.video,
            reels.caption,
            users.profile_pic
        FROM reels
        LEFT JOIN users
        ON reels.username = users.username
        ORDER BY reels.id DESC
    """)

    data = cur.fetchall()

    reels = []

    for r in data:

        reel_id = r[0]

        # Like count
        cur.execute(
            "SELECT COUNT(*) FROM reel_likes WHERE reel_id=?",
            (reel_id,)
        )
        like_count = cur.fetchone()[0]

        # Current user liked?
        cur.execute(
            """
            SELECT id
            FROM reel_likes
            WHERE reel_id=?
            AND username=?
            """,
            (reel_id, current_user)
        )

        liked = cur.fetchone() is not None

        # Comment count
        cur.execute(
            """
            SELECT COUNT(*)
            FROM reel_comments
            WHERE reel_id=?
            """,
            (reel_id,)
        )

        comment_count = cur.fetchone()[0]

        reels.append({
            "id": reel_id,
            "username": r[1],
            "video": r[2],
            "caption": r[3],
            "profile_pic": r[4] if r[4] else "/static/default.png",
            "likes": like_count,
            "comments": comment_count,
            "liked": liked
        })

    conn.close()

    print("REELS =", reels)

    return render_template(
        "reels.html",
        reels=reels,
        current_user=current_user
    )



@app.route("/share_post", methods=["POST"])
def share_post():

    if "username" not in session:
        return jsonify({
            "status":"error",
            "message":"Login required"
        }),401

    data = request.get_json()

    receiver = data.get("receiver")
    post_id = data.get("post_id")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Post data
    cur.execute(
        """
        SELECT username,image,caption
        FROM posts
        WHERE id=?
        """,
        (post_id,)
    )

    post = cur.fetchone()

    if not post:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Post not found"
        })

    owner = post[0]
    image = post[1]
    caption = post[2]

    # Message
    cur.execute(
        """
        INSERT INTO messages
        (sender,receiver,message,image,timestamp)
        VALUES(?,?,?,?,datetime('now','localtime'))
        """,
        (
            session["username"],
            receiver,
            caption,
            image
        )
    )

    # Notification
    if receiver != session["username"]:

        cur.execute(
            """
            INSERT INTO notifications
            (user_to,user_from,action)
            VALUES(?,?,?)
            """,
            (
                receiver,
                session["username"],
                "shared a post with you 📤"
            )
        )

    conn.commit()
    conn.close()

    return jsonify({
        "status":"ok"
    })



@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/logout")
def logout():

    if "username" in session:

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET
                is_online=0,
                last_seen=datetime('now','localtime')
            WHERE username=?
        """, (session["username"],))

        conn.commit()
        conn.close()

    session.clear()

    response = redirect("/login")

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@app.route("/story", methods=["POST"])
def story():

    if "username" not in session:
        return redirect("/login")

    image = request.files.get("image")

    if not image or image.filename == "":
        return redirect("/")

    try:
        result = cloudinary.uploader.upload(image)
        image_url = result["secure_url"]

    except Exception as e:
        print("Story Upload Error:", e)
        return redirect("/")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO stories(username,image)
        VALUES(?,?)
        """,
        (
            session["username"],
            image_url
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "username" not in session:
        return redirect(url_for("login"))

    print(request.files)
    print(request.form)

    new_name = request.form.get("name", "").strip()
    new_username = request.form.get("username", "").strip()
    new_bio = request.form.get("bio", "").strip()

    old_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Username already exists check
    cur.execute(
        "SELECT username FROM users WHERE username=?",
        (new_username,)
    )

    existing = cur.fetchone()

    if existing and new_username != old_username:
        conn.close()
        return "Username already taken"

    # ---------------- USERS ----------------

    cur.execute(
        """
        UPDATE users
        SET
            name=?,
            username=?,
            bio=?
        WHERE username=?
        """,
        (
            new_name,
            new_username,
            new_bio,
            old_username
        )
    )

    # ---------------- POSTS ----------------

    cur.execute(
        """
        UPDATE posts
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- REELS ----------------

    cur.execute(
        """
        UPDATE reels
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- STORIES ----------------

    cur.execute(
        """
        UPDATE stories
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- FOLLOWERS ----------------

    cur.execute(
        """
        UPDATE followers
        SET follower_username=?
        WHERE follower_username=?
        """,
        (
            new_username,
            old_username
        )
    )

    cur.execute(
        """
        UPDATE followers
        SET followed_username=?
        WHERE followed_username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- COMMENTS ----------------

    cur.execute(
        """
        UPDATE comments
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- LIKES ----------------

    cur.execute(
        """
        UPDATE likes
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- REEL LIKES ----------------

    cur.execute(
        """
        UPDATE reel_likes
        SET username=?
        WHERE username=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- NOTIFICATIONS ----------------

    cur.execute(
        """
        UPDATE notifications
        SET user_from=?
        WHERE user_from=?
        """,
        (
            new_username,
            old_username
        )
    )

    cur.execute(
        """
        UPDATE notifications
        SET user_to=?
        WHERE user_to=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- MESSAGES ----------------

    cur.execute(
        """
        UPDATE messages
        SET sender=?
        WHERE sender=?
        """,
        (
            new_username,
            old_username
        )
    )

    cur.execute(
        """
        UPDATE messages
        SET receiver=?
        WHERE receiver=?
        """,
        (
            new_username,
            old_username
        )
    )

    # ---------------- PROFILE PHOTO ----------------

    file = request.files.get("profile_pic")

    if file and file.filename:

        try:

            result = cloudinary.uploader.upload(file)

            photo_url = result["secure_url"]

            cur.execute(
                """
                UPDATE users
                SET profile_pic=?
                WHERE username=?
                """,
                (
                    photo_url,
                    new_username
                )
            )

            session["profile_pic"] = photo_url

        except Exception as e:
            print("Cloudinary Error:", e)

    conn.commit()
    conn.close()

    # ---------------- SESSION UPDATE ----------------

    session["name"] = new_name
    session["username"] = new_username
    session["bio"] = new_bio

    return redirect(url_for("profile"))


@app.route("/search")
def search():

    if "username" not in session:
        return jsonify([])

    current_user = session["username"]

    query = request.args.get("q", "").strip()

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""

    SELECT

        u.username,
        u.name,
        u.profile_pic,

        CASE
            WHEN f.follower_username IS NULL
            THEN 0
            ELSE 1
        END AS following,

        (
            SELECT COUNT(*)
            FROM followers
            WHERE followed_username=u.username
        ) AS followers_count,

        (
            SELECT COUNT(*)
            FROM posts
            WHERE username=u.username
        ) AS posts_count

    FROM users u

    LEFT JOIN followers f
    ON
        f.followed_username=u.username
    AND
        f.follower_username=?

    WHERE

        u.username LIKE ?

        OR

        u.name LIKE ?

    ORDER BY

        u.username ASC

    """,(

        current_user,

        "%" + query + "%",

        "%" + query + "%"

    ))

    users = []

    for row in cur.fetchall():

        users.append({

            "username": row["username"],

            "name": row["name"],

            "profile_pic": row["profile_pic"] or "default.jpg",

            "following": bool(row["following"]),

            "followers": row["followers_count"],

            "posts": row["posts_count"],

            "verified": False

        })

    conn.close()

    return jsonify(users)


def create_tables():
    conn = sqlite3.connect('snapz.db')
    cur = conn.cursor()
    # Puraane tables...
    cur.execute('''CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_to TEXT,
                    user_from TEXT,
                        action TEXT,
                    post_id INTEGER,
                    is_read BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()


@app.route("/notifications")
def notifications():

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            user_from,
            action,
            timestamp
        FROM notifications
        WHERE user_to=?
        ORDER BY id DESC
    """, (current_user,))

    rows = cur.fetchall()

    notifications = []

    for row in rows:

        user_from = row[0]

        # profile photo
        cur.execute("""
            SELECT profile_pic
            FROM users
            WHERE username=?
        """, (user_from,))

        pic = cur.fetchone()

        if pic:
            profile_pic = pic[0]
        else:
            profile_pic = "/static/default.png"

        # Follow status
        cur.execute("""
            SELECT 1
            FROM followers
            WHERE follower_username=?
            AND followed_username=?
        """, (
            current_user,
            user_from
        ))

        is_following = cur.fetchone() is not None

        notifications.append({

            "username": user_from,

            "action": row[1],

            "time": row[2],

            "profile_pic": profile_pic,

            "following": is_following

        })

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications,
        current_user=current_user
    )


@app.route("/profile/<username>")
def profile_view(username):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # User check
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return "User not found"

    # Posts
    cur.execute(
        "SELECT id, username, image, caption FROM posts WHERE username=? ORDER BY id DESC",
        (username,)
    )
    posts = cur.fetchall()

    # Reels
    cur.execute(
        "SELECT id, username, video, caption FROM reels WHERE username=? ORDER BY id DESC",
        (username,)
    )
    reels = cur.fetchall()

    # Counts
    cur.execute(
        "SELECT COUNT(*) FROM posts WHERE username=?",
        (username,)
    )
    posts_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM followers WHERE followed_username=?",
        (username,)
    )
    followers = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM followers WHERE follower_username=?",
        (username,)
    )
    following = cur.fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        username=username,
        user=user,
        posts=posts,
        reels=reels,
        posts_count=posts_count,
        followers=followers,
        following=following
    )



@app.route("/follow/<username>", methods=["POST"])
def follow(username):

    if "username" not in session:
        return jsonify({
            "status":"error",
            "message":"Login required"
        }),401

    follower = session["username"]

    if follower == username:
        return jsonify({
            "status":"error",
            "message":"You can't follow yourself"
        })

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # User exists
    cur.execute(
        "SELECT 1 FROM users WHERE username=?",
        (username,)
    )

    if not cur.fetchone():
        conn.close()
        return jsonify({
            "status":"error",
            "message":"User not found"
        })

    # Already following?
    cur.execute("""
        SELECT 1
        FROM followers
        WHERE follower_username=?
        AND followed_username=?
    """,(follower,username))

    already = cur.fetchone()

    # ======================
    # UNFOLLOW
    # ======================
    if already:

        cur.execute("""
            DELETE FROM followers
            WHERE follower_username=?
            AND followed_username=?
        """,(follower,username))

        conn.commit()

        cur.execute("""
            SELECT COUNT(*)
            FROM followers
            WHERE followed_username=?
        """,(username,))

        followers_count = cur.fetchone()[0]

        conn.close()

        return jsonify({
            "status":"unfollowed",
            "followers":followers_count
        })

    # ======================
    # FOLLOW
    # ======================

    cur.execute("""
        INSERT INTO followers(
            follower_username,
            followed_username
        )
        VALUES(?,?)
    """,(follower,username))

    # Notification
    cur.execute("""
        INSERT INTO notifications(
            user_to,
            user_from,
            action
        )
        VALUES(?,?,?)
    """,(username,follower,"follow"))

    conn.commit()

    cur.execute("""
        SELECT COUNT(*)
        FROM followers
        WHERE followed_username=?
    """,(username,))

    followers_count = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "status":"followed",
        "followers":followers_count
    })



@app.route("/like_post/<int:post_id>", methods=["POST"])
def like_post(post_id):

    if "username" not in session:
        return jsonify({"status": "error"}), 401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    try:

        # Check post exists
        cur.execute(
            "SELECT username FROM posts WHERE id=?",
            (post_id,)
        )

        owner = cur.fetchone()

        if not owner:
            conn.close()
            return jsonify({"status": "post_not_found"}), 404

        owner_username = owner[0]

        # Already liked?
        cur.execute(
            """
            SELECT 1
            FROM likes
            WHERE post_id=?
            AND username=?
            """,
            (post_id, username)
        )

        if cur.fetchone():

            # Unlike
            cur.execute(
                """
                DELETE FROM likes
                WHERE post_id=?
                AND username=?
                """,
                (post_id, username)
            )

            conn.commit()

            cur.execute(
                """
                SELECT COUNT(*)
                FROM likes
                WHERE post_id=?
                """,
                (post_id,)
            )

            like_count = cur.fetchone()[0]

            conn.close()

            return jsonify({
                "status": "unliked",
                "likes": like_count
            })

        # Like
        cur.execute(
            """
            INSERT INTO likes(post_id, username)
            VALUES(?,?)
            """,
            (post_id, username)
        )

        # Notification
        if owner_username != username:

            cur.execute(
                """
                INSERT INTO notifications
                (user_to, user_from, action)
                VALUES(?,?,?)
                """,
                (
                    owner_username,
                    username,
                    "liked your post ❤️"
                )
            )

        conn.commit()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM likes
            WHERE post_id=?
            """,
            (post_id,)
        )

        like_count = cur.fetchone()[0]

        conn.close()

        return jsonify({
            "status": "liked",
            "likes": like_count
        })

    except Exception as e:

        conn.rollback()
        conn.close()

        print("LIKE ERROR =", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/unfollow/<username>", methods=["POST"])
def unfollow(username):

    if "username" not in session:
        return jsonify({"status": "error"}), 401

    follower = session["username"]

    if follower == username:
        return jsonify({"status": "error"}), 400

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    try:

        cur.execute(
            """
            DELETE FROM followers
            WHERE follower_username=?
            AND followed_username=?
            """,
            (follower, username)
        )

        conn.commit()

        return jsonify({
            "status": "unfollowed"
        })

    except Exception as e:

        conn.rollback()

        print("UNFOLLOW ERROR =", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        conn.close()


@app.route("/delete_post/<int:id>", methods=["POST"])
def delete_post(id):

    if "username" not in session:
        return jsonify({
            "status":"error",
            "message":"Login required"
        }),401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Check owner
    cur.execute("""
        SELECT username
        FROM posts
        WHERE id=?
    """,(id,))

    post = cur.fetchone()

    if post is None:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Post not found"
        })

    if post[0] != username:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Permission denied"
        }),403

    # Delete likes
    cur.execute("""
        DELETE FROM likes
        WHERE post_id=?
    """,(id,))

    # Delete comments
    cur.execute("""
        DELETE FROM comments
        WHERE post_id=?
    """,(id,))

    # Delete post
    cur.execute("""
        DELETE FROM posts
        WHERE id=?
    """,(id,))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"deleted"
    })


@app.route("/edit_reel", methods=["POST"])
def edit_reel():

    data = request.get_json()

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE reels SET caption=? WHERE id=?",
        (data["caption"], data["id"])
    )

    conn.commit()
    conn.close()

    return "ok"

@app.route("/delete_reel/<int:id>", methods=["POST"])
def delete_reel(id):

    if "username" not in session:
        return jsonify({
            "status":"error",
            "message":"Login required"
        }),401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Check owner
    cur.execute("""
        SELECT username
        FROM reels
        WHERE id=?
    """,(id,))

    reel = cur.fetchone()

    if reel is None:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Reel not found"
        })

    if reel[0] != username:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Permission denied"
        }),403

    # Delete reel likes
    cur.execute("""
        DELETE FROM reel_likes
        WHERE reel_id=?
    """,(id,))

    # Delete reel comments
    cur.execute("""
        DELETE FROM reel_comments
        WHERE reel_id=?
    """,(id,))

    # Delete reel
    cur.execute("""
        DELETE FROM reels
        WHERE id=?
    """,(id,))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"deleted"
    })


@app.route("/follow_back/<username>", methods=["POST"])
def follow_back(username):

    if "username" not in session:
        return redirect("/login")

    follower = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT 1 FROM followers
        WHERE follower_username=? AND followed_username=?
    """, (follower, username))

    if not cur.fetchone():
        cur.execute("""
            INSERT INTO followers
            (follower_username, followed_username)
            VALUES (?, ?)
        """, (follower, username))

    conn.commit()
    conn.close()

    return redirect("/notifications")

@app.route("/unfollow_back/<username>", methods=["POST"])
def unfollow_back(username):

    if "username" not in session:
        return redirect("/login")

    follower = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM followers
        WHERE follower_username=? AND followed_username=?
    """, (follower, username))

    conn.commit()
    conn.close()

    return redirect("/notifications")


@app.route("/followers/<username>")
def followers(username):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT follower_username
        FROM followers
        WHERE followed_username=?
    """, (username,))

    followers = cur.fetchall()

    conn.close()

    return render_template(
        "followers.html",
        username=username,
        followers=followers
    )


@app.route("/following/<username>")
def following(username):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT followed_username
        FROM followers
        WHERE follower_username=?
    """, (username,))

    following = cur.fetchall()

    conn.close()

    return render_template(
        "following.html",
        username=username,
        following=following
    )



@app.route("/comments/<int:post_id>")
def get_comments(post_id):

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            username,
            comment,
            timestamp
        FROM comments
        WHERE post_id=?
        ORDER BY id ASC
    """,(post_id,))

    comments=[]

    for row in cur.fetchall():

        comments.append({
            "username":row["username"],
            "comment":row["comment"],
            "time":row["timestamp"]
        })

    conn.close()

    return jsonify(comments)


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment_post(post_id):

    if "username" not in session:
        return jsonify({
            "status":"error",
            "message":"Login required"
        }),401

    username=session["username"]

    comment=request.form.get("comment","").strip()

    if comment=="":
        return jsonify({
            "status":"error",
            "message":"Comment is empty"
        })

    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    # Post owner
    cur.execute("""
        SELECT username
        FROM posts
        WHERE id=?
    """,(post_id,))

    owner=cur.fetchone()

    if owner is None:
        conn.close()
        return jsonify({
            "status":"error",
            "message":"Post not found"
        })

    # Save comment
    cur.execute("""
        INSERT INTO comments(
            post_id,
            username,
            comment
        )
        VALUES(?,?,?)
    """,(post_id,username,comment))

    # Notification
    if owner[0]!=username:

        cur.execute("""
            INSERT INTO notifications(
                user_to,
                user_from,
                action
            )
            VALUES(?,?,?)
        """,(owner[0],username,"comment"))

    conn.commit()

    # Comment count
    cur.execute("""
        SELECT COUNT(*)
        FROM comments
        WHERE post_id=?
    """,(post_id,))

    comment_count=cur.fetchone()[0]

    conn.close()

    return jsonify({
        "status":"ok",
        "username":username,
        "comment":comment,
        "comments":comment_count
    })




@app.route("/like_reel/<int:reel_id>", methods=["POST"])
def like_reel():

    if "username" not in session:
        return jsonify({"status":"error"}),401

    liker = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Reel owner
    cur.execute(
        "SELECT username FROM reels WHERE id=?",
        (reel_id,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"status":"error"})

    owner = row[0]

    # Already liked?
    cur.execute(
        """
        SELECT 1
        FROM reel_likes
        WHERE username=? AND reel_id=?
        """,
        (liker,reel_id)
    )

    if cur.fetchone():
        conn.close()
        return jsonify({"status":"already_liked"})

    # Save like
    cur.execute(
        """
        INSERT INTO reel_likes(username,reel_id)
        VALUES(?,?)
        """,
        (liker,reel_id)
    )

    # Notification
    if owner != liker:

        cur.execute(
            """
            INSERT INTO notifications
            (user_to,user_from,action)
            VALUES(?,?,?)
            """,
            (
                owner,
                liker,
                "liked your reel ❤️"
            )
        )

    conn.commit()

    # Like count
    cur.execute(
        """
        SELECT COUNT(*)
        FROM reel_likes
        WHERE reel_id=?
        """,
        (reel_id,)
    )

    like_count = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "status":"liked",
        "likes":like_count
    })


@app.route("/download_reel/<int:reel_id>")
def download_reel(reel_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT video FROM reels WHERE id=?",
        (reel_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return "Not Found", 404

    video_url = row[0]

    if "?" in video_url:
        video_url += "&fl_attachment=Snapz_Reel.mp4"
    else:
        video_url += "?fl_attachment=Snapz_Reel.mp4"

    return redirect(video_url)


@app.route("/like_story/<int:story_id>", methods=["POST"])
def like_story(story_id):

    liker = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # story owner nikalo
    cur.execute(
        "SELECT username FROM stories WHERE id=?",
        (story_id,)
    )

    cur.execute("""
        INSERT INTO notifications
        (user_to, user_from, action)
        VALUES (?, ?, ?)
    """, (
    owner,
    liker,
    "liked your story"
    ))
    owner = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO notifications
        (user_to, user_from, action)
        VALUES (?, ?, ?)
    """, (
    owner,
    liker,
    "liked your story"
    ))

    conn.commit()
    conn.close()

    return {"status": "liked"}

@app.route("/comment_reel/<int:reel_id>", methods=["POST"])
def comment_reel(reel_id):

    if "username" not in session:
        return {"status":"error"}

    comment = request.form.get("comment")
    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reel_comments
    (reel_id, username, comment)
    VALUES (?, ?, ?)
    """, (reel_id, username, comment))

    conn.commit()
    conn.close()

    return {"status":"success"}

@app.route("/reel/<int:reel_id>")
def single_reel(reel_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT id, username, video, caption
    FROM reels
    WHERE id=?
    """, (reel_id,))

    reel = cur.fetchone()

    conn.close()

    return render_template(
        "single_reel.html",
        reel=reel
    )

@app.route("/share_reel/<int:reel_id>")
def share_reel(reel_id):

    if "username" not in session:
        return redirect("/login")

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Check reel exists
    cur.execute(
        "SELECT id FROM reels WHERE id=?",
        (reel_id,)
    )

    if not cur.fetchone():
        conn.close()
        return "Reel not found"

    cur.execute(
        """
        SELECT username, profile_pic
        FROM users
        WHERE username!=?
        ORDER BY username
        """,
        (my_username,)
    )

    users = cur.fetchall()

    conn.close()

    return render_template(
        "share_reel.html",
        users=users,
        reel_id=reel_id
    )


@app.route("/send_reel/<int:reel_id>/<username>")
def send_reel(reel_id, username):

    if "username" not in session:
        return redirect("/login")

    sender = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Check reel exists
    cur.execute(
        "SELECT id FROM reels WHERE id=?",
        (reel_id,)
    )

    if not cur.fetchone():
        conn.close()
        return "Reel not found"

    # Send message
    cur.execute(
        """
        INSERT INTO messages
        (sender,receiver,message,reel_id,timestamp)
        VALUES(?,?,?,?,datetime('now','localtime'))
        """,
        (
            sender,
            username,
            "🎬 Shared a Reel",
            reel_id
        )
    )

    # Notification
    if sender != username:

        cur.execute(
            """
            INSERT INTO notifications
            (user_to,user_from,action)
            VALUES(?,?,?)
            """,
            (
                username,
                sender,
                "shared a reel with you 🎬"
            )
        )

    conn.commit()
    conn.close()

    return redirect(f"/chat/{username}")




@app.route("/testmail")
def testmail():

    msg = Message(
        "Test Mail",
        sender=app.config["MAIL_USERNAME"],
        recipients=["snapzofficial0@gmail.com"]
    )

    msg.body = "Hello Snapz"

    mail.send(msg)

    return "Success"

@app.route("/view_story/<int:story_id>", methods=["POST"])
def view_story(story_id):

    if "username" not in session:
        return jsonify({"status":"login required"})

    viewer = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM story_views
        WHERE story_id=? AND viewer=?
    """, (story_id, viewer))

    exist = cur.fetchone()

    if not exist:
        cur.execute("""
            INSERT INTO story_views(story_id, viewer)
            VALUES(?,?)
        """, (story_id, viewer))

        conn.commit()

    conn.close()

    return jsonify({"status":"viewed"})


@app.route("/story_views/<int:story_id>")
def story_views(story_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT viewer
        FROM story_views
        WHERE story_id=?
    """, (story_id,))

    viewers = cur.fetchall()

    viewers = [v[0] for v in viewers]

    conn.close()

    return jsonify(viewers)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        value = request.form.get("username")

        cur.execute(
            "SELECT email FROM users WHERE username=? OR email=?",
            (value, value)
        )


        user = cur.fetchone()


        if not user:
            return "User not found"

        email = user[0]


        otp = str(random.randint(100000, 999999))

        session["reset_otp"] = otp
        session["reset_email"] = email

        print("EMAIL =", email)
        print("SENDER =", app.config["MAIL_DEFAULT_SENDER"])


        msg = Message(
            subject="Snapz Password Reset OTP",
            sender="snapzofflicial0@gmail.com",
            recipients=[email]
        )

        msg.body = f"Your Snapz OTP is: {otp}\n\nThis OTP is valid for 5 minutes."

        print("msg.subject =", msg.subject)
        print("msg.sender =", msg.sender)
        print("msg.recipients =", msg.recipients)

        mail.send(msg)

        return redirect("/verify_otp")

    return render_template("forgot_password.html")


@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if "reset_otp" not in session:
        return redirect("/forgot_password")

    if request.method == "POST":

        otp = request.form.get("otp", "").strip()

        if otp == session["reset_otp"]:

            session["otp_verified"] = True

            return redirect("/reset_password")

        return render_template(
            "verify_otp.html",
            error="Invalid OTP"
        )

    return render_template("verify_otp.html")



@app.route("/reset_password", methods=["GET","POST"])
def reset_password():

    if "otp_verified" not in session:
        return redirect("/forgot_password")

    if request.method == "POST":

        password = request.form["password"].strip()
        confirm = request.form["confirm"].strip()

        if password != confirm:
            return "Passwords do not match"

        cur.execute(
            "UPDATE users SET password=? WHERE email=?",
            (password, session["reset_email"])
        )

        conn.commit()

        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        session.pop("otp_verified", None)

        return redirect("/login")

    return render_template("reset_password.html")


@app.route("/resend_otp")
def resend_otp():

    email = session.get("reset_email")

    if not email:
        return redirect("/forgot_password")

    otp = str(random.randint(100000, 999999))

    session["reset_otp"] = otp

    msg = Message(
        "Snapz Password Reset OTP",
        recipients=[email]
    )

    msg.body = f"""Your new Snapz OTP is:

{otp}

This OTP is valid for 5 minutes.
"""

    mail.send(msg)

    return redirect("/verify_otp")


@app.route("/send_images/<username>", methods=["POST"])
def send_images(username):



    if "username" not in session:
        return jsonify({"status":"error"})

    files = request.files.getlist("file")

    if not files:
        return jsonify({"status":"no_file"})

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    os.makedirs("static/uploads", exist_ok=True)

    for file in files:

        if file.filename == "":
            continue

        filename = str(int(time.time()*1000)) + "_" + secure_filename(file.filename)

        file.save(os.path.join("static/uploads", filename))

        cur.execute("""
            INSERT INTO messages
            (sender, receiver, image)
            VALUES (?,?,?)
        """,(
            session["username"],
            username,
            filename
        ))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/send_video/<username>", methods=["POST"])
def send_video(username):

    if "username" not in session:
        return jsonify({"status":"error"})

    files = request.files.getlist("file")

    if not files:
        return jsonify({"status":"no_file"})

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    os.makedirs("static/uploads", exist_ok=True)

    for file in files:

        if file.filename == "":
            continue

        filename = str(int(time.time()*1000)) + "_" + secure_filename(file.filename)

        file.save(os.path.join("static/uploads", filename))

        # ===== Thumbnail =====
        thumb = filename.rsplit(".",1)[0] + ".jpg"

        os.system(
            f'ffmpeg -y -i "static/uploads/{filename}" '
            f'-ss 00:00:01 -vframes 1 '
            f'"static/uploads/{thumb}" > /dev/null 2>&1'
        )

        cur.execute("""
            INSERT INTO messages
            (sender, receiver, video, video_thumb)
            VALUES (?,?,?,?)
        """,(
            session["username"],
            username,
            filename,
            thumb
        ))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


@app.route("/send_voice/<username>", methods=["POST"])
def send_voice(username):

    print("VOICE ROUTE START")
    print(request.files)

    if "username" not in session:
        return jsonify({"status":"error"})


    if "audio" not in request.files:
        return jsonify({"status":"no audio"})


    audio = request.files["audio"]


    filename = "voice_" + str(int(time.time())) + ".webm"


    voice_path = os.path.join(
        "static/uploads",
        filename
    )



    audio.save(voice_path)



    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()


    cur.execute("""
        INSERT INTO messages
        (sender, receiver, message, audio)
        VALUES(?,?,?,?)
    """,(
        session["username"],
        username,
        "",
        filename
    ))


    conn.commit()
    conn.close()


    return jsonify({
        "status":"ok",
        "audio":filename
    })



@app.route("/delete_message/<int:id>", methods=["POST"])
def delete_message(id):

    if "username" not in session:
        return jsonify({"status":"error"})

    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    cur.execute("""
        DELETE FROM messages
        WHERE id=?
        AND sender=?
    """,(id,session["username"]))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


@socketio.on("join")
def join(data):
    print("JOIN:", data["username"])
    join_room(data["username"])



@socketio.on("answer-call")
def answer_call(data):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE calls
        SET status='answered'
        WHERE id=(
            SELECT id FROM calls
            WHERE caller=? AND receiver=?
            ORDER BY id DESC
            LIMIT 1
        )
    """,(
        data["from"],
        data["to"]
    ))

    conn.commit()
    conn.close()

    emit(
        "call-answered",
        data,
        room=data["to"]
    )



def save_system_message(sender, receiver, text):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages(
            sender,
            receiver,
            message,
            timestamp
        )
        VALUES(?,?,?,datetime('now'))
    """,(sender,receiver,text))

    conn.commit()
    conn.close()


@socketio.on("end-call")
def end_call(data):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE calls
        SET status='ended',
            ended_at=datetime('now','localtime')
        WHERE status='answered'
    """)

    conn.commit()
    cur.execute("""
    SELECT caller,receiver,call_type,status
	FROM calls
	ORDER BY id DESC
	LIMIT 1
    """)

    call = cur.fetchone()

    if call and call[3] == "answered":

        if call[2] == "voice":

            save_system_message(
                call[0],
                call[1],
                "📞 Voice call ended"
            )

            save_system_message(
                call[1],
                call[0],
                "📞 Voice call ended"
            )

    else:

            save_system_message(
                call[0],
                call[1],
                "📹 Video call ended"
            )


            save_system_message(
                call[1],
                call[0],
                "📹 Video call ended"
            )

    conn.close()

    emit(
        "call-ended",
        data,
        room=data["to"]
    )


@socketio.on("call-user")
def call_user(data):

    print("CALL USER:", data)

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO calls(
            caller,
            receiver,
            call_type,
            status
        )
        VALUES(?,?,?,?)
    """,(
        data["from"],
        data["to"],
        data["type"],
        "ringing"
    ))

    conn.commit()
    conn.close()

    emit(
        "incoming-call",
        data,
        room=data["to"]
    )
@socketio.on("missed-call")
def missed_call(data):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE calls
        SET status='missed',
            ended_at=datetime('now','localtime')
        WHERE caller=?
        AND receiver=?
        AND status='ringing'
    """,(
        data["from"],
        data["to"]
    ))

    conn.commit()
    if data["type"] == "voice":

        save_system_message(
            data["from"],
            data["to"],
            "📞 Voice call ended"
        )

        save_system_message(
            data["to"],
            data["from"],
            "📞 Missed voice call"
        )

    else:

        save_system_message(
            data["from"],
            data["to"],
            "📹 Video call ended"
        )

        save_system_message(
            data["to"],
            data["from"],
            "📹 Missed video call"
        )

    conn.close()

    emit(
        "call-ended",
        {},
        room=data["to"]
    )


@socketio.on("offer")
def offer(data):
    emit("offer", data, room=data["to"])


@socketio.on("answer")
def answer(data):
    emit("answer", data, room=data["to"])


@socketio.on("ice-candidate")
def ice_candidate(data):
    emit("ice-candidate", data, room=data["to"])


init_db()


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )
