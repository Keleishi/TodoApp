from flask import Flask, render_template, request, url_for, redirect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

# Connect to the MongoDB cluster
uri = "mongodb+srv://todoapp:7JqigwjMK5Cge0Pn@cluster0.b23rpjp.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

# Verify successful connection by sending a ping
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create a new Flask app
app = Flask(__name__)

# Connect to the MongoDB database and collection for storing todos
db = client.flask_db
todos = db.todos


# Define the route for the homepage, which displays all todos and a form to add new todos
@app.route('/', methods=('GET', 'POST'))
def index():
    # If the form has been submitted, add a new todo to the database
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        completed = request.form.get('completed', False)
        todos.insert_one({'content': content, 'degree': degree, 'completed': completed})
        return redirect(url_for('index'))

    # Get all todos from the database and render the homepage template with the todos
    all_todos = todos.find()
    return render_template('index.html', todos=all_todos)


# Define the route for deleting a todo
@app.post('/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


# Define the route for updating a todo
@app.route('/<id>/update', methods=('GET', 'POST'))
def update(id):
    # Get the current todo from the database
    todo = todos.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        # If the form has been submitted, update the todo in the database
        new_content = request.form['content']
        new_degree = request.form['degree']
        new_completed = request.form.get('completed', False)
        todos.update_one({"_id": ObjectId(id)},
                         {"$set": {"content": new_content, "degree": new_degree, "completed": new_completed}})
        return redirect(url_for('index'))

    # Render the update template with the current todo
    return render_template('update.html', todo=todo)


# Define the route for marking a todo as complete or incomplete
@app.route('/<id>/complete/')
def complete(id):
    todo = todos.find_one({"_id": ObjectId(id)})
    completed = not todo['completed']
    todos.update_one({"_id": ObjectId(id)}, {"$set": {"completed": completed}})
    return redirect(url_for('index'))



# Start the Flask app
if __name__ == '__main__':
    app.run()
