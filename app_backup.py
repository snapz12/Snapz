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
REELS = []



app = Flask(__name__, static_folder="static")

conn = sqlite3.connect('database.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, name TEXT, bio TEXT, profile_pic TEXT)''')
conn.commit()


app.secret_key = "snapz_secret"

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


    conn.commit()
    conn.close()



@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    current_user = session["username"]

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        """
        SELECT username,image,caption
        FROM posts
        WHERE image NOT LIKE '%.webm'
        AND image NOT LIKE '%.mp4'
        ORDER BY id DESC
        """
    )
    posts = cur.fetchall()


    cur.execute(
        """
        SELECT username,video,caption
        FROM reels
        ORDER BY id DESC
        """
    )
    reels = cur.fetchall()


    cur.execute(
        """
        SELECT username,image
        FROM stories
        WHERE datetime(created_at) >= datetime('now','-1 day')
        ORDER BY id DESC
        """
    )
    all_stories = cur.fetchall()


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

    my_story_file = row[0] if row else None


    cur.execute(
        """
        SELECT username,image
        FROM stories
        WHERE username != ?
        AND datetime(created_at) >= datetime('now','-1 day')
        ORDER BY id DESC
        """,
        (current_user,)
    )

    friends_stories = cur.fetchall()


    conn.close()



    print("POSTS:", posts)
    print("REELS:", reels)
    print("POST COUNT:", len(posts))

    return render_template(
        "index.html",
        posts=posts,
        reels=reels,
        stories=all_stories,
        my_story=my_story_file,
        friends_stories=friends_stories
    )


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Yahan variable define karo
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')  # Ye missing tha!
        bio = request.form.get('bio', '') 
        
        # Ab ye query kaam karegi
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, name, bio, profile_pic, password) VALUES (?, ?, ?, ?, ?)", 
                    (username, name, bio, "default.jpg", password))
        conn.commit()
        conn.close()
        return redirect('/login')
        
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        
        cur.execute("SELECT name, bio, profile_pic FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        
        conn.close()
        
        if user:
            session['username'] = username
            session['name'] = user[0]  
            session['bio'] = user[1]  
            
            session['pfp'] = user[2] if user[2] else 'default.jpg' 
            
            return redirect(url_for('profile'))
        else:
            return "Invalid username or password"
            
    return render_template('login.html')



@app.route("/users")
def users():
    if "username" not in session:
        return redirect("/login")

    my_username = session["username"]
    
    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()
    
    # Change 'profile_pic' to the correct column name existing in your database
    cur.execute("SELECT username, YOUR_CORRECT_COLUMN_NAME FROM users WHERE username != ?", (my_username,))

    all_users = cur.fetchall()
    
    friends_data = []
    
    for user in all_users:
        friend_name = user[0]
        friend_pic = user[1] or "default.jpg" 
        
        cur.execute(
            """
            SELECT message, timestamp FROM messages 
            WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
            ORDER BY id DESC LIMIT 1
            """,
            (my_username, friend_name, friend_name, my_username)
        )
        last_msg_row = cur.fetchone()
        
        if last_msg_row:
            last_message = last_msg_row[0]
            msg_time = time_ago(last_msg_row[1]) 
        else:
            last_message = "Tap to chat"
            msg_time = ""
            
        friends_data.append({
            "username": friend_name,
            "profile_pic": friend_pic,
            "last_message": last_message,
            "time": msg_time
        })
        
    conn.close()
    return render_template("users.html", friends=friends_data)


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

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            with sqlite3.connect("snapz.db", timeout=20) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA journal_mode=WAL;")
                cur.execute(
                    "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                    (my_username, username, msg),
                )
                conn.commit()
        return redirect(f"/chat/{username}")

    with sqlite3.connect("snapz.db", timeout=20) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        
        cur.execute(
            "UPDATE messages SET is_seen = 1 WHERE sender = ? AND receiver = ?",
            (username, my_username),
        )
        conn.commit()

        cur.execute(
            """
            SELECT sender, message, timestamp, is_seen
            FROM messages
            WHERE
            (sender=? AND receiver=?)
            OR
            (sender=? AND receiver=?)
            ORDER BY id ASC
            """,
            (my_username, username, username, my_username),
        )
        raw_chats = cur.fetchall()

    chats = []
    for chat_item in raw_chats:
        chats.append({
            "sender": chat_item[0],
            "message": chat_item[1],
            "time": time_ago(chat_item[2]),
            "is_seen": chat_item[3]
        })

    return render_template("chat.html", chats=chats, chat_with=username)




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

    file.save("static/uploads/" + filename)

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
        cur.execute(
            "INSERT INTO stories(username, image, caption) VALUES(?,?,?)",
            (username, filename, caption)
        )

    else:
        cur.execute(
            "SELECT * FROM posts WHERE image=? AND caption=?",
            (filename, caption)
        )
        exist = cur.fetchone()

        if exist:
            conn.close()
            return redirect("/")

        cur.execute(
            "INSERT INTO posts(username, image, caption) VALUES(?,?,?)",
            (username, filename, caption)
        )

    conn.commit()
    conn.close()

    return redirect("/")





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

    conn.close()

    print("SENDING REELS TO HTML:", reels)

    return render_template(
        "reels.html",
        reels=reels
    )



@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/story", methods=["POST"])
def story():

    image=request.files["image"]

    filename=secure_filename(image.filename)

    image.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    )


    conn=sqlite3.connect("snapz.db")
    cur=conn.cursor()

    cur.execute(
    "INSERT INTO stories(username,image) VALUES(?,?)",
    (
        session["username"],
        filename
    )
    )

    conn.commit()
    conn.close()

    return redirect("/")




@app.route('/update_profile', methods=['POST'])
def update_profile():

    if 'username' not in session:
        return redirect(url_for('login'))

    new_name = request.form.get('name')
    new_username = request.form.get('username')
    new_bio = request.form.get('bio')

    old_username = session['username']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

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

    cropped_data = request.form.get('cropped_image')

    if cropped_data and cropped_data.startswith('data:image'):

        try:
            header, encoded = cropped_data.split(",", 1)
            image_data = base64.b64decode(encoded)

            folder_path = os.path.join('static', 'images')
            os.makedirs(folder_path, exist_ok=True)

            filename = f"{new_username}.jpg"
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "wb") as f:
                f.write(image_data)

            cur.execute(
                "UPDATE users SET profile_pic=? WHERE username=?",
                (filename, new_username)
            )

            session['pfp'] = filename

        except Exception as e:
            print("Image Save Error:", e)

    conn.commit()
    conn.close()

    session['name'] = new_name
    session['username'] = new_username
    session['bio'] = new_bio

    return redirect(url_for('profile'))







@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    # SQL query
    cur.execute("SELECT username, name, profile_pic FROM users WHERE username LIKE ? OR name LIKE ?", 
                ('%'+query+'%', '%'+query+'%'))
    results = cur.fetchall()
    conn.close()
    return jsonify(results)


def create_tables():
    conn = sqlite3.connect('database.db')
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


@app.route('/save_notification', methods=['POST']) # Check karo ki method POST hi hai
def save_notification():
    print("Notification route hit hua!") # Terminal mein ye print hona chahiye
    data = request.json
    print(data) # Ye check karega ki frontend se kya data aa raha hai
    

    data = request.json
    action = data.get('action', 'like') # Default 'like' hoga agar kuch nahi aaya toh

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO notifications (user_to, user_from, action, post_id) VALUES (?, ?, ?, ?)",
                (data['user_to'], session['username'], action, data.get('post_id')))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_notifications')
def get_notifications():
    current_user = session['username']
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT user_from, action FROM notifications WHERE user_to=? ORDER BY id DESC", (current_user,))
    rows = cur.fetchall()
    conn.close()
    
    notifications = [{'user_from': r[0], 'action': r[1]} for r in rows]
    return jsonify(notifications)





@app.route('/profile/<username>')
def profile_view(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone() # Yeh Zanna ka data hai
    conn.close()
    
    # Hum index.html hi bhej rahe hain, lekin saath mein 'user' ka data bhi
    return render_template('index.html', user=user, is_profile=True)

@app.route("/follow/<username>")
def follow_user(username):

    if "username" not in session:
        return redirect("/login")

    me = session["username"]

    if me != username:

        cur.execute("""
        SELECT * FROM followers
        WHERE follower_username=? AND followed_username=?
        """, (me, username))

        check = cur.fetchone()

        if not check:
            cur.execute("""
            INSERT INTO followers
            (follower_username, followed_username)
            VALUES (?,?)
            """, (me, username))

            conn.commit()

    return redirect("/")


@app.route("/unfollow/<username>")
def unfollow_user(username):

    me = session["username"]

    cur.execute("""
    DELETE FROM followers
    WHERE follower_username=? AND followed_username=?
    """, (me, username))

    conn.commit()

    return redirect("/")


@app.route("/edit_post", methods=["POST"])
def edit_post():

    data = request.get_json()

    conn = sqlite3.connect("snapz.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE posts SET caption=? WHERE id=?",
        (data["caption"], data["id"])
    )

    conn.commit()
    conn.close()

    return "ok"

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



init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
