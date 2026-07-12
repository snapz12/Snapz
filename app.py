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

REELS = []

app = Flask(__name__, static_folder="static")
app.secret_key = "snapz123"


socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
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


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        otp = request.form.get('otp')

        if otp != session.get("signup_otp"):
            return "Invalid OTP"

        conn = sqlite3.connect('snapz.db')
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO users
        (username, name, email, profile_pic, password)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            name,
            email,
            "default.jpg",
            password
        ))

        conn.commit()
        conn.close()

        session.pop("signup_otp", None)

        return redirect('/login')

    return render_template('signup.html')





@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("snapz.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()

        if user:

            cur.execute(
                "UPDATE users SET is_online=1 WHERE username=?",
                (username,)
            )
            conn.commit()

            session["username"] = user["username"]
            session["name"] = user["name"]
            session["bio"] = user["bio"]
            session["profile_pic"] = user["profile_pic"]

            conn.close()
        return redirect("/")
        conn.close()
        return "Invalid username or password"

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
    ON
    (
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

    ORDER BY u.username
    """,(
            my_username,
            my_username,
            my_username
        ))
    all_users = cur.fetchall()

    friends_data = []

    for user in all_users:

        cur.execute("""
            SELECT sender, message, timestamp
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

        last_message = row[1] if row else "Tap to chat"

        friends_data.append({
            "username": user["username"],
            "profile_pic": user["profile_pic"] or "default.jpg",
            "last_message": last_message
        })

    conn.close()

    return render_template(
        "users.html",
        friends=friends_data
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

    # Send text message
    if request.method == "POST":

        msg = request.form.get("message", "").strip()

        if msg:

            conn = sqlite3.connect("snapz.db")
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO messages (sender, receiver, message)
                VALUES (?, ?, ?)
            """, (
                my_username,
                username,
                msg
            ))

            conn.commit()
            conn.close()

        return redirect(f"/chat/{username}")

    # Load chat
    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Seen update
    cur.execute("""
        UPDATE messages
        SET is_seen=1
        WHERE sender=? AND receiver=?
    """, (
        username,
        my_username
    ))

    conn.commit()

    # User info
    cur.execute("""
        SELECT profile_pic,is_online,last_seen
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

    conn.close()

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
            "deleted": r[7]
        })

    return render_template(
        "chat.html",
        chats=chats,
        chat_with=username,
        profile_pic=profile_pic,
        is_online=is_online,
        last_seen=last_seen
    )

@app.route("/chat_messages/<username>")
def chat_messages(username):

    print("SESSION =", session)
    print("USERNAME =", session.get("username"))
    print("CHAT WITH =", username)


    if "username" not in session:
        return []

    my_username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT id, sender, message, timestamp, is_seen, image, audio, deleted
    FROM messages
        WHERE
        (sender=? AND receiver=?)
        OR
        (sender=? AND receiver=?)
        ORDER BY id ASC
    """,
    (
        my_username,
        username,
        username,
        my_username
    ))

    rows = cur.fetchall()
    conn.close()

    data=[]

    for row in rows:
        data.append({
            "id": row[0],
            "sender": row[1],
            "message": row[2],
            "time": time_ago(row[3]),
            "is_seen": row[4],
            "image": row[5],
            "audio": row[6],
            "deleted": row[7]
        })

    return jsonify(data)


@app.route("/send_message/<username>", methods=["POST"])
def send_message(username):

    if "username" not in session:
        return jsonify({"status": "error"})

    message = request.form.get("message", "").strip()

    if message == "":
        return jsonify({"status": "empty"})

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages
        (sender, receiver, message)
        VALUES (?, ?, ?)
    """, (
        session["username"],
        username,
        message
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})




@app.route("/send_image/<username>", methods=["POST"])
def send_image(username):

    if "username" not in session:
        return jsonify({"status":"error"})

    if "image" not in request.files:
        return jsonify({"status":"no_image"})

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"status":"empty"})

    filename = str(int(time.time())) + "_" + file.filename


    result = cloudinary.uploader.upload(file)

    filename = result["secure_url"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages
        (sender, receiver, message, image)
        VALUES (?, ?, ?, ?)
    """, (
        session["username"],
        username,
        "",
        filename
    ))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})








@app.route("/send_audio/<username>", methods=["POST"])
def send_audio(username):

    if "username" not in session:
        return jsonify({"status": "error"})

    if "audio" not in request.files:
        return jsonify({"status": "no_audio"})

    file = request.files["audio"]

    if file.filename == "":
        return jsonify({"status": "empty"})

    filename = str(int(time.time())) + "_voice.webm"

    result = cloudinary.uploader.upload(file)

    filename = result["secure_url"]


    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages
        (sender, receiver, message, audio)
        VALUES (?, ?, ?, ?)
    """, (
        session["username"],
        username,
        "",
        filename
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


@app.route("/typing", methods=["POST"])
def typing():

    sender=request.form["sender"]
    receiver=request.form["receiver"]
    status=request.form["typing"]

    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    cur.execute("""
    SELECT id
    FROM typing
    WHERE sender=?
    AND receiver=?
    """,(sender,receiver))

    row=cur.fetchone()

    if row:

        cur.execute("""
        UPDATE typing
        SET typing=?
        WHERE id=?
        """,(status,row[0]))

    else:

        cur.execute("""
        INSERT INTO typing
        (sender,receiver,typing)
        VALUES(?,?,?)
        """,(sender,receiver,status))

    conn.commit()
    conn.close()

    return {"status":"ok"}

@app.route("/typing_status/<username>")
def typing_status(username):

    me=session["username"]

    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    cur.execute("""
    SELECT typing
    FROM typing
    WHERE sender=?
    AND receiver=?
    """,(username,me))

    row=cur.fetchone()

    conn.close()

    if row and row[0]==1:
        return {"typing":True}

    return {"typing":False}

@app.route("/delete_message/<int:msg_id>", methods=["POST"])
def delete_message(msg_id):

    if "username" not in session:
        return {"status":"error"}

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    UPDATE messages
    SET
    message='',
    image='',
    audio='',
    deleted=1
    WHERE id=?
    AND sender=?
    """,
    (msg_id, session["username"]))

    conn.commit()
    conn.close()

    return {"status":"ok"}


@app.route("/voice_call/<username>")
def voice_call(username):

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "voice_call.html",
        username=username
    )


@app.route("/video_call/<username>")
def video_call(username):

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "video_call.html",
        username=username
    )

@app.route("/start_call/<username>/<call_type>", methods=["POST"])
def start_call(username, call_type):

    if "username" not in session:
        return jsonify({"status":"login_required"})

    caller = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO calls
    (caller, receiver, call_type)
    VALUES (?,?,?)
    """,(caller, username, call_type))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/check_call")
def check_call():

    if "username" not in session:
        return jsonify({})

    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    cur.execute("""
    SELECT id,caller,call_type
    FROM calls
    WHERE receiver=?
    AND status='ringing'
    ORDER BY id DESC
    LIMIT 1
    """,(session["username"],))

    row=cur.fetchone()

    conn.close()

    if row:

        return jsonify({
            "id":row[0],
            "caller":row[1],
            "type":row[2]
        })

    return jsonify({})

@app.route("/accept_call/<int:call_id>", methods=["POST"])
def accept_call(call_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    UPDATE calls
    SET status='accepted'
    WHERE id=?
    """,(call_id,))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/reject_call/<int:call_id>", methods=["POST"])
def reject_call(call_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    UPDATE calls
    SET status='rejected'
    WHERE id=?
    """,(call_id,))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

@app.route("/call_status/<int:call_id>")
def call_status(call_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT status
    FROM calls
    WHERE id=?
    """,(call_id,))

    row = cur.fetchone()

    conn.close()

    if row:
        return jsonify({"status":row[0]})

    return jsonify({"status":"not_found"})






@app.route("/upload", methods=["POST"])
def upload():
    print("UPLOAD START")
    print(request.files)
    print(request.form)

    file = request.files.get("file") or request.files.get("image")
    if not file or file.filename == '':
        return "No file uploaded", 400

    original_filename = file.filename
    filename = f"{int(time.time())}_{original_filename}"

try:
    result = cloudinary.uploader.upload(file)
    filename = result["secure_url"]
    print("Cloudinary Upload Success:", filename)

    except Exception as e:
        print("Cloudinary Error:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    filename = result["secure_url"]

    if "username" not in session:
        return "User not logged in", 401

    username = session["username"]
    caption = request.form.get("caption", "")
    upload_type = request.form.get("type", "post")

    print("LOGGED USER:", username)
    print("RECEIVED TYPE:", upload_type)

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    if upload_type == "reel":
        global REELS
        cur.execute(
            "INSERT INTO reels(username, video, caption) VALUES(?,?,?)",
             (username, filename, caption)
        )

        REELS.append((username, filename, caption))



    elif upload_type == "story":
        cur.execute("""
            INSERT INTO stories
            (username,image)
            VALUES (?,?)
        """,
        (username, filename))

    else:
        cur.execute(
            "SELECT * FROM posts WHERE image=? AND caption=?",
            (filename, caption)
        )
        exist = cur.fetchone()

        if exist:
            conn.close()
            return redirect("/notifications")

        cur.execute(
            "SELECT profile_pic FROM users WHERE username=?",
            (username,)
        )

        user_data = cur.fetchone()

        if user_data:
            profile_pic = user_data[0]
        else:
            profile_pic = None

        cur.execute(
            "INSERT INTO posts(username, image, caption, profile_pic) VALUES(?,?,?,?)",
            (username, filename, caption, profile_pic)
        )

        print("USERNAME =", username)
        print("TYPE =", upload_type)
        print("FILE =", filename)
        print("CAPTION =", caption)

        conn.commit()
        print("UPLOAD SAVED SUCCESSFULLY")
        conn.close()

        return jsonify({"status": "ok"})

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, image, caption FROM posts WHERE username=? ORDER BY id DESC",
        (username,)
    )
    posts = cur.fetchall()

    cur.execute(
        "SELECT id, username, video, caption FROM reels WHERE username=? ORDER BY id DESC",
        (username,)
    )

    reels = cur.fetchall()

    cur.execute(
        "SELECT COUNT(*) FROM posts WHERE username=?",
        (username,)
    )
    posts_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM followers WHERE followed_username=?
        """, (username,))
    followers = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM followers WHERE follower_username=?
    """, (username,))
    following = cur.fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        username=username,
        posts=posts,
        reels=reels,
        posts_count=posts_count,
        followers=followers,
        following=following
    )

@app.route("/reels")
def reels():

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, video, caption
        FROM reels
        ORDER BY id DESC
    """)

    reels = cur.fetchall()

    new_reels = []

    for r in reels:

        cur.execute(
            "SELECT COUNT(*) FROM reel_likes WHERE reel_id=?",
            (r[0],)
        )

        like_count = cur.fetchone()[0]

        new_reels.append((
            r[0],  # id
            r[1],  # username
            r[2],  # video
            r[3],  # caption
            like_count
        ))

    reels = new_reels

    conn.close()

    print("SENDING REELS TO HTML:", reels)

    return render_template(
        "reels.html",
        reels=reels
    )

@app.route("/share_post", methods=["POST"])
def share_post():

    if "username" not in session:
        return {"status":"error"}

    data = request.get_json()

    receiver = data["receiver"]
    post_id = data["post_id"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT image, caption FROM posts WHERE id=?",
        (post_id,)
    )

    post = cur.fetchone()

    if not post:
        conn.close()
        return {"status":"error"}

    image = post[0]
    caption = post[1]

    cur.execute("""
        INSERT INTO messages
        (sender,receiver,message,image,timestamp)
        VALUES(?,?,?,?,datetime('now','localtime'))
    """,(
        session["username"],
        receiver,
        caption,
        image
    ))

    conn.commit()
    conn.close()

    return {"status":"ok"}

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

    return redirect("/login")


@app.route("/story", methods=["POST"])
def story():

    if "username" not in session:
        return redirect("/login")

    image = request.files["image"]

    result = cloudinary.uploader.upload(image)

    filename = result["secure_url"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO stories(username,image) VALUES(?,?)",
        (
            session["username"],
            filename
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route('/update_profile', methods=['POST'])
def update_profile():

    if 'username' not in session:
        return redirect(url_for('login'))

    print(request.files)
    print(request.form)

    new_name = request.form.get('name')
    new_username = request.form.get('username')
    new_bio = request.form.get('bio')

    old_username = session['username']

    conn = sqlite3.connect('snapz.db')
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

    # Users table update
    cur.execute(
        "UPDATE users SET name=?, username=?, bio=? WHERE username=?",
        (new_name, new_username, new_bio, old_username)
    )

    # Posts update
    cur.execute(
        "UPDATE posts SET username=? WHERE username=?",
        (new_username, old_username)
    )

    # Reels update
    cur.execute(
        "UPDATE reels SET username=? WHERE username=?",
        (new_username, old_username)
    )

    # Stories update
    cur.execute(
        "UPDATE stories SET username=? WHERE username=?",
        (new_username, old_username)
    )

    # Followers update
    cur.execute(
        "UPDATE followers SET follower_username=? WHERE follower_username=?",
        (new_username, old_username)
    )

    cur.execute(
        "UPDATE followers SET followed_username=? WHERE followed_username=?",
        (new_username, old_username)
    )



# Profile Photo Update

    file = request.files.get("profile_pic")

    print(request.files)
    print(file)

    if file and file.filename:

        folder_path = os.path.join("static", "images")
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{new_username}.jpg"

        result = cloudinary.uploader.upload(file)

        filename = result["secure_url"]

        print("PHOTO SAVED:", filename)

        cur.execute(
            "UPDATE users SET profile_pic=? WHERE username=?",
            (filename, new_username)
        )

        session["pfp"] = filename


    conn.commit() 
    conn.close()


    session['name'] = new_name
    session['username'] = new_username
    session['bio'] = new_bio

    return redirect(url_for('profile'))




@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('snapz.db')
    cur = conn.cursor()

    cur.execute("""
    SELECT
        users.username,
        users.name,
        users.profile_pic,
        CASE
            WHEN followers.follower_username IS NULL THEN 0
            ELSE 1
        END
    FROM users
    LEFT JOIN followers
    ON followers.followed_username = users.username
    AND followers.follower_username = ?
    WHERE users.username LIKE ?
       OR users.name LIKE ?
    """, (
        session.get("username", ""),
        "%"+query+"%",
        "%"+query+"%"
    ))

    results = cur.fetchall()
    conn.close()
    return jsonify(results)


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

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT user_from, action, timestamp
        FROM notifications
        WHERE user_to=?
        ORDER BY id DESC
    """, (session["username"],))

    rows = cur.fetchall()

    print("SESSION USER =", session["username"])
    print("ROWS =", rows)

    notifications = []

    for row in rows:

        user_from = row[0]

        cur.execute("""
            SELECT 1
            FROM followers
            WHERE follower_username=?
            AND followed_username=?
        """, (session["username"], user_from))

        is_following = cur.fetchone() is not None

        notifications.append((
            row[0],
            row[1],
            row[2],
            is_following
        ))

    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
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
        return {"status": "error"}

    follower = session["username"]

    if follower == username:
        return {"status": "error"}

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Already followed check
    cur.execute("""
        SELECT 1
        FROM followers
        WHERE follower_username=? AND followed_username=?
    """, (follower, username))

    if cur.fetchone():
        conn.close()
        from flask import redirect

        return redirect("/")

    # Insert follow
    cur.execute("""
        INSERT INTO followers (follower_username, followed_username)
        VALUES (?, ?)
    """, (follower, username))

    # Notification
    cur.execute("""
        INSERT INTO notifications (user_to, user_from, action)
        VALUES (?, ?, ?)
    """, (username, follower, "follow"))

    conn.commit()
    conn.close()

    return {"status": "followed"}


@app.route("/unfollow/<username>", methods=["POST"])
def unfollow(username):

    if "username" not in session:
        return {"status": "error"}

    follower = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM followers
        WHERE follower_username=? AND followed_username=?
    """, (follower, username))

    conn.commit()
    conn.close()

    return {"status": "unfollowed"}


@app.route("/delete_post/<int:id>", methods=["POST"])
def delete_post(id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM posts WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return "deleted"

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

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM reels WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return "deleted"


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


@app.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):

    username = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM likes WHERE post_id=? AND username=?",
        (post_id, username)
    )

    already = cur.fetchone()

    if already:

        cur.execute(
            "DELETE FROM likes WHERE post_id=? AND username=?",
            (post_id, username)
        )

        status = "unliked"

    else:

        cur.execute(
            "INSERT INTO likes(post_id, username) VALUES(?, ?)",
            (post_id, username)
        )

        status = "liked"

    conn.commit()

    cur.execute(
        "SELECT COUNT(*) FROM likes WHERE post_id=?",
        (post_id,)
    )

    total_likes = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "status": status,
        "likes": total_likes
    })

@app.route("/comments/<int:post_id>")
def get_comments(post_id):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT username, comment
        FROM comments
        WHERE post_id=?
        ORDER BY id ASC
    """, (post_id,))

    comments = cur.fetchall()

    conn.close()

    return jsonify(comments)

@app.route("/comment/<int:post_id>", methods=["POST"])
def comment_post(post_id):

    if "username" not in session:
        return jsonify({"error":"login required"}), 401

    username = session["username"]
    comment = request.form.get("comment")

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO comments(post_id, username, comment) VALUES(?,?,?)",
        (post_id, username, comment)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "username": username,
        "comment": comment
    })


@app.route("/like_reel/<int:reel_id>", methods=["POST"])
def like_reel(reel_id):

    if "username" not in session:
        return {"status": "error"}


    liker = session["username"]

    
    print("REEL LIKE HIT")
    print("REEL ID =", reel_id)

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    # Reel owner nikalo
    cur.execute(
        "SELECT username FROM reels WHERE id=?",
        (reel_id,)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return {"status": "error"}

    owner = row[0]

    cur.execute("""
        SELECT 1
        FROM reel_likes
        WHERE username=? AND reel_id=?
    """, (liker, reel_id))


    print("REEL ID:", reel_id)
    print("LIKER:", liker)

    if cur.fetchone():
        conn.close()
        return {"status": "already_liked"}

    cur.execute("SELECT * FROM reel_likes")
    print("REEL LIKES:", cur.fetchall())
    # Reel like save
    cur.execute("""
        INSERT INTO reel_likes (username, reel_id)
        VALUES (?, ?)
    """, (liker, reel_id))

    print("OWNER =", owner)
    print("LIKER =", liker)

    # Notification
    if owner != liker:
     cur.execute("""
        INSERT INTO notifications
        (user_to, user_from, action)
        VALUES (?, ?, ?)
     """, (
        owner,
        liker,
        "liked your reel ❤️"
     ))

    print("NOTIFICATION SAVED")

    cur.execute("""
        SELECT reel_id
        FROM reel_likes
        WHERE username=?
    """, (session["username"],))

    liked_reels = [row[0] for row in cur.fetchall()]

    print("CURRENT USER =", session["username"])
    print("LIKED REELS =", liked_reels)

    conn.commit()
    conn.close()

    return render_template(
    "reels.html",
    reels=reels,
    liked_reels=liked_reels
    )


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

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    my_username = session["username"]

    cur.execute(
        "SELECT username, profile_pic FROM users WHERE username != ?",
        (my_username,)
    )

    users = cur.fetchall()

    print("USERS =", users)

    conn.close()

    return render_template(
        "share_reel.html",
        users=users,
        reel_id=reel_id
    )

@app.route("/send_reel/<int:reel_id>/<username>")
def send_reel(reel_id,username):

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO messages
    (sender,receiver,message,reel_id)
    VALUES (?,?,?,?)
    """,
    (
        session["username"],
        username,
        "🎬 Shared a Reel",
        reel_id
    ))

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

@socketio.on("join")
def join(data):

    join_room(data["room"])

    if "username" in data:
        join_room(data["username"])

    emit(
        "joined",
        {"room": data["room"]},
        room=data["room"]
    )

@socketio.on("offer")
def offer(data):

    emit(
        "offer",
        data,
        room=data["room"],
        include_self=False
    )


@socketio.on("answer")
def answer(data):

    emit(
        "answer",
        data,
        room=data["room"],
        include_self=False
    )


@socketio.on("ice_candidate")
def ice_candidate(data):

    emit(
        "ice_candidate",
        data,
        room=data["room"],
        include_self=False
    )

@socketio.on("call_user")
def call_user(data):

    emit(
        "incoming_call",
        {
            "caller": data["caller"],
            "room": data["room"],
            "type": data["type"]
        },
        room=data["receiver"]
    )



init_db()


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )
