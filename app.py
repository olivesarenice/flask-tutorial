from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
db = SQLAlchemy(app)

class myList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(128), nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Entry {self.id}'

@app.route('/', methods = ['POST','GET'])
def index():
    if request.method == 'GET':
        tasks = myList.query.order_by(myList.date_created).all()   
        return render_template('index.html',tasks=tasks)

            
    elif request.method == 'POST':
        task_content = request.form["content"]
        newEntry = myList(content = task_content)
        
        try:
            db.session.add(newEntry)
            db.session.commit()
            
            return redirect("/")

        except:
            return "Error with adding to database"
    else:
        return 'Method not allowed'

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = myList.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Task not found'

@app.route('/update/<int:id>', methods = ['GET', 'POST']) # Need 2 methods. GET will load the update page. POST will send the update
def update(id): 
    task = myList.query.get_or_404(id) # Either way, retrieve the task data first
    if request.method == 'GET': # When the user first clicks on Update
	    return render_template('update.html', task=task) # send them to the update.html page with the form preloaded with the selected task data.
    elif request.method == 'POST': # Then when they POST the updated data,
        task.content = request.form["content"] # Update the task contents with the ontent in the form
        try:
            db.session.commit() # Update the database
            return redirect("/")
        except:
            return 'Could not update.' 
    else:
        return 'Method not allowed'

if __name__ == "__main__":
    app.run(debug=True)