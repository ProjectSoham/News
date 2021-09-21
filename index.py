from flask import Flask 
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import session

from flask_pymongo import PyMongo

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
import datetime
from werkzeug.utils import secure_filename

import random
 

app = Flask(__name__) 

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','webp'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/Newspaper-Website")

mongodb_client = PyMongo(app, uri="mongodb+srv://soham123:soham123@cluster0.scfq5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = mongodb_client.db
 
@app.route('/')  
def index():  
    return render_template('index.html')


@app.route('/userreg', methods=["GET", "POST"])  
def userregpage():
    if request.method == 'GET':
        return render_template('userreg.html')
    else:
        x=datetime.datetime.now()
        x = ''+str(x)
        #print(x)
        userobj = db.usercollection.find_one(
        {'useremail': request.form['email']})
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('userreg.html',msg=' User Already Registered')
        else:
            uname = request.form['user']
        
            db.usercollection.insert_one(
            {'username': uname,
            'useremail': request.form['email'],
            'usermobile': request.form['mobile'],
            'userpass': request.form['pass'],
            'userconpass': request.form['conpass'],
            'regdate':x
            })
            return render_template('userreg.html',msg='Registration Successfully Completed')
        

@app.route('/userlogin', methods=["GET", "POST"])  
def userloginpage(): 
    if request.method == 'GET': 
        return render_template('userlogin.html')
    else:
        user = db.usercollection.find_one(
        {'useremail': request.form['email'],
         'userpass': request.form['pass'],
        })
        print(user)
        
        if user:
            session['uemail']= user['useremail']
            session['uname'] = user['username']
            session['usertype']= 'USER'
            #print(user['username'])
            return redirect(url_for('userafterlogin'))
        else:
            return render_template('userlogin.html', errormsg = "INVALID UID OR PASSWORD")


@app.route('/about')  
def aboutpage():  
    return render_template('about.html')

@app.route('/adminlogin', methods=['GET','POST'])  
def adminloginpage(): 
    if request.method == 'GET':
        return render_template('adminlogin.html')
    else:      
        adminuid = request.form['adminuserid']
        adminpass = request.form['adminpassword']

        if(adminuid == 'admin@gmail.com' and adminpass == 'admin'):
            session['adminemail']='admin@gmail.com'
            session['adminname']='admin'
            session['usertype']='ADMIN'
            return redirect(url_for('adminafterlogin'))
        else:
            return render_template('adminlogin.html', msg = 'INVALID UID OR PASS')

@app.route('/adminhome')  
def adminafterlogin(): 
    adminemail=session['adminemail']
    userobj = db.uploadcollection.find({})
    print(userobj)
    return render_template('adminafterlogin.html',userdata=userobj)

@app.route('/viewall')  
def viewall(): 
    userobj = db.usercollection.find({})
    print(userobj)
    return render_template('viewuser.html', userdata = userobj)

@app.route('/adminaddnews', methods = ['GET','POST']) 
def adminaddnewspage():  
    if request.method == 'GET': 
        return render_template('adminaddnews.html')
    else:
        x=datetime.datetime.now()
        x = ''+str(x)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('upload_image filename: ' +filename)
            flash('Image successfully uploaded')
            path = 'static/uploads/' +filename

            adminemail=session['adminemail']
            n = str(random.randint(0,9999))

            db.uploadcollection.insert_one(
                {
                    'username':adminemail,
                    'usernews':n,
                    'usercata': request.form['cata'],
                    'userdes':request.form['des'],
                    'userdob':x,
                    'image':path
                }
            )
            return render_template("adminaddnews.html")  
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif,webp')
            return redirect(request.url)

@app.route('/adminsearchuser', methods=['GET','POST'])  
def adminsearchuser(): 
    if request.method == 'GET':
        return render_template('adminsearchuser.html')
    else:      
        userobj = db.usercollection.find_one(
        {'useremail': request.form['email']})
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('adminsearchuser.html', userdata = userobj, show_results=1)
        else:
            return render_template('adminsearchuser.html', msg = "INVALID EMAIL ID")  

@app.route('/admindeleteuser', methods=['POST'])  
def admindeleteuser():
    print(request.form['email']) 
    responsefrommongodb = db.usercollection.find_one_and_delete({'useremail': request.form['email']})
    print(responsefrommongodb)
    return redirect(url_for('adminsearchuser'))

@app.route('/adminsearchnews', methods=['GET','POST'])  
def adminsearchnewspage(): 
    if request.method == 'GET':
        return render_template('adminsearchnews.html')
    else:      
        userobj = db.uploadcollection.find(
        {
          'usercata':request.form['cata']
        })
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('adminsearchnews.html', userdata = userobj, show_results=1)
        else:
            return render_template('adminsearchnews.html',msg= "No News Found")

@app.route('/admindeletenews', methods=['GET','POST'])  
def admindeletenews(): 
    if request.method == 'GET':
        return render_template('admindeletenews.html')
    else:      
        responsefrommongodb = db.uploadcollection.find_one_and_delete(
        {'usernews':request.form['news'],
        })
        print(responsefrommongodb)
        if responsefrommongodb is not None:
            return render_template('admindeletenews.html', msg = "SUCCESSFULLY DETELED")
        return render_template('admindeletenews.html', msg = "INVALID News ID")



@app.route('/userafterlogin')
def userafterlogin():
    uemail=session['uemail']
    userobj = db.uploadcollection.find({})
    print(userobj)
    return render_template('userafterlogin.html',userdata=userobj,uname=session['uname'])

@app.route('/viewnews')
def viewnewspage():
    userobj = db.uploadcollection.find({'username': session['uemail']})
    print(userobj)
    return render_template('viewnews.html',userdata=userobj,uname=session['uname'])



@app.route('/addnews', methods = ['GET','POST']) 
def addnewspage():  
    if request.method == 'GET': 
        return render_template('addnews.html',uname=session['uname'])
    else:
        x=datetime.datetime.now()
        x = ''+str(x)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('upload_image filename: ' +filename)
            flash('Image successfully uploaded')
            path = 'static/uploads/' +filename

            uemail=session['uemail'] #how to retrive value from session
            n = str(random.randint(0,9999))

            db.uploadcollection.insert_one(
                {
                    'username':uemail,
                    'usernews': n,
                    'usercata': request.form['cata'],
                    'userdes':request.form['des'],
                    'userdob':x,
                    'image':path
                }
            )  
            return render_template("addnews.html",uname=session['uname'])  
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif,webp')
            return redirect(request.url)


@app.route('/searchnews', methods=['GET','POST'])  
def searchnewspage(): 
    if request.method == 'GET':
        return render_template('searchnews.html',uname=session['uname'])
    else:      
        userobj = db.uploadcollection.find(
        {'username': session['uemail'],
          'usercata':request.form['cata']
        })
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('searchnews.html', userdata = userobj, show_results=1,uname=session['uname'])
        else:
            return render_template('searchnews.html',msg= "No News Found",uname=session['uname'])
            

@app.route('/deletenews', methods=['GET','POST'])  
def deletenews(): 
    if request.method == 'GET':
        return render_template('deletenews.html',uname=session['uname'])
    else:      
        responsefrommongodb = db.uploadcollection.find_one_and_delete(
        {'usernews':session['uemail'],
        'usercata':request.form['cata']
        })
        print(responsefrommongodb)
        if responsefrommongodb is not None:
            return render_template('deletenews.html', msg = "SUCCESSFULLY DETELED",uname=session['uname'])
        return render_template('deletenews.html', msg = "INVALID News ID",uname=session['uname'])

@app.route('/delete1', methods=['POST'])  
def deletenews1():
    print(request.form['news']) 
    responsefrommongodb = db.uploadcollection.find_one_and_delete({'usernews': request.form['news']})
    print(responsefrommongodb)
    return redirect(url_for('searchnewspage'))

@app.route('/delete2', methods=['POST'])  
def deletenews2():
    print(request.form['news']) 
    responsefrommongodb = db.uploadcollection.find_one_and_delete({'usernews': request.form['news']})
    print(responsefrommongodb)
    return redirect(url_for('adminsearchnewspage'))

@app.route('/viewuserprofile')  
def viewuserprofile(): 
    uemail = session['uemail']      
    userobj = db.usercollection.find_one({'useremail': uemail})
    print(userobj)
    return render_template('viewuserprofile.html', userdata = userobj,uname=session['uname'])

@app.route('/updateuserprofile', methods=["GET", "POST"])  
def updateuserprofile():
    if request.method == 'GET':
        uemail = session['uemail']      
        userobj = db.usercollection.find_one({'useremail': uemail})
        return render_template('updateuserprofile.html',userdata = userobj,uname=session['uname'])
    else:
        db.usercollection.update_one( {'useremail': session['uemail'] },
        { "$set": { 'usermobile': request.form['mobile'],
                    'userpass': request.form['pass']
                    
                  } 
        })
        return redirect(url_for('viewuserprofile'))

@app.route('/logout')  
def logout():  
    if 'usertype' in session:
        utype = session['usertype']
        if utype == 'ADMIN':
            session.pop('usertype',None)
            session.pop('adminemail',None)
            session.pop('adminname',None)
        else: 
            session.pop('usertype',None)
            session.pop('uemail',None)
            session.pop('uname',None)
        return redirect(url_for('index'));    
    else:  
        return '<p>user already logged out</p>' 


@app.route('/contact', methods=["GET", "POST"])  
def contactpage():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        x=datetime.datetime.now()
        x = ''+str(x)

        uname = request.form['user']
       
        db.contactcollection.insert_one(
        {'username': uname,
        'useremail': request.form['email'],
        'usermessage': request.form['message'],
        'messagedate':x
        })
        return render_template('contact.html',msg = 'Your Response Successfully Saved')

@app.route('/adminviewcontact')
def adminviewcontact():
    userobj = db.contactcollection.find({})
    print(userobj)
    return render_template('adminviewcontact.html',userdata=userobj)

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/homesearchnews', methods=['GET','POST'])  
def homesearchnewspage(): 
    if request.method == 'GET':
        return render_template('homesearchnews.html')
    else:      
        userobj = db.uploadcollection.find(
        {
          'usercata':request.form['cata']
        })
        print(userobj)
        
        if userobj:
            #print(userobj['username'])
            return render_template('homesearchnews.html', userdata = userobj, show_results=1)
        else:
            return render_template('homesearchnews.html')


@app.route('/change', methods=["GET", "POST"])  
def change():
    if request.method == 'GET':
        return render_template('change.html')
    else:
        db.usercollection.update_one( {'useremail': request.form['email']},
        { "$set": { 'userpass': request.form['pass'] } 
        })
        return redirect(url_for('userloginpage'))
        


if __name__ == '__main__':  
   app.run(debug = True) 
