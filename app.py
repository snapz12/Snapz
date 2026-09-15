from pathlib import Path
import os
os.environ["EVENTLET_NO_GREENDNS"] = "yes"
import eventlet
eventlet.monkey_patch()
import sqlite3
import base64
import uuid
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
from flask import jsonify
import tempfile
import json
from flask import send_file
from flask import session, redirect
import re

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


def get_device_name(user_agent):

    ua = user_agent or ""
    low = ua.lower()

    # Android
    if "android" in low:

        # Android 10+ model
        m = re.search(r'Android\s[\d\.]+;\s*([^;)]+)', ua)

        if m:
            model = m.group(1).strip()

            # Common cleanup
            model = model.replace("Build", "")
            model = model.split(";")[0].strip()

            return "Android " + model

        return " Android"

    # iPhone
    elif "iphone" in low:

        return " iPhone"

    # iPad
    elif "ipad" in low:

        return " iPad"

    # Windows
    elif "windows" in low:

        return " Windows PC"

    # macOS
    elif "macintosh" in low:

        return " Mac"

    # Linux
    elif "linux" in low:

        return " Linux"

    return " Unknown Device"

def check_session():

    if "username" not in session:
        return None

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT current_session
        FROM users
        WHERE username=?
    """, (
        session["username"],
    ))

    row = cur.fetchone()

    conn.close()

    if not row:
        session.clear()
        return redirect("/login")

    if row[0] != session.get("session_id"):
        session.clear()
        return redirect("/login")

    return None


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



    cur.execute("""
    CREATE TABLE IF NOT EXISTS post_shares(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter TEXT NOT NULL,
        reported TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS blocked_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blocker TEXT NOT NULL,
        blocked TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS post_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        tagged_username TEXT NOT NULL,
        UNIQUE(post_id, tagged_username)
    )
    """)

    conn.commit()
    conn.close()


@app.before_request
def check_user_session():

    protected_routes = [
        "home",
        "chat",
        "profile",
        "settings",
        "privacy",
        "login_activity",
        # baad me aur routes add kar sakte ho
    ]

    if request.endpoint not in protected_routes:
        return

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT current_session
        FROM users
        WHERE username=?
    """, (session["username"],))

    row = cur.fetchone()

    conn.close()

    if not row or row[0] != session.get("session_id"):
        session.clear()
        return redirect("/login")


@app.route("/splash")
def splash():
    return render_template("splash.html")

@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO story_archive
        (
            username,
            image,
            caption,
            created_at
        )
        SELECT
            username,
            image,
            caption,
            created_at
        FROM stories
        WHERE datetime(created_at) <= datetime('now','-24 hours')
    """)

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

    # Remove posts from users blocked by the current user
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (current_user,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    posts = [
        post for post in posts
        if post[0] not in blocked_usernames
    ]

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
        
        # Current user liked this post?
        cur.execute(
            """
            SELECT 1
            FROM likes
            WHERE post_id=?
            AND username=?
            LIMIT 1
            """,
            (post_id, session["username"])
        )
        liked = cur.fetchone() is not None



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

        # -----------------------------------------------------
        # LOAD ALL MEDIA FOR THIS POST
        # -----------------------------------------------------

        cur.execute(
            """
            SELECT media_url, media_type, media_order
            FROM post_media
            WHERE post_id=?
            ORDER BY media_order ASC
            """,
            (post_id,)
        )

        media_rows = cur.fetchall()

        post_media_list = []

        for media_url, media_type, media_order in media_rows:

            post_media_list.append({
                "url": media_url,
                "type": media_type,
                "order": media_order
            })

        # Old posts may not have post_media rows.
        # Keep their original image working.
        if not post_media_list and post[1]:
            post_media_list.append({
                "url": post[1],
                "type": "image",
                "order": 0
            })

        print(
            "POST MEDIA DATA:",
            post_id,
            post_media_list
        )

        # Comment count
        cur.execute(
            "SELECT COUNT(*) FROM comments WHERE post_id=?",
            (post_id,)
        )
        comment_count = cur.fetchone()[0]

        # Share count
        cur.execute(
            "SELECT COUNT(*) FROM post_shares WHERE post_id=?",
            (post_id,)
        )
        share_count = cur.fetchone()[0]

        # -----------------------------------------------------
        # POST MUSIC FOR HOME FEED
        # Existing post data/indexes remain unchanged.
        # Music is appended at the end.
        # -----------------------------------------------------
        cur.execute(
            """
            SELECT audio, music_start, music_end
            FROM posts
            WHERE id=?
            """,
            (post_id,)
        )
        music_row = cur.fetchone()

        post_audio = music_row[0] if music_row and music_row[0] else ""
        post_music_start = music_row[1] if music_row and music_row[1] is not None else 0
        post_music_end = music_row[2] if music_row and music_row[2] is not None else 0

        # -----------------------------------------------------
        # POST TAGGED PEOPLE FOR HOME FEED
        # Existing tag system remains untouched.
        # Load username + profile photo only.
        # -----------------------------------------------------
        cur.execute(
            """
            SELECT
                pt.tagged_username,
                COALESCE(u.profile_pic, '')
            FROM post_tags pt
            LEFT JOIN users u
                ON u.username = pt.tagged_username
            WHERE pt.post_id=?
            ORDER BY pt.rowid ASC
            LIMIT 5
            """,
            (post_id,)
        )

        post_tagged_people = []

        for tag_username, tag_profile_pic in cur.fetchall():
            post_tagged_people.append({
                "username": tag_username,
                "profile_pic": tag_profile_pic or "/static/default.png"
            })

        posts_with_likes.append(
            post + (
                like_count,
                comments,
                post_media_list,
                comment_count,
                share_count,
                post_audio,
                post_music_start,
                post_music_end,
                post_tagged_people,
                liked
            )
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
        SELECT
            s1.id,
            s1.username,
            s1.image
        FROM stories s1
        JOIN users u
        ON s1.username = u.username

        WHERE s1.id = (
            SELECT MAX(s2.id)
            FROM stories s2
            WHERE s2.username = s1.username
              AND datetime(s2.created_at) >= datetime('now','-1 day')
        )

        AND datetime(s1.created_at) >= datetime('now','-1 day')
        AND s1.username != ?

        AND (

            u.story_privacy = 'everyone'

            OR (

                u.story_privacy = 'followers'

                AND EXISTS (

                    SELECT 1
                    FROM followers f
                    WHERE
                    f.follower_username = ?
                    AND f.followed_username = s1.username

                )

            )

            OR (

                u.story_privacy = 'close_friends'

                AND EXISTS (

                    SELECT 1
                    FROM close_friends cf
                    WHERE
                    cf.owner = s1.username
                    AND cf.friend = ?

                )

            )

        )

        ORDER BY s1.id DESC
    """, (
        current_user,
        current_user,
        current_user
    ))
    print("CURRENT USER AT QUERY =", current_user)


    story_circles = cur.fetchall()


    print("RAW STORY CIRCLES =", story_circles)

    print("BEFORE FILTER =", story_circles)

    story_circles = [
    s for s in story_circles
    if s[1].strip() != current_user.strip()
]

    print("FILTERED STORY CIRCLES =", story_circles)

    # Users blocked by the current account
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (current_user,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    story_circles = [
        s for s in story_circles
        if s[1] not in blocked_usernames
    ]

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
        SELECT id, username, image, audio, music_start, music_end, media_type, caption
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
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7]
        )

    my_story_file = row[2] if row else None


    cur.execute("""
        SELECT id, username, image, audio, music_start, music_end, media_type, caption
        FROM stories
        WHERE datetime(created_at) >= datetime('now','-1 day')
        ORDER BY username, id DESC
    """)

    all_stories = cur.fetchall()

    all_stories = [
        story for story in all_stories
        if story[1] not in blocked_usernames
    ]

    cur.execute("""
        SELECT id,username,image,audio,music_start,music_end,media_type,caption
        FROM stories
        WHERE username!=?
        ORDER BY id DESC
    """, (current_user,))

    friends_stories = cur.fetchall()

    friends_stories = [
        story for story in friends_stories
        if story[1] not in blocked_usernames
    ]




    cur.execute("""
        SELECT id, username, image, audio, music_start, music_end, media_type, caption
        FROM stories
        WHERE datetime(created_at) >= datetime('now','-1 day')
        ORDER BY username, id DESC
    """)

    all_user_stories = cur.fetchall()

    all_user_stories = [
        story for story in all_user_stories
        if story[1] not in blocked_usernames
    ]


    cur.execute("""
        SELECT followed_username
        FROM followers
        WHERE follower_username=?
    """, (current_user,))

    following_users = [row[0].strip() for row in cur.fetchall()]


    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
    SELECT DISTINCT
    CASE
    WHEN sender=? THEN receiver
    ELSE sender
    END AS username
    FROM messages
    WHERE sender=? OR receiver=?
    ORDER BY id DESC
    """,(
        session["username"],
        session["username"],
        session["username"]
    ))

    recent_users=[]

    for row in cur.fetchall():

        cur.execute("""
        SELECT profile_pic
        FROM users
        WHERE username=?
        """,(row["username"],))

        u=cur.fetchone()

        recent_users.append({
            "username":row["username"],
            "profile_pic":u["profile_pic"] if u else "default.jpg"
        })

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
        all_stories=all_user_stories,
        current_user=current_user,
	recent_users=recent_users
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

        return redirect("w/login")

    return render_template("signup.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    import uuid
    session_id = str(uuid.uuid4())

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
        """, (username, password))

        user = cur.fetchone()

        if user:
            cur.execute("""
                UPDATE users
                SET is_online=1, current_session=?
                WHERE username=?
            """, (session_id, username))
            conn.commit()

            session["username"] = user["username"]
            session["name"] = user["name"]
            session["bio"] = user["bio"]
            session["profile_pic"] = user["profile_pic"]
            session["session_id"] = session_id

            device = request.headers.get("User-Agent")
            ip = request.remote_addr

            cur.execute("""
                INSERT INTO login_activity
                (username, device, ip_address, session_id)
                VALUES (?, ?, ?, ?)
            """, (username, device, ip, session_id))
            
            conn.commit()
            conn.close()

            return redirect("/splash")
        else:
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

    # Remove users blocked by the current account
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (my_username,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    all_users = [
        user for user in all_users
        if user["username"] not in blocked_usernames
    ]

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
		(
		    (sender=? AND receiver=?)
		    OR
		    (sender=? AND receiver=?)
		)
		AND (
		    message IS NULL
		    OR (
		        message NOT LIKE '📹 Video call%'
		        AND message NOT LIKE '📹 Missed video call%'
		        AND message NOT LIKE '📞 Voice call%'
		        AND message NOT LIKE '📞 Missed voice call%'
		    )
		)

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

# =========================
# CALL HISTORY
# =========================

    cur.execute("""
        SELECT
            id,
            caller,
            receiver,
            call_type,
            status,
            created_at,
            started_at,
            ended_at
        FROM calls
        WHERE
            (caller=? AND receiver=?)
            OR
            (caller=? AND receiver=?)
        ORDER BY id ASC
    """, (
        my_username,
        username,
        username,
        my_username
    ))

    call_rows = cur.fetchall()

    calls = []

    from datetime import datetime

    for row in call_rows:

        call_id = row[0]
        caller = row[1]
        receiver = row[2]
        call_type = row[3]
        status = row[4]
        created_at = row[5]
        started_at = row[6]
        ended_at = row[7]

        duration = None
        call_time = None

    # =========================
    # CALL RECEIVED
    # =========================
        if started_at and ended_at:

            try:
                start = datetime.fromisoformat(started_at)
                end = datetime.fromisoformat(ended_at)

                seconds = int((end - start).total_seconds())

                if seconds < 0:
                    seconds = 0

                minutes = seconds // 60
                secs = seconds % 60

                duration = f"{minutes} min {secs} sec"

            except Exception as e:

                print("DURATION ERROR =", e)

                duration = "0 min 0 sec"

        # =========================
        # CALL NOT RECEIVED
        # =========================
        else:

            try:

                if status == "missed" and ended_at:
                    dt = datetime.fromisoformat(ended_at)
                else:
                    dt = datetime.fromisoformat(created_at)

                call_time = dt.strftime("%I:%M %p").lstrip("0")

            except Exception:
                call_time = ""


        calls.append({
            "id": call_id,
            "caller": caller,
            "receiver": receiver,
            "call_type": call_type,
            "status": status,
            "created_at": created_at,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration": duration,
            "call_time": call_time
        })

    print("CALLS FINAL =", calls)


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
    print("CALLS FINAL =", calls)
    return render_template(
        "chat.html",
        chats=chats,
        chat_with=username,
        profile_url=profile_url,
        is_online=is_online,
        last_seen=last_seen,
    calls=calls
    )



@app.route("/video_call/<username>")
def video_call(username):
    if "username" not in session:
        return redirect("/login")

    return render_template(
        "video_call.html",
        chat_with=username
    )

@app.route("/chat_messages/<username>")
def chat_messages(username):

    if "username" not in session:
        return jsonify([])

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            sender,
            receiver,
            message,
            reel_id,
            reel_thumbnail,
            is_seen,
            timestamp,
            image,
            audio,
            deleted,
            video
        FROM messages
	WHERE
	(
	    (sender=? AND receiver=?)
	    OR
	    (sender=? AND receiver=?)
	)
	AND (
	    message IS NULL
	    OR (
        	message NOT LIKE '📹 Video call%'
	        AND message NOT LIKE '📹 Missed video call%'
	        AND message NOT LIKE '📞 Voice call%'
        	AND message NOT LIKE '📞 Missed voice call%'
	    )
	)

        ORDER BY id ASC
    """, (
        my_username,
        username,
        username,
        my_username
    ))

    rows = cur.fetchall()

    data = []

    for row in rows:
        data.append({
            "id": row["id"],
            "sender": row["sender"],
            "receiver": row["receiver"],
            "message": row["message"] or "",
            "reel_id": row["reel_id"],
            "reel_thumbnail": row["reel_thumbnail"],
            "is_seen": row["is_seen"] or 0,
            "time": time_ago(row["timestamp"]) if row["timestamp"] else "",
            "image": row["image"],
            "audio": row["audio"],
            "deleted": row["deleted"] or 0,
            "video": row["video"]
        })

    conn.close()

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

    my_username = session["username"]

    cur.execute(
        "SELECT message_privacy FROM users WHERE username=?",
        (username,)
    )

    row = cur.fetchone()

    if row:

        privacy = row[0]

        if privacy == "nobody":
            conn.close()
            return jsonify({
                "status":"blocked",
                "message":"This user isn't accepting messages."
            })

        elif privacy == "followers":

            cur.execute("""
                SELECT 1
                FROM followers
                WHERE follower_username=?
                AND followed_username=?
            """, (
                my_username,
                username
            ))

            if cur.fetchone() is None:
                conn.close()
                return jsonify({
                    "status":"blocked",
                    "message":"Only followers can message this user."
                })


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


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "GET":
        return render_template("upload.html")

    if "username" not in session:
        return "User not logged in"

    username = session["username"]
    caption = request.form.get("caption", "")
    upload_type = request.form.get("type", "post")



    print("UPLOAD TYPE =", upload_type)

    # =========================================================
    # REEL
    # Existing Reel upload system kept separate
    # =========================================================
    if upload_type == "reel":

        file = request.files.get("file") or request.files.get("image")

        if not file or file.filename == "":
            return "No file uploaded"

        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as tmp:

                file.save(tmp.name)
                temp_path = tmp.name

            print("TEMP FILE =", temp_path)

            result = cloudinary.uploader.upload_large(
                temp_path,
                resource_type="video"
            )

            file_url = result["secure_url"]

            print("REEL UPLOAD SUCCESS =", file_url)

        except Exception as e:

            print("CLOUDINARY REEL ERROR =", e)

            return jsonify({
                "status": "error",
                "message": str(e)
            })

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        try:

            # -----------------------------------------------------
            # SAVE REEL MUSIC
            # Existing Post/Reel Music system sends these fields.
            # -----------------------------------------------------
            music_url = request.form.get("music_url", "").strip()

            try:
                music_start = float(request.form.get("music_start", 0) or 0)
            except Exception:
                music_start = 0.0

            try:
                music_end = float(request.form.get("music_end", 0) or 0)
            except Exception:
                music_end = 0.0

            cur.execute(
                """
                INSERT INTO reels(
                    username,
                    video,
                    caption,
                    audio,
                    music_start,
                    music_end
                )
                VALUES(?,?,?,?,?,?)
                """,
                (
                    username,
                    file_url,
                    caption,
                    music_url,
                    music_start,
                    music_end
                )
            )
            reel_id = cur.lastrowid
            
            # Save tagged users (Max 5 limit)
            tagged_users_str = request.form.get("tagged_users", "")
            if tagged_users_str:
                import json
                try:
                    tagged_list = json.loads(tagged_users_str)
                except:
                    tagged_list = [u.strip() for u in tagged_users_str.split(",") if u.strip()]
                
                for t_user in tagged_list[:5]:
                    cur.execute(
                        "INSERT INTO reel_tags (reel_id, tagged_username, status) VALUES (?, ?, 'pending')",
                        (reel_id, t_user)
                    )
            
            conn.commit()

            return jsonify({
                "status": "ok"
            })

        except Exception as e:

            conn.rollback()

            return jsonify({
                "status": "error",
                "message": str(e)
            })

        finally:
            conn.close()


    # =========================================================
    # STORY
    # Instagram-style Story upload
    # Supports IMAGE + VIDEO + MUSIC
    # =========================================================
    elif upload_type == "story":

        file = request.files.get("file") or request.files.get("image")

        if not file or not file.filename:
            return jsonify({
                "status": "error",
                "message": "No story media uploaded"
            }), 400

        # -----------------------------------------------------
        # STORY MEDIA TYPE
        # -----------------------------------------------------

        filename = file.filename.lower()

        if (
            (file.mimetype and file.mimetype.startswith("video/"))
            or filename.endswith((
                ".mp4",
                ".mov",
                ".webm",
                ".mkv",
                ".avi"
            ))
        ):
            media_type = "video"
        else:
            media_type = "image"

        print(
            "STORY MEDIA TYPE =",
            media_type,
            "| FILE =",
            file.filename
        )

        # -----------------------------------------------------
        # MUSIC DATA
        # -----------------------------------------------------

        music_url = request.form.get("music_url", "").strip()

        try:
            music_start = float(
                request.form.get("music_start", 0) or 0
            )
        except Exception:
            music_start = 0.0

        try:
            music_end = float(
                request.form.get("music_end", 0) or 0
            )
        except Exception:
            music_end = 0.0

        if music_start < 0:
            music_start = 0.0

        if music_end < 0:
            music_end = 0.0

        print(
            "STORY MUSIC =",
            music_url,
            "| START =",
            music_start,
            "| END =",
            music_end
        )

        # -----------------------------------------------------
        # CLOUDINARY UPLOAD
        # -----------------------------------------------------

        try:

            if media_type == "video":

                import tempfile

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                ) as tmp:

                    file.save(tmp.name)
                    temp_path = tmp.name

                result = cloudinary.uploader.upload_large(
                    temp_path,
                    resource_type="video"
                )

                try:
                    import os
                    os.remove(temp_path)
                except Exception:
                    pass

            else:

                result = cloudinary.uploader.upload(
                    file,
                    resource_type="image"
                )

            file_url = result["secure_url"]

            print(
                "STORY UPLOAD SUCCESS =",
                file_url
            )

        except Exception as e:

            print(
                "CLOUDINARY STORY ERROR =",
                e
            )

            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

        # -----------------------------------------------------
        # SAVE STORY
        # -----------------------------------------------------

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        try:

            cur.execute(
                """
                INSERT INTO stories(
                    username,
                    image,
                    caption,
                    media_type,
                    audio,
                    music_start,
                    music_end
                )
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    username,
                    audio_url,
                    caption,
                    media_type,
                    music_url if music_url else None,
                    music_start,
                    music_end
                )
            )

            story_id = cur.lastrowid

            conn.commit()

            print(
                "STORY CREATED:",
                story_id,
                "| TYPE:",
                media_type,
                "| MUSIC:",
                bool(music_url)
            )

            return jsonify({
                "status": "ok",
                "story_id": story_id,
                "media_type": media_type
            })

        except Exception as e:

            conn.rollback()

            print(
                "STORY DATABASE ERROR =",
                e
            )

            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

        finally:

            conn.close()


    # =========================================================
    # POST
    # Instagram-style MULTIPLE MEDIA upload
    # =========================================================

    files = request.files.getlist("files")

    # Backward compatibility:
    # old frontend still sending "file"
    if not files:
        old_file = request.files.get("file") or request.files.get("image")

        if old_file and old_file.filename:
            files = [old_file]

    if not files:
        return jsonify({
            "status": "error",
            "message": "No media selected"
        }), 400

    # Maximum 10 media items per post
    if len(files) > 10:
        return jsonify({
            "status": "error",
            "message": "Maximum 10 photos or videos allowed"
        }), 400

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    try:

        # -----------------------------------------------------
        # USER PROFILE PIC
        # -----------------------------------------------------

        cur.execute(
            "SELECT profile_pic FROM users WHERE username=?",
            (username,)
        )

        row = cur.fetchone()

        profile_pic = row[0] if row else "default.jpg"


        # -----------------------------------------------------
        # UPLOAD FIRST MEDIA
        # -----------------------------------------------------

        uploaded_media = []

        for order, media in enumerate(files):

            if not media or not media.filename:
                continue

            filename = media.filename.lower()

            if media.mimetype and media.mimetype.startswith("video/"):
                media_type = "video"
            elif filename.endswith((
                ".mp4",
                ".mov",
                ".webm",
                ".mkv",
                ".avi"
            )):
                media_type = "video"
            else:
                media_type = "image"


            print(
                "POST MEDIA UPLOAD:",
                order,
                media.filename,
                media_type
            )


            if media_type == "video":

                import tempfile

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                ) as tmp:

                    media.save(tmp.name)
                    temp_path = tmp.name

                result = cloudinary.uploader.upload_large(
                    temp_path,
                    resource_type="video"
                )

            else:

                print(
                    "CLOUDINARY IMAGE UPLOAD START:",
                    media.filename
                )

                import tempfile
                import os

                temp_path = None

                try:

                    suffix = ".jpg"

                    if filename.endswith(".png"):
                        suffix = ".png"
                    elif filename.endswith(".webp"):
                        suffix = ".webp"
                    elif filename.endswith(".jpeg"):
                        suffix = ".jpeg"

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as tmp:

                        media.save(tmp.name)
                        temp_path = tmp.name

                    print(
                        "IMAGE TEMP FILE CREATED:",
                        temp_path
                    )

                    result = cloudinary.uploader.upload(
                        temp_path,
                        resource_type="image",
                        timeout=120
                    )

                    print(
                        "CLOUDINARY IMAGE UPLOAD DONE:",
                        media.filename
                    )

                except Exception as upload_error:

                    print(
                        "CLOUDINARY IMAGE UPLOAD ERROR =",
                        repr(upload_error)
                    )

                    raise

                finally:

                    if temp_path:

                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass


            media_url = result["secure_url"]

            uploaded_media.append({
                "url": media_url,
                "type": media_type,
                "order": order
            })

            print(
                "POST MEDIA SUCCESS:",
                media_url
            )


        if not uploaded_media:

            conn.rollback()

            return jsonify({
                "status": "error",
                "message": "No valid media uploaded"
            }), 400


        # -----------------------------------------------------
        # CREATE ONE POST
        # -----------------------------------------------------

        first_media = uploaded_media[0]

        # -----------------------------------------------------
        # SAVE POST MUSIC
        # Existing Post/Reel Music system sends these fields.
        # -----------------------------------------------------
        music_url = request.form.get("music_url", "").strip()

        try:
            music_start = float(request.form.get("music_start", 0) or 0)
        except Exception:
            music_start = 0.0

        try:
            music_end = float(request.form.get("music_end", 0) or 0)
        except Exception:
            music_end = 0.0

        cur.execute(
            """
            INSERT INTO posts(
                username,
                image,
                caption,
                profile_pic,
                audio,
                music_start,
                music_end
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                username,
                first_media["url"],
                caption,
                profile_pic,
                music_url,
                music_start,
                music_end
            )
        )

        post_id = cur.lastrowid

        # -----------------------------------------------------
        # SAVE TAGGED PEOPLE
        # Maximum 5 mutual-follow users
        # -----------------------------------------------------

        import json

        tagged_users_raw = request.form.get(
            "tagged_users",
            "[]"
        )

        try:
            tagged_users = json.loads(tagged_users_raw)
        except Exception:
            tagged_users = []

        if not isinstance(tagged_users, list):
            tagged_users = []

        clean_tagged_users = []

        for tagged_username in tagged_users:

            if not isinstance(tagged_username, str):
                continue

            tagged_username = tagged_username.strip()

            if not tagged_username:
                continue

            if tagged_username == username:
                continue

            if tagged_username in clean_tagged_users:
                continue

            # Only mutual-follow users can be tagged
            cur.execute(
                """
                SELECT 1
                FROM followers f1
                INNER JOIN followers f2
                    ON f2.follower_username = f1.followed_username
                   AND f2.followed_username = f1.follower_username
                WHERE f1.follower_username = ?
                  AND f1.followed_username = ?
                LIMIT 1
                """
                ,
                (
                    username,
                    tagged_username
                )
            )

            if not cur.fetchone():
                continue

            clean_tagged_users.append(tagged_username)

            if len(clean_tagged_users) >= 5:
                break

        for tagged_username in clean_tagged_users:

            cur.execute(
                """
                INSERT OR IGNORE INTO post_tags(
                    post_id,
                    tagged_username
                )
                VALUES(?, ?)
                """,
                (
                    post_id,
                    tagged_username
                )
            )

            # -----------------------------------------------------
            # NOTIFICATION FOR TAGGED USER
            # -----------------------------------------------------

            cur.execute(
                """
                INSERT INTO notifications(
                    user_to,
                    user_from,
                    action,
                    post_id
                )
                VALUES(?,?,?,?)
                """,
                (
                    tagged_username,
                    username,
                    "tagged you in a post",
                    post_id
                )
            )

        
        # SAVE ALL MEDIA
        # -----------------------------------------------------

        for media in uploaded_media:

            cur.execute(
                """
                INSERT INTO post_media(
                    post_id,
                    media_url,
                    media_type,
                    media_order
                )
                VALUES(?,?,?,?)
                """,
                (
                    post_id,
                    media["url"],
                    media["type"],
                    media["order"]
                )
            )


        conn.commit()

        print(
            "POST CREATED:",
            post_id,
            "MEDIA:",
            len(uploaded_media)
        )


        return jsonify({
            "status": "ok",
            "post_id": post_id,
            "media_count": len(uploaded_media)
        })


    except Exception as e:

        conn.rollback()

        print(
            "POST UPLOAD ERROR =",
            e
        )

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

    # =========================================================
    # PROFILE POST COUNTS
    # Likes + Comments + Shares
    # =========================================================

    profile_posts = []

    for post in posts:

        post_id = post[0]

        # Like count
        cur.execute(
            "SELECT COUNT(*) FROM likes WHERE post_id=?",
            (post_id,)
        )
        like_count = cur.fetchone()[0]

        # Comment count
        cur.execute(
            "SELECT COUNT(*) FROM comments WHERE post_id=?",
            (post_id,)
        )
        comment_count = cur.fetchone()[0]

        # Share count
        cur.execute(
            "SELECT COUNT(*) FROM post_shares WHERE post_id=?",
            (post_id,)
        )
        share_count = cur.fetchone()[0]

        profile_posts.append(
            post + (
                like_count,
                comment_count,
                share_count
            )
        )

    posts = profile_posts

    # Reels
    cur.execute("""
        SELECT id, username, video, caption
        FROM reels
        WHERE username=?
        ORDER BY id DESC
    """, (username,))

    reels = cur.fetchall()

    # ACCEPTED TAGGED POSTS
    cur.execute("""
        SELECT
            pt.post_id,
            pt.tagged_username,
            pt.accepted,
            p.id,
            p.username,
            p.image,
            p.caption
        FROM post_tags pt
        INNER JOIN posts p
        ON p.id = pt.post_id
        WHERE pt.tagged_username=?
        AND pt.accepted=1
        ORDER BY p.id DESC
    """, (username,))

    tagged_posts = cur.fetchall()


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

    # Check whether current user is following this profile
    cur.execute("""
        SELECT 1
        FROM followers
        WHERE follower_username=?
        AND followed_username=?
    """, (session["username"], username))

    is_following = cur.fetchone() is not None

    conn.close()

    return render_template(
        "profile.html",

        username=username,
        name=name,
        bio=bio,
        profile_pic=profile_pic,

        posts=posts,
        reels=reels,
        tagged_posts=tagged_posts,

        posts_count=posts_count,
        reels_count=reels_count,

        followers=followers,
        following=following,

        is_following=is_following
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
            users.profile_pic,
            reels.audio,
            reels.music_start,
            reels.music_end
        FROM reels
        LEFT JOIN users
        ON reels.username = users.username
        ORDER BY reels.id DESC
    """)

    data = cur.fetchall()
    # Remove reels from users blocked by the current user
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (current_user,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    data = [
        reel for reel in data
        if reel[1] not in blocked_usernames
    ]


    reels = []

    for r in data:

        reel_id = r[0]

        # Like count
        cur.execute("""
            SELECT COUNT(*)
            FROM reel_likes
            WHERE reel_id=?
        """, (reel_id,))
        like_count = cur.fetchone()[0]

        # Current user liked?
        cur.execute("""
            SELECT id
            FROM reel_likes
            WHERE reel_id=?
            AND username=?
        """, (reel_id, current_user))
        liked = cur.fetchone() is not None

        # Comment count
        cur.execute("""
            SELECT COUNT(*)
            FROM reel_comments
            WHERE reel_id=?
        """, (reel_id,))
        comment_count = cur.fetchone()[0]

        # Comment list
        cur.execute("""
            SELECT username, comment
            FROM reel_comments
            WHERE reel_id=?
            ORDER BY id DESC
        """, (reel_id,))
        comment_list = cur.fetchall()

        reels.append({
            "id": reel_id,
            "username": r[1],
            "video": r[2],
            "caption": r[3],
            "profile_pic": r[4] if r[4] else "/static/default.png",
            "audio": r[5] if r[5] else "",
            "music_start": r[6] if r[6] is not None else 0,
            "music_end": r[7] if r[7] is not None else 0,
            "likes": like_count,
            "comments": comment_count,
            "liked": liked,
            "comment_list": comment_list
        })

    # =========================
    # CURRENT USER FOLLOWING
    # =========================

    cur.execute("""
        SELECT followed_username
        FROM followers
        WHERE follower_username=?
    """, (current_user,))

    following_users = [
        row[0].strip()
        for row in cur.fetchall()
    ]

    conn.close()

    print("REELS =", reels)
    print("FOLLOWING USERS =", following_users)

    return render_template(
        "reels.html",
        reels=reels,
        current_user=current_user,
        following_users=following_users
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

    cur.execute("""
        INSERT INTO post_shares
        (post_id, sender, receiver)
        VALUES (?, ?, ?)
    """, (
        post_id,
        session["username"],
        receiver
    ))

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

    search_rows = cur.fetchall()

    # Remove users blocked by the current account
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (current_user,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    users = []

    for row in search_rows:

        if row["username"] in blocked_usernames:
            continue

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
    print(users)
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
            timestamp,
            post_id
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

        action = row[1]

        # Tagged post acceptance status
        tag_accepted = False

        if action == "tagged you in a post" and row[3] is not None:
            cur.execute("""
                SELECT accepted
                FROM post_tags
                WHERE post_id=?
                  AND tagged_username=?
            """, (
                row[3],
                current_user
            ))

            tag_row = cur.fetchone()

            if tag_row:
                tag_accepted = bool(tag_row[0])

        if action == "like":
            text = " liked your post"
            link = "/"

        elif action == "comment":
            text = " commented on your post"
            link = "/"

        elif action == "follow":
            text = " started following you"
            link = f"/user/{user_from}"

        elif action == "reel_like":
            text = " liked your reel"
            link = "/reels"

        elif action == "reel_comment":
            text = " commented on your reel"
            link = "/reels"

        elif action == "mention":
            text = "@ mentioned you"
            link = "/"

        elif action == "support_reply":
            text = " Snapz Support replied to your support request."
            link = "/my_support"

        else:
            text = action
            link = "#"

        notifications.append({

            "username": user_from,
            "action": action,
            "text": text,
            "link": link,
            "time": row[2],
              "post_id": row[3],
              "tag_accepted": tag_accepted,
            "profile_pic": profile_pic,
            "following": is_following

        })

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications,
        current_user=current_user
    )




@app.route("/accept_reel_tag/<int:reel_id>", methods=["POST"])
def accept_reel_tag(reel_id):
    if "username" not in session:
        return jsonify({"status": "error", "message": "Login required"}), 401
    username = session["username"]
    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    cur.execute("UPDATE reel_tags SET status='accepted' WHERE reel_id=? AND tagged_username=?", (reel_id, username))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/reject_reel_tag/<int:reel_id>", methods=["POST"])
def reject_reel_tag(reel_id):
    if "username" not in session:
        return jsonify({"status": "error", "message": "Login required"}), 401
    username = session["username"]
    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM reel_tags WHERE reel_id=? AND tagged_username=?", (reel_id, username))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/accept_tag/<int:post_id>", methods=["POST"])
def accept_tag(post_id):

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE post_tags
        SET accepted=1
        WHERE post_id=?
          AND tagged_username=?
    """, (post_id, username))

    changed = cur.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return jsonify({
            "status": "error",
            "message": "Tag not found"
        }), 404

    return jsonify({
        "status": "ok",
        "message": "Tag accepted"
    })


@app.route("/reject_tag/<int:post_id>", methods=["POST"])
def reject_tag(post_id):

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM post_tags
        WHERE post_id=?
          AND tagged_username=?
    """, (post_id, username))

    changed = cur.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return jsonify({
            "status": "error",
            "message": "Tag not found"
        }), 404

    return jsonify({
        "status": "ok",
        "message": "Tag rejected"
    })


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
        """
        SELECT id, username, image, caption
        FROM posts
        WHERE username=?
        AND COALESCE(is_hidden, 0)=0
        ORDER BY id DESC
        """,
        (username,)
    )

    posts = cur.fetchall()

    # Reels
    cur.execute(
        """
        SELECT id, username, video, caption
        FROM reels
        WHERE username=?
        AND COALESCE(is_hidden, 0)=0
        ORDER BY id DESC
        """,
        (username,)
    )

    reels = cur.fetchall()

    # Tagged Posts
    cur.execute("""
    SELECT
    p.id,
    p.username,
    p.image,
    p.caption
    FROM post_tags pt
    INNER JOIN posts p
    ON p.id = pt.post_id
    WHERE pt.tagged_username=?
    AND pt.accepted=1
    AND COALESCE(p.is_hidden, 0)=0
    ORDER BY p.id DESC
    """, (username,))

    tagged_posts = cur.fetchall()

    # Hide all content from users blocked by the current account
    cur.execute(
        "SELECT 1 FROM blocked_users WHERE blocker=? AND blocked=?",
        (session["username"], username)
    )
    profile_user_is_blocked = cur.fetchone() is not None

    if profile_user_is_blocked:
        posts = []
        reels = []
        tagged_posts = []

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

    # Check whether logged-in user is following this profile
    cur.execute("""
        SELECT 1
        FROM followers
        WHERE follower_username=?
        AND followed_username=?
    """, (session["username"], username))

    is_following = cur.fetchone() is not None

    # Check whether logged-in user has blocked this profile
    cur.execute("""
        SELECT 1
        FROM blocked_users
        WHERE blocker=?
        AND blocked=?
    """, (session["username"], username))

    is_blocked = cur.fetchone() is not None

    conn.close()

    return render_template(
        "profile.html",
        username=username,
        user=user,
        profile_pic=user[5] or "default.jpg",
        posts=posts,
        tagged_posts=tagged_posts,
        reels=reels,
        posts_count=posts_count,
        followers=followers,
        following=following,
        is_following=is_following,
        is_blocked=is_blocked
    )


@app.route("/edit_post", methods=["POST"])
def edit_post():

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    data = request.get_json() or {}

    post_id = data.get("id")
    caption = data.get("caption", "")

    if not post_id:
        return jsonify({
            "status": "error",
            "message": "Post ID required"
        }), 400

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE posts
        SET caption=?
        WHERE id=?
        AND username=?
    """, (caption, post_id, username))

    changed = cur.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return jsonify({
            "status": "error",
            "message": "Post not found or permission denied"
        }), 403

    return jsonify({
        "status": "ok",
        "message": "Post updated"
    })


@app.route("/hide_post/<int:id>", methods=["POST"])
def hide_post(id):

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE posts
        SET is_hidden=1
        WHERE id=?
        AND username=?
    """, (id, username))

    changed = cur.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return jsonify({
            "status": "error",
            "message": "Post not found or permission denied"
        }), 403

    return jsonify({
        "status": "hidden"
    })


@app.route("/hide_reel/<int:id>", methods=["POST"])
def hide_reel(id):

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE reels
        SET is_hidden=1
        WHERE id=?
        AND username=?
    """, (id, username))

    changed = cur.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return jsonify({
            "status": "error",
            "message": "Reel not found or permission denied"
        }), 403

    return jsonify({
        "status": "hidden"
    })



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

# Comment count
            cur.execute(
                "SELECT COUNT(*) FROM comments WHERE post_id=?",
                (post_id,)
            )

            comment_count = cur.fetchone()[0]


# Share count
            cur.execute(
                "SELECT COUNT(*) FROM post_shares WHERE post_id=?",
                (post_id,)
            )

            share_count = cur.fetchone()[0]


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



@app.route("/tag_people_users")
def tag_people_users():

    if "username" not in session:
        return jsonify([])

    username = session["username"]
    query = request.args.get("q", "").strip()

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = """
        SELECT
            u.username,
            u.profile_pic
        FROM followers f1

        INNER JOIN followers f2
            ON f2.follower_username = f1.followed_username
           AND f2.followed_username = f1.follower_username

        INNER JOIN users u
            ON u.username = f1.followed_username

        WHERE f1.follower_username = ?
          AND f1.followed_username != ?
    """

    params = [username, username]

    if query:
        sql += """
            AND (
                LOWER(u.username) LIKE LOWER(?)
                OR LOWER(COALESCE(u.name, '')) LIKE LOWER(?)
            )
        """

        search = "%" + query + "%"

        params.extend([
            search,
            search
        ])

    sql += """
        ORDER BY LOWER(u.username) ASC
        LIMIT 100
    """

    cur.execute(
        sql,
        params
    )

    rows = cur.fetchall()

    # Remove users blocked by the current account
    cur.execute(
        "SELECT blocked FROM blocked_users WHERE blocker=?",
        (username,)
    )
    blocked_usernames = {row[0] for row in cur.fetchall()}

    rows = [
        row for row in rows
        if row["username"] not in blocked_usernames
    ]

    conn.close()

    result = []

    for row in rows:

        profile_pic = (
            row["profile_pic"]
            or "/static/default.png"
        )

        if (
            profile_pic
            and not (
                profile_pic.startswith("http://")
                or profile_pic.startswith("https://")
                or profile_pic.startswith("/")
            )
        ):
            profile_pic = (
                "/static/images/" +
                profile_pic
            )

        result.append({
            "username": row["username"],
            "profile_pic": profile_pic
        })

    return jsonify(result)


@app.route("/followers/<username>")
def followers(username):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            f.follower_username,
            u.profile_pic
        FROM followers f
        LEFT JOIN users u
            ON u.username = f.follower_username
        WHERE f.followed_username=?
    """, (username,))

    followers = cur.fetchall()

    following_usernames = set()
    # Hide users blocked by the current account
    if "username" in session:
        current_user = session["username"]

        cur.execute(
            "SELECT blocked FROM blocked_users WHERE blocker=?",
            (current_user,)
        )
        blocked_usernames = {row[0] for row in cur.fetchall()}

        followers = [
            row for row in followers
            if row[0] not in blocked_usernames
        ]

        # Check which followers are already followed by current user
        cur.execute("""
            SELECT followed_username
            FROM followers
            WHERE follower_username=?
        """, (current_user,))

        following_usernames = {
            row[0] for row in cur.fetchall()
        }

    conn.close()

    return render_template(
        "followers.html",
        username=username,
        followers=followers,
        following_usernames=following_usernames
    )


@app.route("/following/<username>")
def following(username):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            f.followed_username,
            u.profile_pic
        FROM followers f
        LEFT JOIN users u
            ON u.username = f.followed_username
        WHERE f.follower_username=?
    """, (username,))

    following = cur.fetchall()

    # Hide users blocked by the current account
    if "username" in session:
        current_user = session["username"]

        cur.execute(
            "SELECT blocked FROM blocked_users WHERE blocker=?",
            (current_user,)
        )
        blocked_usernames = {row[0] for row in cur.fetchall()}

        following = [
            row for row in following
            if row[0] not in blocked_usernames
        ]

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
            c.id,
            c.post_id,
            c.username,
            c.comment,
            c.timestamp,
            c.reply_to,
            u.profile_pic
        FROM comments c
        LEFT JOIN users u
            ON u.username = c.username
        WHERE c.post_id=?
        ORDER BY c.id ASC
    """, (post_id,))

    comments = []

    for row in cur.fetchall():

        comments.append({
            "id": row["id"],
            "post_id": row["post_id"],
            "username": row["username"],
            "comment": row["comment"],
            "time": row["timestamp"],
            "reply_to": row["reply_to"],
            "profile_pic": row["profile_pic"]
        })

    conn.close()

    return jsonify(comments)


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment_post(post_id):

    if "username" not in session:
        return jsonify({
            "status": "error",
            "message": "Login required"
        }), 401

    username = session["username"]

    comment = request.form.get("comment", "").strip()

    if comment == "":
        return jsonify({
            "status": "error",
            "message": "Comment is empty"
        })

    reply_to_raw = request.form.get("reply_to", "").strip()

    reply_to = None

    if reply_to_raw:
        try:
            reply_to = int(reply_to_raw)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid reply"
            })

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Post owner
    cur.execute("""
        SELECT username
        FROM posts
        WHERE id=?
    """, (post_id,))

    owner = cur.fetchone()

    if owner is None:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Post not found"
        })

    post_owner = owner[0]

    # Comment privacy check
    cur.execute(
        "SELECT comment_privacy FROM users WHERE username=?",
        (post_owner,)
    )

    row = cur.fetchone()

    if row:
        privacy = row[0]

        if privacy == "nobody":
            conn.close()
            return jsonify({
                "status": "blocked",
                "message": "Comments are disabled for this post."
            })

        elif privacy == "followers":

            cur.execute("""
                SELECT 1
                FROM followers
                WHERE follower_username=?
                AND followed_username=?
            """, (
                username,
                post_owner
            ))

            if cur.fetchone() is None:
                conn.close()
                return jsonify({
                    "status": "blocked",
                    "message": "Only followers can comment on this post."
                })

    # Validate reply target
    if reply_to is not None:

        cur.execute("""
            SELECT id, reply_to
            FROM comments
            WHERE id=?
            AND post_id=?
        """, (
            reply_to,
            post_id
        ))

        reply_target = cur.fetchone()

        if reply_target is None:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "Comment to reply to was not found."
            })

        # Replies stay one level deep.
        # If a user replies to a reply, attach it to the original comment.
        if reply_target[1] is not None:
            reply_to = reply_target[1]

    # Save comment / reply
    cur.execute("""
        INSERT INTO comments(
            post_id,
            username,
            comment,
            timestamp,
            reply_to
        )
        VALUES(
            ?,
            ?,
            ?,
            datetime('now','localtime'),
            ?
        )
    """, (
        post_id,
        username,
        comment,
        reply_to
    ))

    new_comment_id = cur.lastrowid

    # Notification
    if owner[0] != username:

        notification_action = "reply" if reply_to is not None else "comment"

        cur.execute("""
            INSERT INTO notifications(
                user_to,
                user_from,
                action
            )
            VALUES(?,?,?)
        """, (
            owner[0],
            username,
            notification_action
        ))

    conn.commit()

    # Comment count
    cur.execute("""
        SELECT COUNT(*)
        FROM comments
        WHERE post_id=?
    """, (post_id,))

    comment_count = cur.fetchone()[0]

    # Profile picture of newly created comment
    cur.execute("""
        SELECT profile_pic
        FROM users
        WHERE username=?
    """, (username,))

    profile_row = cur.fetchone()

    profile_pic = profile_row[0] if profile_row else None

    conn.close()

    return jsonify({
        "status": "ok",
        "id": new_comment_id,
        "username": username,
        "comment": comment,
        "reply_to": reply_to,
        "profile_pic": profile_pic,
        "comments": comment_count
    })


@app.route("/like_reel/<int:reel_id>", methods=["POST"])
def like_reel(reel_id):

    if "username" not in session:
        return jsonify({"status":"error"}), 401

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
    cur.execute("""
        SELECT 1
        FROM reel_likes
        WHERE username=? AND reel_id=?
    """, (liker, reel_id))

    if cur.fetchone():

        cur.execute("""
            DELETE FROM reel_likes
            WHERE username=? AND reel_id=?
        """, (liker, reel_id))

        conn.commit()

        cur.execute("""
            SELECT COUNT(*)
            FROM reel_likes
            WHERE reel_id=?
        """, (reel_id,))

        like_count = cur.fetchone()[0]

        conn.close()

        return jsonify({
            "status": "unliked",
            "likes": like_count
        })

    # Like Save
    cur.execute("""
        INSERT INTO reel_likes(username, reel_id)
        VALUES(?, ?)
    """, (liker, reel_id))

    # Notification
    if owner != liker:

        cur.execute("""
            INSERT INTO notifications
            (user_to, user_from, action)
            VALUES(?,?,?)
        """, (
            owner,
            liker,
            "liked your reel ❤️"
        ))

    conn.commit()

    cur.execute("""
        SELECT COUNT(*)
        FROM reel_likes
        WHERE reel_id=?
    """, (reel_id,))

    like_count = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "status": "liked",
        "likes": like_count
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

@app.route("/reel_comments/<int:reel_id>", methods=["GET"])
def get_reel_comments(reel_id):

    if "username" not in session:
        return {"status": "error", "message": "Login required"}, 401

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            rc.id,
            rc.reel_id,
            rc.username,
            rc.comment,
            rc.reply_to,
            u.profile_pic
        FROM reel_comments rc
        LEFT JOIN users u
            ON LOWER(u.username) = LOWER(rc.username)
        WHERE rc.reel_id=?
        ORDER BY rc.id ASC
    """, (reel_id,))

    rows = cur.fetchall()
    conn.close()

    comments = []

    for row in rows:
        comments.append({
            "id": row[0],
            "reel_id": row[1],
            "username": row[2],
            "comment": row[3],
            "reply_to": row[4],
            "profile_pic": row[5] or ""
        })

    return {
        "status": "ok",
        "comments": comments,
        "count": len(comments)
    }


@app.route("/comment_reel/<int:reel_id>", methods=["POST"])
def comment_reel(reel_id):

    if "username" not in session:
        return {"status": "error", "message": "Login required"}, 401

    comment = (request.form.get("comment") or "").strip()

    if not comment:
        return {
            "status": "error",
            "message": "Comment cannot be empty"
        }, 400

    reply_to = request.form.get("reply_to")

    if reply_to in (None, "", "null", "undefined"):
        reply_to = None
    else:
        try:
            reply_to = int(reply_to)
        except (TypeError, ValueError):
            reply_to = None

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM reels WHERE id=?",
        (reel_id,)
    )

    if not cur.fetchone():
        conn.close()
        return {
            "status": "error",
            "message": "Reel not found"
        }, 404

    # If replying to a reply, attach it to the
    # original top-level comment instead.
    if reply_to is not None:

        cur.execute("""
            SELECT id, reply_to
            FROM reel_comments
            WHERE id=? AND reel_id=?
        """, (reply_to, reel_id))

        target = cur.fetchone()

        if not target:
            conn.close()
            return {
                "status": "error",
                "message": "Reply target not found"
            }, 400

        if target[1] is not None:
            reply_to = target[1]

    username = session["username"]

    cur.execute("""
        INSERT INTO reel_comments
        (reel_id, username, comment, reply_to)
        VALUES (?, ?, ?, ?)
    """, (
        reel_id,
        username,
        comment,
        reply_to
    ))

    comment_id = cur.lastrowid

    cur.execute("""
        SELECT profile_pic
        FROM users
        WHERE LOWER(username)=LOWER(?)
        LIMIT 1
    """, (username,))

    pic_row = cur.fetchone()
    profile_pic = pic_row[0] if pic_row else ""

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "comment": {
            "id": comment_id,
            "reel_id": reel_id,
            "username": username,
            "comment": comment,
            "reply_to": reply_to,
            "profile_pic": profile_pic or ""
        }
    }


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

    # Reel exists + get video filename
    cur.execute("""
        SELECT video
        FROM reels
        WHERE id=?
    """, (reel_id,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return "Reel not found"

    reel_thumbnail = row[0]

    # Users list
    cur.execute("""
        SELECT username, profile_pic
        FROM users
        WHERE username!=?
        ORDER BY username
    """, (my_username,))

    users = cur.fetchall()

    conn.close()

    return render_template(
        "share_reel.html",
        users=users,
        reel_id=reel_id,
	reel_thumbnail=reel_thumbnail
    )

@app.route("/send_reel/<int:reel_id>/<username>")
def send_reel(reel_id, username):

    if "username" not in session:
        return redirect("/login")

    sender = session["username"]
    receiver = username

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

    cur.execute("""
        SELECT video
        FROM reels
        WHERE id=?
    """, (reel_id,))

    row = cur.fetchone()

    if row:
        thumbnail = row[0]
    else:
        thumbnail = ""


    # Send message
    cur.execute("""
        INSERT INTO messages
        (sender, receiver, message, reel_id, reel_thumbnail)
        VALUES (?, ?, ?, ?, ?)
        """, (
            sender,
            receiver,
            "",
            reel_id,
            thumbnail
    ))

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

    return redirect(f"/reels?play={reel_id}")



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

    # Blocked user story access protection
    cur.execute(
        "SELECT username FROM stories WHERE id=?",
        (story_id,)
    )
    story_owner_row = cur.fetchone()

    if story_owner_row:
        story_owner = story_owner_row[0]

        cur.execute(
            "SELECT 1 FROM blocked_users WHERE blocker=? AND blocked=?",
            (viewer, story_owner)
        )

        if cur.fetchone():
            conn.close()
            return jsonify({
                "status": "blocked"
            }), 403

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

    # User login hona zaroori hai
    if "username" not in session:
        return jsonify({
            "error": "login required"
        }), 401

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ==========================================
    # CHECK STORY OWNER
    # ==========================================

    cur.execute("""
        SELECT username
        FROM stories
        WHERE id=?
    """, (story_id,))

    story = cur.fetchone()

    # Story exist nahi karti
    if not story:
        conn.close()

        return jsonify({
            "error": "story not found"
        }), 404

    story_owner = story["username"]

    # ==========================================
    # ONLY STORY OWNER CAN SEE VIEWERS
    # ==========================================

    if str(story_owner).strip() != str(current_user).strip():

        conn.close()

        return jsonify({
            "error": "not allowed"
        }), 403

    # ==========================================
    # GET STORY VIEWERS
    # ==========================================

    cur.execute("""
        SELECT
            sv.viewer AS username,
            u.profile_pic AS profile_pic
        FROM story_views sv
        LEFT JOIN users u
            ON sv.viewer = u.username
        WHERE sv.story_id = ?
        ORDER BY sv.id ASC
    """, (story_id,))

    rows = cur.fetchall()

    viewers = []

    for row in rows:

        profile_pic = row["profile_pic"] or ""

        # Local profile image
        if profile_pic and not (
            profile_pic.startswith("http://")
            or profile_pic.startswith("https://")
            or profile_pic.startswith("/")
        ):
            profile_pic = "/static/images/" + profile_pic

        viewers.append({
            "username": row["username"] or "Unknown",
            "profile_pic": profile_pic
        })

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
            artist,
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
        SET status='answered',
            started_at=datetime('now','localtime')
        WHERE id=(
            SELECT id FROM calls
            WHERE caller=? AND receiver=?
            ORDER BY id DESC
            LIMIT 1
        )
    """, (
        data["from"],
        data["to"]
    ))

    conn.commit()
    conn.close()

    emit(
        "call-answered",
        data,
        room=data["from"]
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

    caller = data.get("from")
    receiver = data.get("to")
    call_type = data.get("type", "video")

    if not caller or not receiver:
        return


    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()


    # Find the latest active call in either direction.
    cur.execute("""
        SELECT id, caller, receiver, call_type, status, started_at
        FROM calls
        WHERE
            (
                caller=? AND receiver=?
            )
            OR
            (
                caller=? AND receiver=?
            )
        ORDER BY id DESC
        LIMIT 1
    """, (
        caller,
        receiver,
        receiver,
        caller
    ))

    row = cur.fetchone()


    if row:

        call_id = row[0]
        db_call_type = row[3] or call_type
        status = row[4]
        started_at = row[5]


        # Do not change an already missed/rejected call.
        if status not in ("missed", "ended"):

            cur.execute("""
                UPDATE calls
                SET
                    status='ended',
                    ended_at=datetime('now','localtime')
                WHERE id=?
            """, (call_id,))

            conn.commit()


            # Calculate duration only for an answered call.
            if status == "answered" and started_at:

                cur.execute("""
                    SELECT CAST(
                        strftime('%s', ended_at)
                        -
                        strftime('%s', started_at)
                        AS INTEGER
                    )
                    FROM calls
                    WHERE id=?
                """, (call_id,))

                result = cur.fetchone()
                seconds = (result[0] or 0) if result else 0

            else:
                seconds = 0


            minutes = seconds // 60
            sec = seconds % 60
            duration = f"{minutes} min {sec} sec"


            if db_call_type == "voice":

                save_system_message(
                    row[1],
                    row[2],
                    f"📞 Voice Call\n{duration}"
                )

                save_system_message(
                    row[2],
                    row[1],
                    f"📞 Voice Call\n{duration}"
                )

            else:

                save_system_message(
                    row[1],
                    row[2],
                    f"📹 Video Call\n{duration}"
                )

                save_system_message(
                    row[2],
                    row[1],
                    f"📹 Video Call\n{duration}"
                )

    conn.close()


    # Always notify the other phone so its WebRTC session
    # can immediately run cleanupCall().
    emit(
        "call-ended",
        {
            "from": caller,
            "to": receiver,
            "type": call_type
        },
        room=receiver
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


@socketio.on("video-call-ready")
def video_call_ready(data):
    emit(
        "video-call-ready",
        data,
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


@socketio.on("reject-call")
def reject_call(data):

    caller = data.get("from")
    receiver = data.get("to")
    call_type = data.get("type", "video")

    if not caller or not receiver:
        return


    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()


    cur.execute("""
        SELECT id, caller, receiver, call_type, status
        FROM calls
        WHERE
            (
                caller=? AND receiver=?
            )
            OR
            (
                caller=? AND receiver=?
            )
        ORDER BY id DESC
        LIMIT 1
    """, (
        caller,
        receiver,
        receiver,
        caller
    ))

    row = cur.fetchone()


    if row and row[4] not in ("missed", "ended"):

        cur.execute("""
            UPDATE calls
            SET
                status='missed',
                ended_at=datetime('now','localtime')
            WHERE id=?
        """, (row[0],))

        conn.commit()


    conn.close()


    # Notify both sides so either side can immediately
    # terminate any active WebRTC resources.
    emit(
        "call-rejected",
        {
            "from": caller,
            "to": receiver,
            "type": call_type
        },
        room=receiver
    )

    emit(
        "call-rejected",
        {
            "from": caller,
            "to": receiver,
            "type": call_type
        },
        room=caller
    )


@app.route("/menu")
def menu():

    if "username" not in session:
        return redirect("/login")

    return render_template("menu.html")


@app.route("/settings")
def settings():

    if "username" not in session:
        return redirect("/login")

    return render_template("settings.html")


@app.route("/settings/sound")
def sound_settings():

    if "username" not in session:
        return redirect("/login")

    return render_template("sound_settings.html")

@app.route("/account")
def account():

    if "username" not in session:
        return redirect("/login")

    return render_template("account.html")



@app.route("/change_email")
def change_email():
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    c = conn.cursor()

    c.execute(
        "SELECT email FROM users WHERE username=?",
        (session["username"],)
    )

    email = c.fetchone()[0]

    conn.close()

    return render_template("change_email.html", email=email)


@app.route("/send_change_email_otp", methods=["POST"])
def send_change_email_otp():

    if "username" not in session:
        return "Login First"

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT email FROM users WHERE username=?",
        (session["username"],)
    )

    email = cur.fetchone()[0]
    conn.close()

    otp = str(random.randint(100000,999999))

    session["change_email_otp"] = otp

    msg = Message(
        "Snapz Email Change OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body = f"Your OTP is: {otp}"

    mail.send(msg)

    return "OTP Sent Successfully"


@app.route("/verify_change_email_otp", methods=["POST"])
def verify_change_email_otp():

    otp = request.form.get("otp")

    if otp == session.get("signup_otp"):

        session["email_verified"] = True

        return redirect("/new_email")

    otp = request.form.get("otp")

    print("Entered OTP:", otp)
    print("Session OTP:", session.get("change_email_otp"))


    if otp != session.get("change_email_otp"):
        return "Invalid OTP"


@app.route("/save_new_email", methods=["POST"])
def save_new_email():

    otp = request.form["otp"]

    if otp != session.get("change_email_otp"):
        return "Invalid OTP"

    new_email = request.form["new_email"]
    confirm = request.form["confirm_email"]

    if new_email != confirm:
        return "Emails do not match"

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE email=?",
        (new_email,)
    )

    if cur.fetchone():
        conn.close()
        return "Email already exists"

    cur.execute(
        "UPDATE users SET email=? WHERE username=?",
        (new_email, session["username"])
    )

    conn.commit()
    conn.close()

    session.pop("change_email_otp", None)

    return redirect("/account")

@app.route("/change_mobile")
def change_mobile():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT mobile FROM users WHERE username=?",
        (session["username"],)
    )

    row = cur.fetchone()
    conn.close()

    mobile = row[0] if row and row[0] else ""

    return render_template(
        "change_mobile.html",
        mobile=mobile
    )
@app.route("/save_new_mobile", methods=["POST"])
def save_new_mobile():

    if "username" not in session:
        return redirect("/login")

    new_mobile = request.form.get("new_mobile")
    confirm_mobile = request.form.get("confirm_mobile")

    if new_mobile != confirm_mobile:
        return "Mobile numbers do not match"

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE mobile=?",
        (new_mobile,)
    )

    if cur.fetchone():
        conn.close()
        return "Mobile number already exists"

    cur.execute(
        "UPDATE users SET mobile=? WHERE username=?",
        (new_mobile, session["username"])
    )

    conn.commit()
    conn.close()

    return redirect("/account")

@app.route("/privacy")
def privacy():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT private_account, activity_status, message_privacy, comment_privacy,story_privacy
        FROM users
        WHERE username=?
    """,(session["username"],))

    row = cur.fetchone()
    conn.close()

    return render_template(
        "privacy.html",
        private_account=row[0],
        activity_status=row[1],
	message_privacy=row[2],
	comment_privacy=row[3],
	story_privacy=row[4]
    )


@app.route("/update_privacy", methods=["POST"])
def update_privacy():

    if "username" not in session:
        return "Login"

    setting = request.form.get("setting")
    value = request.form.get("value")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if setting == "private":

        cur.execute("""
        UPDATE users
        SET private_account=?
        WHERE username=?
        """,(value,session["username"]))

    elif setting == "activity":

        cur.execute("""
        UPDATE users
        SET activity_status=?
        WHERE username=?
        """,(value,session["username"]))

    conn.commit()
    conn.close()

    return "OK"





@app.route("/message_privacy", methods=["GET", "POST"])
def message_privacy():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if request.method == "POST":

        value = request.form["privacy"]

        cur.execute(
            "UPDATE users SET message_privacy=? WHERE username=?",
            (value, username)
        )

        conn.commit()

        conn.close()

        return redirect("/privacy")

    cur.execute(
        "SELECT message_privacy FROM users WHERE username=?",
        (username,)
    )

    privacy = cur.fetchone()[0]

    conn.close()

    return render_template(
        "message_privacy.html",
        privacy=privacy
    )

@app.route("/comment_privacy", methods=["GET","POST"])
def comment_privacy():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if request.method == "POST":

        value = request.form["privacy"]

        cur.execute(
            "UPDATE users SET comment_privacy=? WHERE username=?",
            (value, username)
        )

        conn.commit()
        conn.close()

        return redirect("/privacy")

    cur.execute(
        "SELECT comment_privacy FROM users WHERE username=?",
        (username,)
    )

    privacy = cur.fetchone()[0]

    conn.close()

    return render_template(
        "comment_privacy.html",
        privacy=privacy
    )

@app.route("/story_privacy", methods=["GET","POST"])
def story_privacy():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if request.method == "POST":

        value = request.form["privacy"]

        cur.execute(
            "UPDATE users SET story_privacy=? WHERE username=?",
            (value, username)
        )

        conn.commit()
        conn.close()

        return redirect("/privacy")

    cur.execute(
        "SELECT story_privacy FROM users WHERE username=?",
        (username,)
    )

    privacy = cur.fetchone()[0]

    conn.close()

    return render_template(
        "story_privacy.html",
        privacy=privacy
    )


@app.route("/close_friends")
def close_friends():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT followed_username
        FROM followers
        WHERE follower_username=?
    """, (username,))

    following = [x[0] for x in cur.fetchall()]

    cur.execute("""
        SELECT friend
        FROM close_friends
        WHERE owner=?
    """, (username,))

    selected = [x[0] for x in cur.fetchall()]

    conn.close()

    return render_template(
        "close_friends.html",
        following=following,
        selected=selected
    )


@app.route("/toggle_close_friend/<username>", methods=["POST"])
def toggle_close_friend(username):

    if "username" not in session:
        return jsonify({"status":"error"})

    owner = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM close_friends
        WHERE owner=?
        AND friend=?
    """, (
        owner,
        username
    ))

    row = cur.fetchone()

    if row:

        cur.execute("""
            DELETE FROM close_friends
            WHERE owner=?
            AND friend=?
        """, (
            owner,
            username
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "status":"removed"
        })

    cur.execute("""
        INSERT INTO close_friends(
            owner,
            friend
        )
        VALUES(?,?)
    """, (
        owner,
        username
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"added"
    })



@app.route("/story_archive")
def story_archive():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            image,
            caption,
            created_at
        FROM story_archive
        WHERE username=?
        ORDER BY id DESC
    """, (
        session["username"],
    ))

    stories = cur.fetchall()

    conn.close()

    return render_template(
        "story_archive.html",
        stories=stories
    )


@app.route("/story_archive/<int:story_id>")
def view_archive_story(story_id):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            image,
            caption,
            created_at
        FROM story_archive
        WHERE id=?
        AND username=?
    """, (
        story_id,
        session["username"]
    ))

    story = cur.fetchone()

    conn.close()

    if not story:
        return redirect("/story_archive")

    return render_template(
        "view_archive_story.html",
        story=story
    )


@app.route("/share_archive_story/<int:story_id>", methods=["POST"])
def share_archive_story(story_id):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            image,
            caption
        FROM story_archive
        WHERE id=?
        AND username=?
    """, (
        story_id,
        session["username"]
    ))

    row = cur.fetchone()

    if not row:
        conn.close()
        return redirect("/story_archive")

    cur.execute("""
        INSERT INTO stories(
            username,
            image,
            caption
        )
        VALUES(?,?,?)
    """, (
        session["username"],
        row[0],
        row[1]
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete_archive_story/<int:story_id>", methods=["POST"])
def delete_archive_story(story_id):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM story_archive
        WHERE id=?
        AND username=?
    """, (
        story_id,
        session["username"]
    ))

    conn.commit()
    conn.close()

    return redirect("/story_archive")





@app.route("/account_info")
def account_info():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT username,name,bio,email,mobile,profile_pic
    FROM users
    WHERE username=?
    """,(session["username"],))

    user = cur.fetchone()

    conn.close()

    return render_template(
        "account_info.html",
        user=user
    )

@app.route("/download_account_data")
def download_account_data():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # User
    cur.execute("""
        SELECT username,name,bio,email,mobile,profile_pic
        FROM users
        WHERE username=?
    """,(username,))
    user = cur.fetchone()

    # Posts
    cur.execute("""
        SELECT caption,image
        FROM posts
        WHERE username=?
    """,(username,))
    posts = cur.fetchall()

    # Reels
    cur.execute("""
        SELECT caption,video
        FROM reels
        WHERE username=?
    """,(username,))
    reels = cur.fetchall()

    conn.close()

    data = {

        "Username": user[0],
        "Name": user[1],
        "Bio": user[2],
        "Email": user[3],
        "Mobile": user[4],
        "Profile Photo": user[5],
        "Posts": posts,
        "Reels": reels

    }

    file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".json",
        mode="w",
        encoding="utf-8"
    )

    json.dump(data,file,indent=4)

    file.close()

    return send_file(
        file.name,
        as_attachment=True,
        download_name=f"{username}_Account_Info.json"
    )


@app.route("/blocked_accounts")
def blocked_accounts():

    if "username" not in session:
        return redirect("/login")

    me = session["username"]

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""

        SELECT users.username,
               users.profile_pic

        FROM blocked_users

        JOIN users

        ON blocked_users.blocked = users.username

        WHERE blocker=?

        ORDER BY users.username

    """,(me,))

    users = cur.fetchall()

    conn.close()

    return render_template(
        "blocked_accounts.html",
        users=users
    )

@app.route("/block/<username>")
def block_user(username):

    if "username" not in session:
        return redirect("/login")

    me = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM blocked_users WHERE blocker=? AND blocked=?",
        (me, username)
    )

    already = cur.fetchone()

    if not already:
        cur.execute(
            "INSERT INTO blocked_users(blocker,blocked) VALUES(?,?)",
            (me, username)
        )
        conn.commit()

    conn.close()

    return redirect("/profile/" + username)

@app.route("/report_user/<username>", methods=["GET", "POST"])
def report_user(username):
    if "username" not in session:
        return redirect("/login")

    me = session["username"]

    if me == username:
        return "You cannot report yourself", 400

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT username FROM users WHERE username=?",
        (username,)
    )

    if not cur.fetchone():
        conn.close()
        return "User not found", 404

    if request.method == "GET":
        conn.close()
        return render_template(
            "report_user.html",
            reported_username=username,
            submitted=False
        )

    reason = (request.form.get("reason") or "").strip()

    allowed_reasons = {
        "Spam or unwanted content",
        "Harassment or bullying",
        "Hate speech or symbols",
        "Violence or dangerous content",
        "Nudity or sexual content",
        "Scam or fraud",
        "Fake account or impersonation",
        "Something else"
    }

    if reason not in allowed_reasons:
        conn.close()
        return render_template(
            "report_user.html",
            reported_username=username,
            submitted=False,
            error="Please select a reason."
        )

    cur.execute(
        "SELECT 1 FROM user_reports WHERE reporter=? AND reported=?",
        (me, username)
    )

    existing = cur.fetchone()

    if existing:
        cur.execute(
            """
            UPDATE user_reports
            SET reason=?
            WHERE reporter=? AND reported=?
            """,
            (reason, me, username)
        )
    else:
        cur.execute(
            """
            INSERT INTO user_reports(reporter, reported, reason)
            VALUES(?, ?, ?)
            """,
            (me, username, reason)
        )

    conn.commit()
    conn.close()

    return render_template(
        "report_user.html",
        reported_username=username,
        submitted=True,
        selected_reason=reason
    )


@app.route("/unblock/<username>")
def unblock_user(username):

    if "username" not in session:
        return redirect("/login")

    me = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM blocked_users WHERE blocker=? AND blocked=?",
        (me, username)
    )

    conn.commit()
    conn.close()

    return redirect("/blocked_accounts")

@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        password = request.form["password"]
        username = session["username"]

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cur.fetchone()

        if not user or user[0] != password:
            conn.close()
            return render_template(
                "delete_account.html",
                error="Incorrect password"
            )

        # Delete account
        cur.execute("DELETE FROM users WHERE username=?", (username,))
        cur.execute("DELETE FROM posts WHERE username=?", (username,))
        cur.execute("DELETE FROM reels WHERE username=?", (username,))
        cur.execute("DELETE FROM stories WHERE username=?", (username,))
        cur.execute("DELETE FROM comments WHERE username=?", (username,))
        cur.execute("DELETE FROM reel_comments WHERE username=?", (username,))
        cur.execute("DELETE FROM likes WHERE username=?", (username,))
        cur.execute("DELETE FROM reel_likes WHERE username=?", (username,))

        cur.execute(
            "DELETE FROM followers WHERE follower_username=? OR followed_username=?",
            (username, username)
        )

        cur.execute(
            "DELETE FROM messages WHERE sender=? OR receiver=?",
            (username, username)
        )

        cur.execute(
            "DELETE FROM notifications WHERE user_to=? OR user_from=?",
            (username, username)
        )

        cur.execute(
            "DELETE FROM typing WHERE sender=? OR receiver=?",
            (username, username)
        )

        cur.execute(
            "DELETE FROM calls WHERE caller=? OR receiver=?",
            (username, username)
        )


        conn.commit()
        conn.close()

        session.clear()

        return redirect("/login")

    return render_template("delete_account.html")



@app.route("/login_activity")
def login_activity():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            device,
            ip_address,
            login_time,
	    session_id
        FROM login_activity
        WHERE username=?
        ORDER BY id DESC
    """, (
        session["username"],
    ))

    devices = cur.fetchall()

    conn.close()

    return render_template(
        "login_activity.html",
        devices=devices,
	current_session=session.get("session_id")
    )

@app.route("/logout_device/<int:id>", methods=["POST"])
def logout_device(id):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM login_activity
        WHERE id=?
        AND username=?
    """,(
        id,
        session["username"]
    ))

    conn.commit()
    conn.close()

    return redirect("/login_activity")

@app.route("/logout_other_devices", methods=["POST"])
def logout_other_devices():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM login_activity
        WHERE username=?
        AND session_id != ?
    """, (
        session["username"],
        session["session_id"]
    ))

    conn.commit()
    conn.close()

    return redirect("/login_activity")


@app.route("/appearance", methods=["GET", "POST"])
def appearance():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":

        theme = request.form.get("theme")
        font_size = request.form.get("font_size")
        amoled = 1 if request.form.get("amoled") else 0

        cur.execute("""
        UPDATE users
        SET
            theme=?,
            font_size=?,
            amoled_mode=?
        WHERE username=?
        """, (
            theme,
            font_size,
            amoled,
            session["username"]
        ))

        conn.commit()

    cur.execute("""
    SELECT
        theme,
        font_size,
        amoled_mode
    FROM users
    WHERE username=?
    """, (session["username"],))

    user = cur.fetchone()

    conn.close()

    return render_template(
        "appearance.html",
        user=user
    )

@app.context_processor
def inject_appearance():

    if "username" not in session:
        return {}

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            theme,
            font_size,
            amoled_mode
        FROM users
        WHERE username=?
    """, (session["username"],))

    appearance = cur.fetchone()

    conn.close()

    return dict(appearance=appearance)


@app.route("/about")
def about_redirect():
    return redirect(url_for("about_snapz"))

@app.route("/about_snapz")
def about_snapz():

    return render_template("about_snapz.html")

@app.route("/whats_new")
def whats_new():
    return render_template("whats_new.html")


@app.route("/community_guidelines")
def community_guidelines():

    return render_template(
        "community_guidelines.html"
    )


@app.route("/report_problem")
def report_problem():

    if "username" not in session:
        return redirect("/login")

    return redirect("/help_center")


@app.route("/check_update")
def check_update():

    current_version = "1.0.0"
    latest_version = "1.0.0"

    return render_template(
        "check_update.html",
        current=current_version,
        latest=latest_version
    )


@app.route("/rate_snapz", methods=["GET","POST"])
def rate_snapz():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if request.method == "POST":

        rating = request.form.get("rating")
        feedback = request.form.get("feedback","").strip()

        cur.execute("""
        INSERT INTO app_reviews
        (
            username,
            rating,
            feedback
        )
        VALUES(?,?,?)
        """,(
            session["username"],
            rating,
            feedback
        ))

        conn.commit()
        conn.close()

        return render_template(
            "rate_snapz.html",
            success=True
        )

    conn.close()

    return render_template(
        "rate_snapz.html",
        success=False
    )


@app.route("/privacy_policy")
def privacy_policy():

    return render_template("privacy_policy.html")

@app.route("/terms")
def terms():

    return render_template("terms.html")

@app.route("/licenses")
def licenses():

    return render_template("licenses.html")

@app.route("/help_center", methods=["GET", "POST"])
def help_center():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        subject = request.form.get("subject", "").strip()

        message = request.form.get("message", "").strip()

        file = request.files.get("image")

        filename = ""

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            folder = "static/support"

            os.makedirs(folder, exist_ok=True)

            file.save(os.path.join(folder, filename))

        conn = sqlite3.connect("snapz.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO support_messages
            (
                username,
                subject,
                message,
                image
            )
            VALUES(?,?,?,?)
        """, (
            session["username"],
            subject,
            message,
            filename
        ))

        support_id = cur.lastrowid

        cur.execute("""
        INSERT INTO support_chat
        (
            support_id,
            sender,
            message
        )
        VALUES(?,?,?)
        """, (
            support_id,
            session["username"],
            message
        ))



        conn.commit()

        socketio.emit(
            "support_message",
            {
               "support_id": support_id,
               "sender": session["username"],
               "message": message
            },
            to="support_" + str(support_id)
        )

        conn.close()

        return render_template(
            "help_center.html",
            success=True
        )

    return render_template(
        "help_center.html",
        success=False
    )

ADMIN_USERNAME = "snapz_admin"

@app.route("/admin/support")
def admin_support():

    if "username" not in session:
        return redirect("/login")

    if session["username"] != ADMIN_USERNAME:
        return "Access Denied"

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM support_messages
        WHERE status='open'
    """)

    open_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM support_messages
        WHERE status='replied'
    """)

    replied_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM support_messages
    """)

    total_count = cur.fetchone()[0]

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    if search:

        cur.execute("""
            SELECT *
            FROM support_messages
            WHERE username LIKE ?
            AND status='open'
            ORDER BY created_at DESC
        """, (
            f"%{search}%",
        ))

    status = request.args.get("status", "open")

    if status == "replied":

        cur.execute("""
            SELECT *
            FROM support_messages
            WHERE status='replied'
            ORDER BY replied_at DESC
        """)

    else:

        cur.execute("""
            SELECT *
            FROM support_messages
            WHERE status='open'
            ORDER BY created_at DESC
        """)

    messages = cur.fetchall()
    conn.close()

    return render_template(
        "admin_support.html",
        messages=messages,
        open_count=open_count,
        replied_count=replied_count,
        total_count=total_count,
        current_tab=status
    )


@app.route("/admin/support/<int:support_id>", methods=["GET", "POST"])
def admin_support_view(support_id):

    if "username" not in session:
        return redirect("/login")

    if session["username"] != ADMIN_USERNAME:
        return "Access Denied"

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":

        reply = request.form.get("reply", "").strip()

        if reply:

            cur.execute("""
                INSERT INTO support_chat
                (
                    support_id,
                    sender,
                    message
                )
                VALUES(?,?,?)
            """, (
                support_id,
                "Snapz Support",
                reply
            ))

            socketio.emit(
                "support_message",
                {
                    "support_id": support_id,
                    "sender": "Snapz Support",
                    "message": reply
                },
                to="support_" + str(support_id)
            )

            cur.execute("""
                UPDATE support_messages
                SET
                    admin_reply=?,
                    status='replied',
                    replied_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                reply,
                support_id
            ))

            conn.commit()

            cur.execute("""
                SELECT username
                FROM support_messages
                WHERE id=?
            """, (
                support_id,
            ))

            user = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO notifications
                (
                    user_to,
                    user_from,
                    action
                )
                VALUES(?,?,?)
            """, (
                user,
                "Snapz Support",
                "support_reply"
            ))

            conn.commit()

            conn.close()

            return redirect(f"/admin/support/{support_id}")
    cur.execute("""
        SELECT *
        FROM support_messages
        WHERE id=?
    """, (
        support_id,
    ))

    message = cur.fetchone()
# ===============================
# Mark User messages as Seen
# ===============================

    cur.execute("""
        UPDATE support_chat
        SET seen=1
        WHERE support_id=?
        AND sender!='Snapz Support'
        AND seen=0
    """, (support_id,))

    conn.commit()

    cur.execute("""
        SELECT
            sender,
            message,
            created_at,
            seen
        FROM support_chat
        WHERE support_id=?
        ORDER BY id ASC
    """, (
        support_id,
    ))

    chat = cur.fetchall()


    conn.close()

    return render_template(
        "admin_support_chat.html",
        message=message,
        chat=chat
    )




@app.route("/my_support")
def my_support():

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM support_messages
        WHERE username=?
        ORDER BY id DESC
    """, (session["username"],))

    requests = cur.fetchall()

    print("SESSION USER =", session["username"])
    print("REQUESTS =", requests)

    conn.close()

    return render_template(
        "my_support.html",
        requests=requests
    )


@app.route("/my_support/<int:support_id>")
def support_chat(support_id):

    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM support_messages
        WHERE id=?
        AND username=?
    """, (
        support_id,
        session["username"]
    ))

    support = cur.fetchone()

    if not support:

        conn.close()

        return "Support Request Not Found"

# Admin ke messages ko Seen mark karo
    cur.execute("""
        UPDATE support_chat
        SET seen=1
        WHERE support_id=?
        AND sender='Snapz Support'
        AND seen=0
    """, (support_id,))

    conn.commit()


    if request.method == "POST":

        text = request.form.get("message", "").strip()

        if text:

            cur.execute("""
                INSERT INTO support_chat
                (
                    support_id,
                    sender,
                    message
                )
                VALUES(?,?,?)
            """, (
                support_id,
                session["username"],
                text
            ))

            cur.execute("""
                UPDATE support_messages
                SET status='open'
                WHERE id=?
            """, (
                support_id,
            ))

            conn.commit()

            return redirect(f"/my_support/{support_id}")

    cur.execute("""
        SELECT
            sender,
            message,
            created_at,
            seen
        FROM support_chat
        WHERE support_id=?
        ORDER BY id ASC
    """, (
        support_id,
    ))

    chat = cur.fetchall()

    conn.close()

    return render_template(
        "support_chat.html",
        support=support,
        chat=chat
    )

@app.route("/my_support/<int:support_id>", methods=["GET", "POST"])
def my_support_detail(support_id):


    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":

        text = request.form.get("message", "").strip()

        if text:

            cur.execute("""
                INSERT INTO support_chat
                (
                    support_id,
                    sender,
                    message
                )
                VALUES(?,?,?)
            """, (
                support_id,
                session["username"],
                text
            ))

            cur.execute("""
                UPDATE support_messages
                SET status='open'
                WHERE id=?
            """, (support_id,))

            conn.commit()

            return redirect(f"/my_support/{support_id}")

    cur.execute("""
        SELECT *
        FROM support_messages
        WHERE id=? AND username=?
    """, (
        support_id,
        session["username"]
    ))

    support = cur.fetchone()

# ===============================
# Mark Support messages as Seen
# ===============================

    cur.execute("""
        UPDATE support_chat
        SET seen=1
        WHERE support_id=?
        AND sender='Snapz Support'
        AND seen=0
    """, (support_id,))


    cur.execute("""
        SELECT sender,message,created_at, seen
        FROM support_chat
        WHERE support_id=?
        ORDER BY id ASC
    """, (support_id,))

    chat = cur.fetchall()

    conn.close()

    print("SUPPORT =", support)
    print("CHAT =", chat)

    print("LOADING my_support_detail.html")
    return render_template(
        "my_support_detail.html",
        support=support,
        chat=chat
    )



@app.route("/story", methods=["POST"])
def story():

    print("Story route called")

    if "username" not in session:
        return redirect("/login")


    # =====================
    # STORY MEDIA
    # =====================

    file = (
        request.files.get("file")
        or request.files.get("image")
    )


    # Old file-based music support
    music = request.files.get("music")


    # New Snapz Music Library support
    music_url = request.form.get(
        "music_url",
        ""
    ).strip()


    music_start = request.form.get(
        "music_start",
        "0"
    )


    music_end = request.form.get(
        "music_end",
        "0"
    )


    if not file:

        print("No media selected")

        return redirect("/")


    filename = (
        file.filename or ""
    ).lower()


    try:

        # =====================
        # VIDEO STORY
        # =====================

        if filename.endswith(
            (
                ".mp4",
                ".webm",
                ".mov",
                ".mkv",
                ".avi"
            )
        ):

            print(
                "Uploading Video..."
            )


            result = (
                cloudinary.uploader.upload(
                    file,
                    resource_type="video",
                    timeout=600
                )
            )


            media_type = "video"


        # =====================
        # IMAGE STORY
        # =====================

        else:

            print(
                "Uploading Image..."
            )


            result = (
                cloudinary.uploader.upload(
                    file,
                    resource_type="image"
                )
            )


            media_type = "image"


        media_url = result[
            "secure_url"
        ]


        print(
            "MEDIA URL =",
            media_url
        )


        # =====================
        # MUSIC
        # =====================

        audio_url = None


        # ---------------------------------
        # NEW MUSIC LIBRARY SYSTEM
        # ---------------------------------

        if music_url:

            audio_url = music_url

            print(
                "STORY MUSIC URL =",
                audio_url
            )


        # ---------------------------------
        # OLD FILE MUSIC SYSTEM
        # ---------------------------------

        elif (
            music
            and music.filename != ""
        ):

            print(
                "Uploading Music..."
            )


            audio_result = (
                cloudinary.uploader.upload(
                    music,
                    resource_type="video"
                )
            )


            audio_url = audio_result[
                "secure_url"
            ]


            print(
                "OLD MUSIC URL =",
                audio_url
            )


        # =====================
        # MUSIC TRIM VALUES
        # =====================

        try:

            music_start = float(
                music_start
            )

        except (
            ValueError,
            TypeError
        ):

            music_start = 0.0


        try:

            music_end = float(
                music_end
            )

        except (
            ValueError,
            TypeError
        ):

            music_end = 0.0


        # Make sure values are valid

        if music_start < 0:

            music_start = 0.0


        if music_end < 0:

            music_end = 0.0


        if (
            audio_url
            and music_end <= music_start
        ):

            print(
                "Invalid music range, resetting"
            )

            music_start = 0.0
            music_end = 0.0


    except Exception as e:

        print(
            "STORY ERROR =",
            e
        )

        return redirect("/")


    # =====================
    # SAVE DATABASE
    # =====================

    conn = sqlite3.connect(
        "snapz.db"
    )

    cur = conn.cursor()


    cur.execute(
        """
        INSERT INTO stories
        (
            username,
            image,
            caption,
            media_type,
            audio,
            music_start,
            music_end
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["username"],
            media_url,
            request.form.get(
                "caption",
                ""
            ),
            media_type,
            audio_url,
            music_start,
            music_end
        )
    )


    conn.commit()

    conn.close()


    print(
        "Story Saved"
    )

    print(
        "Story Music =",
        audio_url
    )

    print(
        "Music Start =",
        music_start
    )

    print(
        "Music End =",
        music_end
    )


    return redirect(
        url_for("home")
    )


@app.route("/music_library")
def music_library():

    if "username" not in session:
        return jsonify([])

    search = request.args.get("search", "").strip()

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if search:
        like = f"%{search}%"
        cur.execute("""
            SELECT
                id,
                title,
                artist,
                file_url,
                duration
            FROM music
            WHERE title LIKE ?
               OR artist LIKE ?
            ORDER BY id DESC
        """, (like, like))
    else:
        cur.execute("""
            SELECT
                id,
                title,
                artist,
                file_url,
                duration
            FROM music
            ORDER BY id DESC
        """)

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {
            "id": row["id"],
            "title": row["title"] or "",
            "artist": row["artist"] or "",
            "file_url": row["file_url"] or "",
            "audio_url": row["file_url"] or "",
            "duration": row["duration"] or ""
        }
        for row in rows
    ])


@app.route("/story_upload")
def story_upload():

    if "username" not in session:
        return redirect("/login")

    return render_template("story_upload.html")


@app.route("/support_chat_messages/<int:support_id>")
def support_chat_messages(support_id):

    if "username" not in session:
        return jsonify([])

    conn = sqlite3.connect("snapz.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            sender,
            message,
            created_at,
            seen
        FROM support_chat
        WHERE support_id=?
        ORDER BY id ASC
    """, (support_id,))

    rows = cur.fetchall()

    conn.close()

    return jsonify([dict(x) for x in rows])

@socketio.on("join_support")
def join_support(data):

    support_id = str(data["support_id"])

    join_room("support_" + support_id)


@socketio.on("join_support_admin")
def join_support_admin(data):

    support_id = str(data["support_id"])

    join_room("support_" + support_id)



@app.route("/story_viewers")
def story_viewers():
    return render_template("story_viewers.html")






init_db()


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )


