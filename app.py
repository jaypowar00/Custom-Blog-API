from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2 , json , pprint , requests

app = Flask(__name__)

#dev if you are doing developement locally , it will set debug = true and you will be working with local database
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@localhost/<database>'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://<username>:<password>@<port>/<database>'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'posts'
    _id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())

    def __init__(self,username,email):
        self.username = username
        self.email = email

def get_blog_posts():
    try:
        conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        try:
            cur = conn.cursor()
            cur.execute("SELECT json_agg(<TABLE_NAME>) FROM <TABLE_NAME>")
            cur.execute("SELECT to_jsonb(array_agg(<TABLE_NAME>)) FROM <TABLE_NAME>")
            result = cur.fetchall()[0][0]
            conn.commit()
            cur.close()
            conn.close()
            return result
        except:
            return False
    except:
        return False


@app.route('/')
@app.route('/blog')
def add():
    return "<h1>this is blog page</h1><br><h3>go to /blog/posts</h3>"

@app.route('/blog/posts',methods=["GET"])
def return_blog_posts():
    result = get_blog_posts()
    if result != False:
        #MAKING THE RECEIVED DATA INTO VALID JSON FORMAT
        json_result = {"posts":result}
        newresult = json.dumps(json_result)
        return newresult,200
    else:
        #ON ANY ERROR FROM DATABASE, RETURNING 'some error' msg with STATUS_CODE as 506
        return 'some error',506

if __name__ == "__main__":
    db.create_all()
    app.run()
