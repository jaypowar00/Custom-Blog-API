# api-demo-public
# API using Python - Flask - Postgresql
(understand the code before running it blindly)

The app.py is like a skeleton!

don't try to run it without modiying it...
you have to enter your own credentials for the postgresql database...
there are some values indicated by <> , inside which you have supposed to fillup the particular data...

This gets all the data from given table of from the database and return it in json format (array of objects)
e.g.

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

This is still under developement ...
