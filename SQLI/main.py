import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g, redirect, url_for
from model import get_model_tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy
import pandas
from tensorflow.keras import backend as K
from keras.models import load_model
import tensorflow as tf
global graph
graph = tf.get_default_graph()

app = Flask(__name__)
app.database = "sample.db"

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/login_temp',methods=['GET','POST'])
def login_temp():
    return render_template('login_temp.html')

@app.route('/courses',methods=['GET','POST'])
def courses():
    return render_template('courses.html')

@app.route('/restock')
def restock():
    return render_template('restock.html')


#API routes

##juice' UNION SELECT username,password from employees;--
def detector(uname):
    K.clear_session()
    tokenizer1=get_model_tokenizer()
    token=tokenizer1.texts_to_sequences([uname.lower()])
    pad=pad_sequences(token, maxlen=150,padding="post")
    print(pad)
    with graph.as_default():
        model=load_model('model.h5')
        probab=model.predict_proba(pad)[0][0]
    K.clear_session()
    return probab


@app.route('/api/v1.0/storeLoginAPI/', methods=['POST'])
def loginAPI():
    if request.method == 'POST':
        uname,pword = (request.json['username'],request.json['password'])


        # DNN CAll
        probab = detector(uname)
        if(probab >= 0.91):
            result = {'status': 'SQL Injection Detected . Your IP will be Blocked !'}
            return jsonify(result)


        print(uname,pword)
        g.db = connect_db()
        cur = g.db.execute("SELECT * FROM employees WHERE username = '%s' AND password = '%s'" %(uname, hash_pass(pword)))
        if cur.fetchone():
            result = {'status': 'success'}
        else:
            result = {'status': 'fail'}

        g.db.close()
        return jsonify(result)


@app.route('/api/v1.0/storeAPI', methods=['GET', 'POST'])
def storeapi():
    if request.method == 'GET':
        g.db = connect_db()
        curs = g.db.execute("SELECT * FROM courses")
        cur2 = g.db.execute("SELECT * FROM employees")
        items = [{'items':[dict(name=row[0], seats=row[1], code=row[2]) for row in curs.fetchall()]}]
        empls = [{'employees':[dict(username=row[0], password=row[1]) for row in cur2.fetchall()]}]
        g.db.close()
        return jsonify(items+empls)

    elif request.method == 'POST':
        g.db = connect_db()
        name,seats,code = (request.json['name'],request.json['seats'],request.json['code'])
        curs = g.db.execute("""INSERT INTO courses(name, seats, code) VALUES(?,?,?)""", (name, seats, code))
        g.db.commit()
        g.db.close()
        return jsonify({'status':'OK','name':name,'seats':seats,'code':code})



@app.route('/api/v1.0/storeAPI/<item>', methods=['GET'])
def searchAPI(item):
    probab = detector(item)
    print(probab)
    if(probab >= 0.91):
        results = [dict(name="SQLI detected", seats="SQLI detected", code="SQLI detected") ]
        return jsonify(results)


    g.db = connect_db()
    curs = g.db.execute("SELECT * FROM courses WHERE name = '%s'" %item)
    results = [dict(name=row[0], seats=row[1], code=row[2]) for row in curs.fetchall()]

    print(results)
    g.db.close()
    print(jsonify(results))
    return jsonify(results)


def connect_db():
    return sqlite3.connect(app.database)

# Create password hashes
def hash_pass(passw):
	m = hashlib.md5()
	m.update(passw.encode('utf-8'))
	return m.hexdigest()

if __name__ == "__main__":

    #create database if it doesn't exist yet
    if not os.path.exists(app.database):
        with sqlite3.connect(app.database) as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE courses(name TEXT, seats TEXT, code TEXT)""")
            c.execute("""CREATE TABLE employees(username TEXT, password TEXT)""")
            c.execute('INSERT INTO courses VALUES("Software Engineering", "40", "CSE3001")')
            c.execute('INSERT INTO courses VALUES("Internet and Web Programming", "40", "CSE3002")')
            c.execute('INSERT INTO courses VALUES("Database Management Systems", "60", "CSE2001")')
            c.execute('INSERT INTO employees VALUES("Nishant Pandey", "{}")'.format(hash_pass("123")))
            c.execute('INSERT INTO employees VALUES("PradyumnBeriwal", "{}")'.format(hash_pass("456")))
            c.execute('INSERT INTO employees VALUES("Ramsai Vajrapu", "{}")'.format(hash_pass("pass123")))
            connection.commit()
            connection.close()

    app.debug = True
    app.run(host='0.0.0.0') # runs on machine ip address to make it visible on netowrk
