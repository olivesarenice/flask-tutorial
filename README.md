# WILL UPDATE THIS LATER, STORING SOME NOTES FIRST

Learning about how Flask @app.route("/") actually works sent me down a rabbithole of learning about **decorators**.

In Flask apps, the code is usually:

from flask import Flask

app = Flask(__name)

@app.route('/hello')
def hello():
    return "Hello, World!"

First, I need to understand what the decorators (@...) actually do. The purpose of decorators is to modify the behaviour of another function without having to touch the source code of said function. This is similar to how wrappers works. The difference is that wrapper(function()) needs to be called everytime we want to get the modified behaviour. Decorators are applied from the beginning when the function is defined.

A working example:

def decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@decorator
def say_hello():
    print("Hello!")

say_hello()

The decorator has 2 parts:
- The decorator() function which when called will take in a function and modify its behaviour.
- The @decorator syntax which says which functions decorator() should take in.

Thus, whenever say_hello() is called, it will now be calling decorator(say_hello). The inner wrapper() specified what to do with say_hello function subsequently.

In the case of Flask, the `@app.route()` decorator is referencing the `route` function within the `app` object that was created with the `Flask` command.

So why does requesting a HTTP GET to http://flask_app_url/hello trigger the hello() command?

Unlike the above example, `route()` doesnt actually modify the behaviour of `say_hello`. It simply takes `/hello` and add its to the `app` router - a list of reachable endpoints, along with the function `say_hello` which should be called when this endpoint is reached.

This is described in the documentation for `route`:

def route(self, rule, **options):
        """A decorator that is used to register a view function for a
        given URL rule.  This does the same thing as :meth:`add_url_rule`
        but is intended for decorator usage::
            @app.route('/')
            def index():
                return 'Hello World'
        For more information refer to :ref:`url-route-registrations`.
        :param rule: the URL rule as string
        :param endpoint: the endpoint for the registered URL rule.  Flask
                         itself assumes the name of the view function as
                         endpoint
        :param options: the options to be forwarded to the underlying
                        :class:`~werkzeug.routing.Rule` object.  A change
                        to Werkzeug is handling of method options.  methods
                        is a list of methods this rule should be limited
                        to (``GET``, ``POST`` etc.).  By default a rule
                        just listens for ``GET`` (and implicitly ``HEAD``).
                        Starting with Flask 0.6, ``OPTIONS`` is implicitly
                        added and handled by the standard request handling.
        """
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

This is how Flask knows what functions to call when certain HTTP requests are made.

In fact, we could do the same thing without `route` with the following code:

app = Flask(_name_)

def say_hello():
    return "Hello!"

app.add_url_rule("/", "hello", say_hello)

In this way, it is much clearer how `app` decides what to execute based on the requests it gets.

Setting up a basic Flask app! (on Google Firebase)

https://jakevdp.github.io/blog/2016/08/25/conda-myths-and-misconceptions/

Typical webserver folders
- env (this shd contain all the python dependencies to run, im using conda so i dont have that)
-static 
-templates
app.py

Flask uses jinja2 which is a templating enginer for Python. We can define templates which can be used across differnt pages.
- create a base template and have other pages inherit from this template.
- dynamically replace content using template syntax like {{ this_thing_will_be_turned_into_a_string }} and control logic {% logical_function %}


In templates, create the index.html and base.html .

index.html <--inherits from-- base.html

Wherever we want to add dynamic content, we can use:

{% block BLOCK_NAME %}

followed by {% endblock %}.

We can also dynamically generate strings based on functions and then pass them as HTML variables:

For e.g. to generate the href to our main.css file, we can use:

 href="{{ url_for('static',filename='css/main.css') }}"

{{ variable }} turns anything inside into a string.

url_for is a Flask function that generates a URL to a specified app endpoint along with parameters for that endpoint (if erquired)

The static folder just happens to be accessible by builtin endpoint. 

See app.url_map:

Map([<Rule '/static/<filename>' (HEAD, GET, OPTIONS) -> static>])

i.e. accessing static endpoint will return the string '/static/<filename>` where filename will be replaced with whatever parameter was sent to the endpoint. Hence we set the parameter as the path to the file inside /static directory.

simply:

{{ url_for(static,filename='css/main.css' }}

e.g.

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>My Website</title>
    <link rel="stylesheet" href="{{ url_for('static',filename='css/main.css') }}">
    <link rel="icon" href="./favicon.ico" type="image/x-icon">
    {% block head %}{% endblock %} 
  <body>
    {% block body %}{% endblock %}
  </body>
</html>

. Then in the page we want to create from the base.html template, we enter:

{% extends 'base.html'%}  // use base.html as the template

{% block head %} // define the content for the 'head' block
<h1> Some Header... </h1>
{% endblock %} 

{% block body %} // define the content for the 'body' block
Some text
{% endblock %}

NEXT, we need a database to store user inputs:

Use SQLAlchemy...

Tell the app that we want to add a sqlite db resource
app.config['SQLALCHEMY_DATABSE_URI'] = 'sqlite:///test.db' # 

then have SQLAlchemy create a db using that resource.

for demo we create a db.Model object that has the properties we need.
https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
we are saying that the model should have id, content, date_created, which are their own columns of (type, other parameters)

We can initialise the database file .db from the configurations within app with a python interpreter:

> from app.py import db
> db.create_all()
> exit()

next, we need to create some logic for the user.

the user can either view the current table (GET) or add a  new row to the table (POST).

if the request to the app is a POST, we will use the information submitted with POST to add a database entry:

on the frontend HTML, create a simple HTML form:

    <form action="/" method="POST"> // sends this POST to the / endpoint
        <input type="text" name="content" id="content"> 
        <input type="submit" value="Add">

on the app backend:

    if request.method == 'POST':
        task_content = request.form["content"]
        newEntry = myList(content = task_content) # pass the content from the form to the database model
        
        try:
            db.session.add(newEntry) 
            db.session.commit() # add it to the db
            
            return redirect("/") # note that we need to import redirect module from flask

        except:
            return "Error with adding to database"

OTHERWISE, if it is a GET method:

    else:
        tasks = myList.query.order_by(myList.date_created).all()   
        return render_template('index.html',tasks=tasks)

query the database myList, then order_by the results by date_created, and return all the results.

pass the resuts to the .html and then redner the page.

on the frontend, we take in the tasks variable and use jinja to loop through each task and put the task.content and date_created as a string inside the table row.

        {% for task in tasks %}
            <tr>
                <td>{{ task.content}}</td>
                <td>{{ task.date_created}}</td>
                <td>
                    <a href="">Delete</a>
                    <br>
                    <a href="">Update</a>
                </td>
            </tr>
        {% endfor %}

NOW ADD MORE FUNCTIONALITY: DELETE

A user should be able to delete an entry in the table.

Frontend:
When user clicks the delete button, send a request to the /delete endpoint, along with the task id to delete. /delete/{{ task.id }}

Backend:
Create new route 
@app.route('/delete/<int:id>') # ensures that the task id is an integer
def delete(id):
    task_to_delete = myList.query.get_or_404(id) # try to get the row from DB
    try:
        db.session.delete(task_to_delete) # delete it and commit
        db.session.commit()
        return redirect('/')
    except:
        return 'Task not found'

NEXT FUNCTION: UPDATE

A user can update the content of a row. They will edit the content on another page.

Frontend:
When user clicks on update button, send a GET request to the /update endpoint, along with the task id to update /update/{{ task.id }}

Create the update.html page they will be sent to.
It will contain a form which preloads the task content in the box. When the user clicks on update button, it will POST to the same /update endpoint.

<div class="content">
    <h2>Update Entry </h2>
    <form action="/update/{{ task.id }}" method="POST">
        <input type="text" name="content" id="content" value={{ task.content }}> 
        <input type="submit" value="Update">
    </div>

Note that update.html requires the task data as well to load id and content.

Backend:

@app.route('/update/<int:id>', methods = ['GET', 'POST']) # Need 2 methods. GET will load the update page. POST will send the update
def update(id): 
    task = myList.query.get_or_404(id) # Either way, retrieve the task data first
    if request.method == 'GET': # When the user first clicks on Update
	return render_template('update.html', task=task) # send them to the update.html page with the form preloaded with the selected task data.

    elif request.method == 'POST: # Then when they POST the updated data,
        task.content = request.form["content"] # Update the task contents with the ontent in the form
        try:
            db.session.commit() # Update the database
            return redirect("/")
        except:
            return 'Could not update.' 
        
TO HOST THE APP: Use Digital Ocean App Platform, will build from Github repo;;

https://dev.to/ajot/how-to-deploy-a-flask-app-to-digital-oceans-app-platform-goc

1) Create a GH repo for project