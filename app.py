'''
This is a custome API for Blogsites (still in development)
(Don't rush and try to run it! observe the code and fillin your credentials for SQL database; I've tested this with only Postgresql)
'''
from flask import Flask, request, redirect, url_for, make_response, session ,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import psycopg2
from psycopg2 import sql
import datetime
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from functools import wraps
import jwt

cookie_duration = timedelta(days=3)
app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app,expose_headers=['Access-Control-Allow-Origin'],supports_credentials=True)  #Required if working with cross-domain/cross-site requests! [Important]
app.permanent_session_lifetime = timedelta(days=3)

app.config['SECRET_KEY']='YourVeryOwnVeryLongTopSecretKey'


# change this to 'dev' if u wish to test the code with your local database and running the app on local machine other wise make it 'prod'...
ENV = 'prod'
if ENV == 'dev':
    '''for local databse connection(if testing and running on local machine instead of server)'''
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@localhost/<database>'
else:
    '''for online databse connection'''
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@localhost/<database>'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader

class Posts(db.Model):
    '''This is a class for "posts" table'''
    __tablename__ = 'posts'
    _id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text())
    author = db.Column(db.Text())
    tags = db.Column(db.ARRAY(db.Text()))
    content = db.Column(db.Text())
    description = db.Column(db.Text())
    thumbnail = db.Column(db.Text())
    created = db.Column(db.DateTime(timezone=True),server_default=func.now())

class Author(db.Model):
    '''This is a class for "authors" table'''
    __tablename__ = 'authors'
    auth_id = db.Column(db.Integer,primary_key=True)
    public_id = db.Column(db.Integer,unique=True)
    name = db.Column(db.Text())
    rname = db.Column(db.Text())
    password = db.Column(db.Text())
    admin = db.Column(db.Boolean)
    bio = db.Column(db.Text())
    mail = db.Column(db.Text())
    social = db.Column(db.ARRAY(db.Text()))
    
    def __init__(self, name, mail, password, rname, bio,public_id,social,admin):
        self.name = name
        self.mail = mail
        self.password = password
        self.rname = rname
        self.bio = bio
        self.public_id = public_id
        self.social = social
        self.admin = admin

    def get_id(self):
        return self.auth_id

def get_searched_post(orderby='created' ,order='desc',author=None,tag=None,searchString=False):
    '''actual implementation of getting-fetching all blogs/posts from posts table filtered by search items with other filters'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        if author:
            if tag:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}' AND tags @> '{{"{tag}"}}' AND {searchString})) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
            else:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}' AND {searchString})) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
        elif tag:
            cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE tags @> '{{"{tag}"}}' AND {searchString})) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
        else :
            cur.execute(f"SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created)WHERE {searchString})) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;")
        result = cur.fetchall()[0][0]
        result = list(filter(None, result))
        conn.commit()
        cur.close()
        conn.close()
        print("search result:")
        print(result)
        return result if len(result)>0 else (500,{'Server Error':'posts not found'})
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}
    except psycopg2.errors.UndefinedColumn:
        return 500,{'Server Error':'Invalid Orderby'}
    except psycopg2.errors.SyntaxError:
        return 500,{'Server Error':'Invalid Search String'}
    except psycopg2.errors.AmbiguousFunction:
        return 500,{'Server Error':'Invalid Search String'}
def get_blog_posts(orderby='created' ,order='desc',author=None,tag=None):
    '''actual implementation of getting-fetching all blogs/posts from posts table'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        if author:
            if tag:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}' AND tags @> '{{"{tag}"}}')) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
            else:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}')) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
        elif tag:
            cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE tags @> '{{"{tag}"}}')) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;''')
        else :
            cur.execute(f"SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created))) {'ORDER BY '+orderby+' '+order if orderby and order else False or 'ORDER BY '+orderby+' desc' if orderby else False or 'ORDER BY created '+order if order else False or 'ORDER BY created desc' }) FROM posts;")
        result = cur.fetchall()[0][0]
        result = list(filter(None, result))
        conn.commit()
        cur.close()
        conn.close()
        print("get posts:")
        print(result)
        return result
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}
    except psycopg2.errors.UndefinedColumn:
        return 500,{'Server Error':'Invalid Orderby'}

def get_tags_from_db():
    '''actual implementation of getting-fetching all tags used in posts table'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        cur.execute("SELECT json_agg(tags) FROM posts;")
        result = cur.fetchall()[0][0]
        new=set()
        for i in result:
            if type(i)==type(list()):
                for ii in i:
                    new.add(ii)
        result = list(new)
        conn.commit()
        cur.close()
        conn.close()
        print("get tags:")
        print(result)
        return result
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}

def getadmindata(name):
    print('name->'+name)
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        cur.execute(f"SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT auth_id,name,rname,bio,mail,social) AS ColumnName (auth_id,name,rname,bio,mail,social)))) FROM authors where name = '{name}' ;")
        result = cur.fetchall()[0][0][0]
        print(result)
        new = dict()
        for d,v in result.items():
            if not type(v)==type(list()):
                new[d] = v
            else:
                new_list = list()
                for i in range(len(v[0])):
                    new_list.append(dict({'name':v[0][i],'url':v[1][i]}))
                new[d] = new_list
        result = new
        conn.commit()
        cur.close()
        conn.close()
        print("get admin data")
        print(result)
        return result
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}
    except TypeError:
        return False

def fetch_post_by_id(id):
    '''actual implementation of getting-fetching post from posts table of gievn id'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        cur.execute(f"SELECT json_agg(posts) FROM posts where _id = {id}")
        result = cur.fetchall()[0][0][0]
        print('get post by id->'+id)
        print(result)
        conn.commit()
        cur.close()
        conn.close()
        return result
    except TypeError as error:
        return 500,{'Server Error':f'{error}'}

def insert_post_to_database(title, content, description, tags, thumbnail, author):
    '''actual implementation of insertion of data into posts table'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        try:
            cur = conn.cursor()
            query = sql.SQL('''insert into posts (title, content, description, tags, thumbnail, author) values (%s,%s,%s,%s,%s,%s)''')
            cur.execute(query, (title, content, description, tags, thumbnail, author))
            conn.commit()
            cur.close()
            conn.close()
            print('done uploading post')
            return True
        except:
            print('failed uploading post')
            return False
    except:
        print('failed connecting to db for create')
        return False

def update_post_by_id(id,title, content, description, tags, thumbnail, author):
    '''actual implementation of updation of post'''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        try:
            cur = conn.cursor()
            query = sql.SQL('''UPDATE posts SET title=%s, content=%s, description=%s, tags=%s, thumbnail=%s, author=%s WHERE _id=%s''')
            cur.execute(query, (title, content, description, tags, thumbnail, author,id))
            conn.commit()
            cur.close()
            conn.close()
            print('done updating post')
            return True
        except:
            print('failed updating post')
            return False
    except:
        print('failed to connect for update')
        return False

def postadmindata(name,rname,bio,password,admin,mail,social):
    '''
    This will upload author information into authors table...
    '''
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        try:
            cur = conn.cursor()
            query = sql.SQL('''insert into authors (name,rname,bio,password,admin,mail,social) values (%s,%s,%s,%s,%s,%s,%s)''')
            cur.execute(query, (name,rname,bio,password,admin,mail,social))
            conn.commit()
            cur.close()
            conn.close()
            print('done posting admin')
            return True
        except:
            print('failed posting admin')
            return False
    except:
        print('failed to connect')
        return False

def delete_all():
    if ENV == 'dev':
        #local DB config.
        conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
    else:
        #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
    cur = conn.cursor()
    cur.execute('select count(*) from posts')
    n = cur.fetchall()[0][0]
    if n != 0:
        cur.execute("DELETE FROM posts RETURNING *")
        r = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        print('deleted all posts')
        if len(r)==0:
            return make_response({"response":"No posts to delete!"})
        return make_response({"response":"All Posts have been deleted!"})
    else:
        cur.close()
        conn.close()
        print('no posts to delete(for delete all)')
        return make_response({'response':'No posts to delete'})

def delete_by(id):
    if ENV == 'dev':
        #local DB config.
        conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
    else:
        #non-local DB config.(online)
        conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
    cur = conn.cursor()
    cur.execute('select count(*) from posts')
    n = cur.fetchall()[0][0]
    if n != 0:
        cur.execute(f"DELETE FROM posts WHERE _id={id} RETURNING *")
        r=cur.fetchall()
        print('deletebyid')
        conn.commit()
        cur.close()
        conn.close()
        print('post '+str(id)+' deleted')
        if len(r)==0:
            return make_response({"response":"No such post to delete!"})
        return make_response({"response":"The Post have been deleted!"})
    else:
        cur.close()
        conn.close()
        print('no post to delete(for delete post)')
        return make_response({'response':'No posts to delete'})

def check_pass_hash(username,password):
    try:
        if ENV == 'dev':
            #local DB config.
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="localhost" ,port = "5432")
        else:
            #non-local DB config.(online)
            conn = psycopg2.connect(database = "<database_name>", user = "<user>" , password = "<password>", host ="<host/server>" ,port = "5432")
        cur = conn.cursor()
        cur.execute("SELECT json_agg(authors) FROM authors")
        result = cur.fetchall()[0][0]
        conn.commit()
        cur.close()
        conn.close()
        for x in result:
            if x['name']==username and check_password_hash(x['password'],password):
                return x['auth_id']
        return False
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}

#use this wrapper for the routes you want the jwt authentication(valid) as must!
def token_required(func):
    @wraps(func)
    def decorated(*args,**kwargs):
        token = None

        if 'token' in request.args:
            token=request.args['token']
        if not token:
            return jsonify({'response':'token missing'})
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            current_user= Author.query.filter_by(public_id=data['public_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'response':'token has expired!','success':False})
        except jwt.InvalidSignatureError:
            return jsonify({'response':'token is Invalid!','success':False})
        except jwt.DecodeError:
            return jsonify({'response':'token is Invalid!','success':False})
        return func(current_user,*args,**kwargs)
    return decorated

#use this wrapper for the routes you want the jwt authentication as optional !
def token_optional(func):
    '''
    for optional jwt authentication
    on authentication failure it returns {msg='<fail reason>',token=False,admin=False,and all the *args & **kwargs recieved by original wrapped route!}
    success returns {msg='<authors_name>',token=True,admin=<Bool_value(if that author is set admin or not)>,*args,**kwargs}
    '''
    @wraps(func)
    def decorated(*args,**kwargs):
        token = None

        if 'token' in request.args:
            token=request.args['token']
        if not token:
            return func(msg='token is missing',token=False,admin=False,*args,**kwargs)
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            author= Author.query.filter_by(public_id=data['public_id'])
            if author:
                print(author.first().name)
        except jwt.ExpiredSignatureError:
            return func(msg='token has Expired!',token=False,admin=False,*args,**kwargs)
        except jwt.InvalidSignatureError:
            return func(msg='token is Invalid!',token=False,admin=False,*args,**kwargs)
        except jwt.DecodeError:
            return func(msg='token is Invalid!',token=False,admin=False,*args,**kwargs)
        return func(msg=author.first().name if current_user else '',token=True,admin=author.first().admin,*args,**kwargs)
    return decorated


@app.route('''/''')
@app.route('''/blog''')
@token_optional
def blog_page(msg,token,admin):
    '''tempo blog page route'''
    db.create_all()
    in_query = request.args
    if 'get' in in_query:
        if in_query['get']=='tags':
            result = get_tags_from_db()
            resp = make_response({'success':True,f'tags':result})
            resp.mimetype = 'application/json'
            return resp
    admin = '(admin-login not found)'
    header = ''
    try:
            header = request.headers['<your_custom_auth_header_name>']
    finally:
        if token or current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
            admin='(admin-login found)'
        return f"<div style='text-align:center;font-size:calc(100px - 6vw);'><h1>this is blog page</h1><br>{admin}<br><h3><br><br>see posts: <a href='/blog/posts'>/blog/posts</a><br>create a post: <a href='/blog/create'>/blog/create</a><br>admin login: <a href='/blog/admin'>/blog/admin</a></h3><div>"

@app.route('''/blog/posts''', methods=["GET"])
@token_optional
def return_blog_posts(msg,token,admin):
    '''displaying all posts data from posts table as per request (queries acceptable)'''
    db.create_all()
    if token:
        if not admin:
            t_author=msg
    in_query = request.args
    if in_query:
        searchString=''
        if 'search' in in_query:
            '''
            if searching is to be done in db for articles it will be done using 'search' query followed by SearchString
            the search will be case incase sensitive!
            '''
            searchData = in_query['search']
            searchItems = searchData.split(' ')
            contentSearch = ''
            descriptionSearch = ''
            titleSearch = ''
            for i in searchItems:
                if len(i)>0:
                    if i==searchItems[0]:
                        contentSearch += f""" LOWER(content) LIKE '%{i.lower()}%'"""
                        descriptionSearch += f""" or LOWER(description) LIKE '%{i.lower()}%'"""
                        titleSearch += f""" or LOWER(title) LIKE '%{i.lower()}%'"""
                    else:
                        contentSearch += f""" or LOWER(content) LIKE '%{i.lower()}%'""" if len(contentSearch)!=0 else f""" LOWER(content) LIKE '%{i.lower()}%'"""
                        descriptionSearch += f""" or LOWER(description) LIKE '%{i.lower()}%'"""
                        titleSearch += f""" or LOWER(title) LIKE '%{i.lower()}%'"""
            searchString = contentSearch+descriptionSearch+titleSearch
        if 'orderby' in in_query or 'order' in in_query or 'author' in in_query or 'tag' in in_query or 'search' in in_query or token:

            if 'orderby' in in_query and 'order' in in_query and 'author' in in_query and 'tag' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'author' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'tag' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(orderby=in_query["orderby"],order=in_query["order"],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'tag' in in_query and 'author' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(order=in_query["order"],author=in_query['author'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query and 'author' in in_query and 'search' in in_query:
                result = get_searched_post(orderby=in_query["orderby"],author=in_query['author'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
            elif 'author' in in_query and 'tag' in in_query and 'search' in in_query:
                result = get_searched_post(author=in_query['author'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
            elif 'order' in in_query and 'tag' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(order=in_query['order'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query and 'search' in in_query:
                result = get_searched_post(order=in_query['order'],tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
            elif 'order' in in_query and 'author' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(order=in_query['order'],author=in_query['author'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'author' in in_query and 'search' in in_query:
                result = get_searched_post(orderby=in_query['orderby'],author=in_query['author'],searchString=searchString if len(searchString)>0 else False)
            elif 'author' in in_query and 'search' in in_query:
                result = get_searched_post(author=in_query['author'],searchString=searchString if len(searchString)>0 else False)
            elif 'tag' in in_query and 'search' in in_query:
                result = get_searched_post(tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
            elif 'orderby' in in_query and 'order' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(orderby=in_query["orderby"],order=in_query["order"],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'search' in in_query:
                result = get_searched_post(orderby=in_query["orderby"],searchString=searchString if len(searchString)>0 else False)
            elif 'order' in in_query and 'search' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_searched_post(order=in_query["order"],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameter'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'author' in in_query and 'search' in in_query:
                if in_query['author'].lower()=='aeyjey' or in_query['author'].lower() =='redranger' or in_query['author'].lower() == 'whoknows' :
                    result = get_searched_post(author=in_query['author'],searchString=searchString if len(searchString)>0 else False)
                else:
                    resp = make_response({'success':False,'Server Error':'Author does not exists.'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'tag' in in_query and 'search' in in_query:
                result = get_searched_post(tag=in_query['tag'],searchString=searchString if len(searchString)>0 else False)
            elif 'search' in in_query:
                result = get_searched_post(searchString=searchString if len(searchString)>0 else False)
            elif 'orderby' in in_query and 'order' in in_query and 'author' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'tag' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query["order"],author=in_query['author'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query and 'author' in in_query:
                result = get_blog_posts(orderby=in_query["orderby"],author=in_query['author'],tag=in_query['tag'])
            elif 'author' in in_query and 'tag' in in_query:
                result = get_blog_posts(author=in_query['author'],tag=in_query['tag'])
            elif 'order' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query['order'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query:
                result = get_blog_posts(order=in_query['order'],tag=in_query['tag'])
            elif 'order' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query['order'],author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'author' in in_query:
                result = get_blog_posts(orderby=in_query['orderby'],author=in_query['author'])
            elif 'author' in in_query :
                result = get_blog_posts(author=in_query['author'])
            elif 'tag' in in_query :
                result = get_blog_posts(tag=in_query['tag'])
            elif 'orderby' in in_query and 'order' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    if token:
                        if t_author:
                            print('logged author ('+t_author+') requested for his posts!')
                            result = get_blog_posts(order=in_query['order'],orderby=in_query['orderby'],author=t_author)
                        else:
                            print('logged Superuser requested for all posts!')
                            result = get_blog_posts(order=in_query['order'],orderby=in_query['orderby'])
                    else:
                        result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],)
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query:
                if token:
                    if t_author:
                        print('logged author ('+t_author+') requested for his posts!')
                        result = get_blog_posts(orderby=in_query['orderby'],author=t_author)
                    else:
                        print('logged Superuser requested for all posts!')
                        result = get_blog_posts(orderby=in_query['orderby'])
                else:
                    result = get_blog_posts(orderby=in_query["orderby"])
            elif 'order' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    if token:
                        if t_author:
                            print('logged author ('+t_author+') requested for his posts!')
                            result = get_blog_posts(order=in_query['order'],author=t_author)
                        else:
                            print('logged Superuser requested for all posts!')
                            result = get_blog_posts(order=in_query['order'])
                    else:
                        result = get_blog_posts(order=in_query["order"])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameter'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'author' in in_query:
                if in_query['author'].lower()=='aeyjey' or in_query['author'].lower() =='redranger' or in_query['author'].lower() == 'whoknows' :
                    result = get_blog_posts(author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'Author does not exists.'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'tag' in in_query:
                result = get_blog_posts(tag=in_query['tag'])
            elif token and not('orderby' in in_query and 'order' in in_query and 'author' in in_query and 'tag' in in_query and 'search' in in_query):
                if t_author:
                    print('logged author ('+t_author+') requested for his posts!')
                    result = get_blog_posts(author=t_author)
                else:
                    print('logged Superuser requested for all posts!')
                    result = get_blog_posts()

        else:
            resp = make_response({'success':False,'Server Error':'invalid query parameter(s)'})
            resp.mimetype = 'application/json'
            return resp
    else:
        result = get_blog_posts()
    try:
        if result[0] == 500:
            if result[1]['Server Error'] == "Database Error":
                resp = make_response({'success':False,'Server Error':'Database Connection Error'})
            elif result[1]['Server Error'] == "Invalid Orderby":
                resp = make_response({'success':False,'Server Error':'Invalid value for "orderby" query parameter'})
            elif result[1]['Server Error'] == "posts not found":
                resp = make_response({'success':False,'response':'no posts for given search'})
            elif result[1]['Server Error'] == "Invalid Search String":
                resp = make_response({'success':False,'response':'invalid search string'})
            else:
                resp = make_response({'success':False,'Server Error':f'Unknown Error -> {result[1]}'})
        else:
            resp = make_response({'success':True,f'articles':result})
    except TypeError:
        if result is None:
            resp = make_response({'success':False,'Server Error':'No Posts! Someone ate all the posts...'})
        else:
            resp = make_response({'success':True,f'articles':result})
    except IndexError:
        if len(result) == 0 :
            resp = make_response({'success':False,'Server Error':'No Posts for given filter!...'})
    finally:
        resp.mimetype = 'application/json'
        return resp

@app.route('''/blog/post''')
def get_post_by_id():
    '''
    gets the particular post in detail(same as /blog/posts but it will return the post of given id with its content!)
    '''
    print('post')
    id = request.args
    if 'id' in id:
        print(id['id'])
        id = id['id']
        db.create_all()
        result=fetch_post_by_id(id)
        try:
            if result[0] == 500:
                if result[1]['Server Error'] == "'NoneType' object is not subscriptable":
                    resp = make_response({'success':False,'Server Error':f'The Post Does Not Exists'})
                else:
                    resp = make_response({'success':False,'Server Error':'Unknown Error'})
        except KeyError:
            resp = make_response({'success':True,f'article':result})
        finally:
            resp.mimetype = 'application/json'
            return resp
    resp = make_response({'success':False,'Server Error':'missing query'})
    resp.mimetype = 'application/json'
    return resp

@app.route('''/blog/create''', methods=['POST'])
@token_optional
def upload_post(msg,token,admin):
    '''
    used for creating new article in database (in posts table)
    can accepts data via FormData or Json(preference is for FormData if not will look for Json)
    '''
    db.create_all()
    header = ''
    try:
        header = request.headers['<your_custom_auth_header_name>']
    finally:
        print(request.data)
        if token or current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
            if request.form and 'title' in request.form and 'content' in request.form and 'author'  in request.form and 'thumbnail' in request.form and 'tags' in request.form :
                print('\n\nformdata found!\n\n')
                title = request.form['title']
                print(title)
                content = request.form['content']
                print(content)
                author = request.form['author']
                print(author)
                tags = request.form['tags'].split(",")
                print(tags)
                if 'description' in request.form and request.form['description'] != "" :
                    description = request.form['description']
                    print(description)
                else:
                    description = content[0:50] + '...'
                    print(description)
                if request.form['thumbnail'] != "" :
                    thumbnail = request.form['thumbnail']
                    print(thumbnail)
                else:
                    thumbnail = 'https://demo.plugins360.com/wp-content/uploads/2017/12/demo.png'
                    print(thumbnail)
                r = insert_post_to_database(title, content, description, tags, thumbnail, author)
                if r:
                    resp = make_response({'success':True,'result':'post uploaded'})
                    resp.mimetype = 'application/json'
                    return resp
                else:
                    resp = make_response({'success':False,'result':'failed to upload post'})
                    resp.mimetype = 'application/json'
                    resp.status_code = 400
                    return resp
            elif request.data and request.json:
                req = request.get_json()
                if req:
                    print('\n\njson found!\n\n')
                    if 'title' in req and 'content' in req and 'author'  in req and 'thumbnail' in req and 'tags' in req :
                        title = req['title']
                        print(title)
                        content = req['content']
                        print(content)
                        author = req['author']
                        print(author)
                        if type(req['tags'])==list:
                            tags = req['tags']
                            print('tags list')
                        elif type(req['tags'])==str:
                            tags = req['tags'].split(",")
                            print('tags string -> list')
                        else:
                            tags = []
                        print(tags)
                        if 'description' in req and req['description'] != "" :
                            description = req['description']
                            print(description)
                        else:
                            description = content[0:50] + '...'
                            print(description)
                        if 'thumbnail' in req and req['thumbnail'] != "" :
                            thumbnail = req['thumbnail']
                        else:
                            thumbnail = 'https://demo.plugins360.com/wp-content/uploads/2017/12/demo.png'
                        print(thumbnail)
                        r = insert_post_to_database(title, content, description, tags, thumbnail, author)
                        if r:
                            resp = make_response({'success':True,'result':'post uploaded'})
                            resp.mimetype = 'application/json'
                            return resp
                        else:
                            resp = make_response({'success':False,'result':'failed to upload post'})
                            resp.mimetype = 'application/json'
                            resp.status_code = 400
                            return resp
                else:
                    print('no json')
                resp = make_response({'success':True,"result":"json compability under devlopement..."})
                resp.mimetype = 'application/json'
                resp.status_code = 200
                return resp
            else:
                resp = make_response({'success':False,"result":"missing form data for 'title','content','author','tags','description','thumbnail' in the request"})
                resp.mimetype = 'application/json'
                resp.status_code = 500
                return resp
        else:
            return make_response({'success':False,'response':'unauthorized access'})

@app.route('''/blog/update''', methods=['PUT','POST'])
@token_optional
def update_post(msg,token,admin):
    '''
    Used to update/modify the data (values) of article of given id(query param)
    accepted FormData or Json (preference is given to FormData values if not present will lookout for Json)
    only provide values for those attributes which are to be updated if provided attribute_name(like 'title') with no value then it will take it as empty(try to avoid such own errors)
    '''
    db.create_all()
    id = request.args
    if 'id' in id:
        id = id['id']
        header = ''
        try:
            header = request.headers['<your_custom_auth_header_name>']
        finally:
            req=request.get_json()
            if token or current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
                rtitle=''
                rcontent=''
                rauthor=msg if token and not admin else ''
                rdescription=''
                rtags=''
                rthumbnail=''
                presult=fetch_post_by_id(id)
                print(presult)
                try:
                    if presult[0] == 500:
                        if presult[1]['Server Error'] == "'NoneType' object is not subscriptable":
                            resp = make_response({'success':False,'Server Error':f'The Post Does Not Exists'})
                            resp.mimetype = 'application/json'
                            return resp
                        else:
                            resp = make_response({'success':False,'Server Error':'Unknown Error'})
                            resp.mimetype = 'application/json'
                            return resp
                except KeyError:
                    pass
                if token and not admin:
                    if msg!=presult['author']:
                        return jsonify({'response':'''can't update post of another author! ''','success':False})
                rtitle=presult['title']
                rcontent=presult['content']
                rdescription=presult['description']
                rtags=presult['tags']
                rauthor=presult['author']
                rthumbnail=presult['thumbnail']

                if request.form and 'title' in request.form or 'content' in request.form or 'author'  in request.form or 'thumbnail' in request.form or 'tags' in request.form or 'description' in request.form:
                    print('formdata found for update')
                    rtitle = request.form['title'] if 'title' in request.form else rtitle
                    print(rtitle)
                    rcontent = request.form['content'] if 'content' in request.form else rcontent
                    print(rcontent)
                    rauthor = request.form['author'] if 'author' in request.form else rauthor
                    print(rauthor)
                    rtags = request.form['tags'].split(",") if 'tags' in request.form and type(request.form['tags'])==str else rtags
                    print(rtags)
                    if 'description' in request.form:
                        if request.form['description'] != "" :
                            rdescription = request.form['description']
                            print(rdescription)
                        else:
                            rdescription = rcontent[0:50] + '...' if len(rcontent) else ''
                            print(rdescription)
                    if 'thumbnail' in request.form:
                        if request.form['thumbnail'] != "" :
                            rthumbnail = request.form['thumbnail']
                            print(rthumbnail)
                        else:
                            rthumbnail = 'https://demo.plugins360.com/wp-content/uploads/2017/12/demo.png'
                            print(rthumbnail)
                    r = update_post_by_id(id,rtitle, rcontent, rdescription, rtags, rthumbnail, rauthor)
                    if r:
                        resp = make_response({'success':True,'result':'post updated'})
                        resp.mimetype = 'application/json'
                        return resp
                    else:
                        resp = make_response({'success':False,'result':'failed to update post'})
                        resp.mimetype = 'application/json'
                        resp.status_code = 500
                        return resp
                elif req and 'title' in req or 'content' in req or 'author'  in req or 'thumbnail' in req or 'tags' in req or 'description' in req:
                    print('json found for update')
                    rtitle = req['title'] if 'title' in req else rtitle
                    print(rtitle)
                    rcontent = req['content'] if 'content' in req else rcontent
                    print(rcontent)
                    rauthor = req['author'] if 'author' in req else rauthor
                    print(rauthor)
                    rtags = req['tags'].split(",")  if 'tags' in req and type(req['tags'])==str else rtags
                    print(rtags)
                    if 'description' in req:
                        if req['description'] != "" :
                            rdescription = req['description']
                            print(rdescription)
                        else:
                            rdescription = rcontent[0:50] + '...' if len(rcontent) else ''
                            print(rdescription)
                    if 'thumbnail' in req:
                        if req['thumbnail'] != "" :
                            rthumbnail = req['thumbnail']
                            print(rthumbnail)
                        else:
                            rthumbnail = 'https://demo.plugins360.com/wp-content/uploads/2017/12/demo.png'
                            print(rthumbnail)
                    r = update_post_by_id(id,rtitle, rcontent, rdescription, rtags, rthumbnail, rauthor)
                    if r:
                        resp = make_response({'success':True,'result':'post updated'})
                        resp.mimetype = 'application/json'
                        return resp
                    else:
                        resp = make_response({'success':False,'result':'failed to update post'})
                        resp.mimetype = 'application/json'
                        resp.status_code = 500
                        return resp
                else:
                    resp = make_response({'success':False,"result":"missing form data for 'title','content','author' in the request"})
                    resp.mimetype = 'application/json'
                    resp.status_code = 500
                    return resp
            else:
                return make_response({'success':False,'response':'unauthorized access'})
    else:
        return make_response({'success':False,'response':'missing value of id'})

@app.route('''/blog/create''', methods=["GET"])
def upload_post_page():
    '''
    for creating new article from origin(direct) api site!
    (also has option to delete all current articles)
    (Yes its possible to do(not recommended though), if you don't want that functionality just remove this route or comment it out...)
    '''
    db.create_all()
    header = ''
    try:
        header = request.headers['<your_custom_auth_header_name>']
    finally:
        if token or current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
            return '''
            <br><br><br><br><br><hr>
            <form style="text-align: center;line-height: 1.5;" action="/blog/create" method="POST">
            <p style="font-size:calc(130px - 8vw);">Create A Post</p>
            <input style="font-size:calc(130px - 8vw);" type="text" name="title" placeholder="Enter Title" required /><br>
            <input style="font-size:calc(130px - 8vw);" type="text" name="content" placeholder="Enter Content" required /><br>
            <input type="text" name="author" placeholder="Enter Author" style="font-size:calc(130px - 8vw);" required><br>
            <input type="text" name="tags" placeholder="Enter Tags(seperated by commas,no spaces)" style="font-size:calc(130px - 8vw);" required><br>
            <input type="text" name="description" placeholder="Enter Description" style="font-size:calc(130px - 8vw);"><br>
            <input type="text" name="thumbnail" placeholder="Enter Link to thumnail" style="font-size:calc(130px - 8vw);"><br><br>
            <input style="font-size:calc(130px - 8vw);" type="submit" value="Create Article">
            </form><hr>
            <form style="text-align: center;line-height: 1.5;" action="/blog/post/delete" method="POST">
            <input style="font-size:calc(130px - 8vw);" type="submit" value="Delete all Articles">
            </form><hr>
            '''
        else:
            return make_response({'success':False,'response':'unauthorized access'})

@app.route('''/blog/post/delete''', methods=["GET","POST"])
def delete_all_posts():
    '''
    Used to delete all Articles or just to delete one article of which id is provided through query param
    '''
    db.create_all()
    id = request.args
    if 'id' in id:
        id = id['id']
        try:
            id = float(id)
            id = int(id)
        except:
            id = None
        finally:
            header = ''
            try:
                header = request.headers['<your_custom_auth_header_name>']
            finally:
                if token or current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
                    if id:
                        return delete_by(id)
                    else:
                        return make_response({'success':False,'response':'invalid post id'})
                    return delete_all()
                else:
                    return make_response({'success':False,'response':'unauthorized access'})
    else:
        header = ''
        try:
            header = request.headers['<your_custom_auth_header_name>']
        finally:
            if current_user.is_authenticated or header == '<the fixed authentication header value that you want for your api>' :
                return delete_all()
            else:
                return make_response({'response':'unauthorized access'})

@app.route('''/blog/login''', methods=['GET','POST'])
@token_optional
def blog_login(msg,token,admin):
    '''
    Login For authentication purpose!
    This performs login authentication on normal security level...
    accepts FormData or else Json (can also accepts token generated by previous login; then will just return that the user has already logged in[obviously ;-)]...)
    returns JWT Tokens generation which expires after 1 day (can be changed in the code...)
    use the returned jwt token as query param for /blog/create , /blog/update routes or for routes like where auth is required(observe the source code)
    '''
    db.create_all()
    if token:
        return jsonify({'response':'already logged in','success':True,'already_logged_in':True,'author':msg})
    form = request.form
    jsn = request.get_json()
    if form and 'username' in form and 'password' in form:
        username=form['username']
        password=form['password']
    elif jsn and 'username' in jsn and 'password' in jsn:
        username=jsn['username']
        password=jsn['password']
    else:
        return jsonify({'response':'login failed(login credentials not found!)','success':False})

    author=Author.query.filter_by(name=username).first()
    print('username: '+username)
    print('password: '+password)
    if not author:
        return jsonify({'response':'login failed(user not found!)','success':False})
    if check_password_hash(author.password,password):
        token= jwt.encode({'public_id':author.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},app.config['SECRET_KEY'])
        session.permanent = True
        session['_id'] = author.auth_id
        return jsonify({'response':'Logged in','token':token.decode('UTF-8'),'success':True,'already_logged_in':False,'author':username})

    return jsonify({'response':'Failed to login','success':False})

@app.route('''/blog/login/check''')
@token_optional
def getdatafor(msg,token,admin):
    '''
    used for checking the token recieved after succeful login is still valid or not?
    (can be helpful if want to check your token is still valid or not)
    '''
    if token:
        return jsonify({'response':'Logged In!','success':True,'author':msg, 'admin':admin})
    return jsonify({'response':'Not Logged In!(ps:'+msg+')','success':False})

@app.route('''/blog/admin''', methods=['GET'])
@token_optional
def blog_admin_page(msg,token,admin):
    '''
    This lets you login in yourself from Origin(Direct) Api site
    (Though Direct Usage of routes is not recommeneded still could be better if want to confirm by checking out something)
    '''
    db.create_all()
    if current_user.is_authenticated or token:
        return '<form style="text-align: center;" action="/blog/logout" method="POST" style="line-height: 1.5;"><p style="font-size:calc(200px - 10vw); margin-top:35vh;">Logout:</p><input style="font-size:calc(200px - 10vw);" type="submit" value="logout"></form>'
    return '<form style="text-align: center;" action="/blog/login" method="POST" style="line-height: 1.5;"><input style="font-size:calc(150px - 8vw);margin-top:35vh;" type="text" name="username" placeholder="Enter Name" required /><br><br><input type="password" name="passwd" placeholder="Enter Password" style="font-size:calc(150px - 8vw)" required><br><br><input style="font-size:calc(150px - 8vw)" type="submit" value="login"></form>'

@app.route('''/blog/author''', methods=['POST','GET'])
def admin_info():
    '''
    Gives information of author of given name(query param)
    '''
    db.create_all()
    name = request.args
    if 'name' in name:
        name = name['name']
        data = getadmindata(name)
        if data :
            resp = make_response({'success':True,f'author':data})
            resp.mimetype = 'application/json'
            return resp
        else:
            resp = make_response({'success':False,f'response':'author does not exist'})
            resp.mimetype = 'application/json'
            return resp
    resp = make_response({'success':False,f'response':'missing query'})
    resp.mimetype = 'application/json'
    return resp

@app.route('/blog/authorcreate', methods=['GET'])
def admin_info_post():
    '''
    from here you can create your author profile(can edit after posting it to your database from directly your database[recommended :-0])
    password will be in hashed form so try not to store non hashed password
    (for supported passwd type : for hashing password use generate_password_hash('your pass') function which comes in werkzeug.security library in python )
    (so u can do like this: "from werkzeug.security import generate_password_hash"  and then use that function to generate hashed passwd and then store it in your db author table in password column)
    '''
    db.create_all()
    name = 'RedRanger'
    rname = 'Jay A. Powar'
    public_id = 8192
    bio = 'The Programmer!\nWanna be the number one!✨'
    password = generate_password_hash('NewPassword')
    admin = False   #(set True for only one author)
    mail = 'jaypowar6@gmail.com'
    social = [['instagram','twitter','github'],['https://www.instagram.com/_redranger00_/','https://twitter.com/jay_powar?s=09','https://github.com/jaypowar00']]
    data = postadmindata(name,rname,bio,password,admin,mail,social)
    return '<h1>post data</h1>'

@app.route('''/blog/logout''', methods=["POST"])
def blog_logout():
    '''
    This will be useful only in direct usage of the api site!
    If using it on cross-domain/cross-site then you just have to delete/clear the local where token is stored..
    mostly recieved token will be stored in cookies and will be used (if present) for thereafter auth-required requests until it expires or user clicks on log out ater which you would have to clear that cookie(thats one way doing it though)
    '''
    db.create_all()
    if current_user.is_authenticated:
        session.pop("_id",None)
        logout_user()
        return make_response({'response':'logged out'})
    return make_response({'response':'not logged in'})
    
if __name__ == "__main__":
    db.create_all()
    app.run()
