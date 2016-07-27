from flask import Flask, render_template, request, url_for, redirect , session,flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os

# app config
app = Flask(__name__)
app.secret_key = " this is my secret key " # this key is used for encryption and decryption for all sessions
basedir= os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)


# Declare Global Varible that hold the login user name.
loginas = "None"
loggedUid = 0
error = ""


# Login required decorator.
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# Database Models
class Users (db.Model):
    Uid = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(50))
    Username = db.Column(db.String(50))
    Password = db.Column(db.String(50))
    Email = db.Column(db.String(50))
    ImgUrl = db.Column(db.String(30))

    def __init__(self, fullname, username, password, email, imgurl):
        self.FullName = fullname
        self.Username = username
        self.Password = password
        self.ImgUrl = imgurl
        self.Email = email
class Status(db.Model):
    Sid = db.Column(db.Integer, primary_key=True)
    Uid = db.Column(db.Integer)
    Status = db.Column(db.String(100))
    StatusImg= db.Column(db.String(100))

    def __init__(self, uid, status , statusimg):
        self.Uid = uid
        self.Status = status
        self.StatusImg = statusimg


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['formusername']
        userpass = request.form['formpassword']
        getdata = Users.query.filter(Users.Username == username or Users.Password == userpass ).first()
        if getdata != None:
            session['logged_in'] = True
            global loginas, loggedUid, error
            # Initialize global variable to Empty
            error=""
            # set Username and Userid in global Variable
            loginas = username
            loggedUid = getdata.Uid
            return redirect(url_for('home'))
        else:
             error = 'Invalid Login Id or Password'
    return render_template('login.html', errors=error)


# Register New User
@app.route('/register', methods=['GET', 'POST'])
def register():
    global error
    error = ""
    if request.method == 'POST':
        fullname = request.form['regFullName']
        regusername = request.form['regUserName']
        regpasswrod = request.form['regPassword']
        regEmail = request.form['regEmailId']
        addnewuser = Users(username=regusername, fullname=fullname, password=regpasswrod, imgurl="None", email=regEmail)
        chkuname = Users.query.filter(Users.Username == regusername).first()

        if chkuname is None:
            try:
                db.session.add(addnewuser)
                db.session.commit()
                error = "congratulations! User has been Created..! "
            except:
                db.session.rollback()
                error = " Opps Sorry! there's something went wrong!  "
            finally:
                db.session.close()
        else:
            error = "Sorry! user name is already in use"
    return render_template('login.html', errors=error)


# Route For Posting Status without image
@app.route('/poststatus',methods=["GET","POST"])
def poststatus():
    global error
    error = ""
    if request.method == "POST":
        txtstatus = request.form['txtStatus']
        if(txtstatus != ''):
            # Function Call for posting status.
            submitstatus(loggedUid, txtstatus, statusimg="None")
            error = "Status Posted Successfully..!"
        else:
            error="Sorry! please add some text in status box.! "
    return redirect(url_for('home', errors=error))


# this function Submit status in the status table
def submitstatus(userid, description, statusimg):
        addstatus = Status(uid=userid, status=description, statusimg=statusimg)
        db.session.add(addstatus)
        db.session.commit()


# Route For Posting Status with image
@app.route('/uploadimage',methods=["GET","POST"])
def upload():
    global error
    error=""
    target = os.path.join(basedir, 'static/statusimages/')
    file = request.files['file']
    filename = file.filename
    destination = '/'.join([target, filename])
    try:
        caption = request.form["txtCaption"]
        # Check User have selected a file and also provide caption
        if filename != '' and caption != '':
            file.save(destination)
            submitstatus(loggedUid, caption, filename)
            error = "Status Posted Successfully! "
        else:
            error = "Status Posted Failed..! there is no file or caption was found..!"
    except Exception as e:
        error = str(e)
    return redirect(url_for('home', errors=error))


@app.route('/home')
@login_required
def home():
    # Get Status from table Status.
    getstatus = Status.query.filter(Status.Uid == loggedUid).all()
    return render_template('home.html', loginas=loginas, lststatus=getstatus, errors=error)


@app.route('/logout',methods=["GET","POST"])
def logout():
    global error
    error = ""
    # Clear Logged_in session
    session.pop('logged_in', None)
    return redirect(url_for('login', errors=error))


if __name__ == "__main__":
    app.debug = True
    app.run()
