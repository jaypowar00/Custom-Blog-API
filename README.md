# Custome Blog API
# API using Python - Flask - Postgresql
(understand the code before running it blindly)

The app.py is like a skeleton!

don't try to run it without modiying it...
you have to enter your own credentials for the postgresql database...
there are some values indicated by <> , inside which you have supposed to fillup the particular data...

(Created some temporary GET route for posting form data quickly!)

don't except 100% output without modiying it...
## 1) /blog/posts
This gets all the data from given table of from the database and return it in json format (array of objects)

e.g. looks like this...
```
{
  "users" : [
  {
    "name":"user1",
    "email": "user1@example.com"
  },
  {
    "name":"user2",
    "email": "user2@example.com"
  }
  ]
}
```
this route also includes advanced queries!
+ ?order=  [either 'asc' or 'desc' | bydefault it's set to 'desc']
  This will decide in which order the query should give response json either in ascending or descending order.
+ ?orderby= [could have '_id','title','author','created' or 'description' | bydefault it's set to 'created']
  This will tell according to what basis the query should fetch the data from database.[bydefault it will fetch latest data first and oldest last]
+ ?author= [could have name of author | bydefault its None]
  This will fetch data for given author name from db
+ ?tag= [could have any tag value | bydefault its None]
  This will fetch all data whose tags matches the given tag.
+ ?search= [could have any search string which is to be searched]
  This will fetch all data related to the search string

(These queries can be combined together for more accuracy in response as per required!)

## 2) /blog/admin
for admin previleges, must login for performing some adding or deleting posts operations !(from api site)

## 3) /blog/create
Will insert the Title, Author, Content, Description, Tags, Thumbnail data into posts Table!
i.e. it will create a new Article!

Required fields for creation of post:
type -> form data
- title
- author
- content
- description [optional will set value as 50 characters from content]
- tags [needs to be array]
- thumbnail

query parameter:
+ ?token=<token generated after successful login>
  This will be checked for authorized access for creating new Articles

## 4) /blog/post?id=
This route will fetch data for single post of mentioned _id from the database...

## 5) Login through C_AUTH header request
Added feature for logging in via header request (C_AUTH) with particular key value !
(if working on cross-domain/cross-site it will give only one time access, so would've to use it with all requests!)

## 6) /blog/post/delete
This will delete all posts from db

query parameters:
+ ?id=  [It could be any existing post id]
  This will delete the post of given id from db

## 7) /blog/author
This route will give information about author if 'name' query parametr is given to this route.

query parameters:
+ ?name=  [it could have any available author name]
  This will fetch the information about given author name.
  
## 8) /blog/update
This will update the data values from the existing post of given 'id' parameter.

query parameters:
+ ?id= [it could be any existing post id]
  This will define the post which is to be updated
+ ?token=<token generated after successful login>
  This will be checked for authorized access for Updating new Articles

Required fields for updation of post of given id:
(only give the params which needs to be updated from post with given id other data will reamain as it is!)
type -> form data
- title
- author
- content
- description
- tags [needs to be array]
- thumbnail
## 9) /blog
(does nothing but something is one query param is provided!)

query parameter:
+ ?get=tag
  This will fetch all the tags that have been used in all current existing articles

## 10) /blog/login
This is used for authentication, as it sounds it performs login of particular user and generates a jwt token which can be used to access routes like `/blog/create` and `/blog/update` without any auth-header (token will expire after 1 day)

query parameter:
+ ?token=<token generated after successful login>
  This will respond that the user is already logged in!(only if token is valid and not expired..)

## 11) /blog/login/check
This is used to check if the user is logged in or not(obviously will need help of jwt token)

query parameter:
+ ?token=<token generated after successfull login>
  This will respond accordingly the token is provided
e.g.
```
  {
    "response":"Not Logged In!(ps:token is missing)",
     "success":false
  }
```
    
# Web App Under Development!
This is still under developement ...
