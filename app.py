import sqlite3
from flask import Flask
from flask import request
from flask import jsonify
import time
from flask import Response

BEARER_TOKEN = 'token123'

def is_auth(r):
    token = r.headers.get('Authorization')
    if not token:
        return "No Authorization param" 
    
    if not token.startswith("Bearer "):
        return "Bad scheme"
    
    token = token.split(" ", 1)[1]
    if token != BEARER_TOKEN:
        return "Bad token"
    
    return True
    


connection = sqlite3.connect("cards.db")
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cards (
    id INTEGER PRIMARY KEY,
    title STRING NOT NULL,
    description STRING NOT NULL,
    responsible STRING NOT NULL,
    timestamp REAL NOT NULL        
    )     
''')

connection.commit()
connection.close()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "hi"

@app.route('/task/save', methods=['POST'])
def save_card():

    user = is_auth(request)
    if user != True:
        return Response(user, status=400)
    
    ts = time.time()
    title = request.json.get('title')
    description = request.json.get('description')
    responsible = request.json.get('responsible')
    connection = sqlite3.connect('cards.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Cards (title, description, responsible, timestamp) VALUES (?, ?, ?, ?)', (title, description, responsible, ts))
    connection.commit()
    connection.close()  
    return Response("Data added", 200)
    

@app.route('/task/<username>')
def card_by_name(username):
    user = is_auth(request)
    if user != True:
        return Response(user, status=400)
    connection = sqlite3.connect('cards.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Cards WHERE responsible = ?', (username,))
    data = cursor.fetchall()
    if len(data) == 0:
        return Response("No such user", status=400)
    data.sort(key=lambda x: x[-1], reverse=True)
    print(data)
    return jsonify(data)
    

@app.route('/task')
def allcards():
    user = is_auth(request)
    if user != True:
        return Response(user, status=400)
    connection = sqlite3.connect('cards.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Cards')
    data = cursor.fetchall()
    data.sort(key=lambda x: x[-1], reverse=True)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)