from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
import random
import os
import openai
import csv
from dotenv import load_dotenv, dotenv_values

app = Flask(__name__)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
# app.config["TEMPLATES_AUTO_RELOAD"] = True
motivational_messages = [
    "You got this! 💪", "Keep going! 🚀", "Great job! 🎉", "Stay focused! 💡",
    "You're unstoppable! 🌟", "Believe in yourself! 🌈", "One step at a time! 🏃‍♂️",
    "You're making progress! 📈", "Keep pushing! 🔥", "Success is near! 🏆",
    "Stay strong! 💪", "You're doing amazing! 🌟", "Stay positive! 😊", 
    "You've got the power! ⚡", "Every task is a victory! 🏅", "Keep crushing it! 🔨", 
    "Your hard work will pay off! 💰", "Don't stop now! 🎯", "You're almost there! ⏳", 
    "Let's make it happen! 🚀"
]
users = [
    {"id": 1, "name": "Peer 1", "image_url": "path_to_peer_image_1.jpg", "class": "Class 1"},
    {"id": 2, "name": "Peer 2", "image_url": "path_to_peer_image_2.jpg", "class": "Class 1"},
    {"id": 3, "name": "Peer 3", "image_url": "path_to_peer_image_3.jpg", "class": "Class 2"},
    {"id": 4, "name": "Peer 4", "image_url": "path_to_peer_image_4.jpg", "class": "Class 2"},
    {"id": 5, "name": "Peer 5", "image_url": "path_to_peer_image_5.jpg", "class": "Class 3"},
    {"id": 6, "name": "Peer 6", "image_url": "path_to_peer_image_6.jpg", "class": "Class 4"}
]

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        due_date TEXT,
                        completed BOOLEAN DEFAULT 0
                     )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['POST','GET'])
def index():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, due_date, completed FROM tasks ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date DESC")
    tasks = cursor.fetchall()
    
    # calculate completion percentage
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task[3] == 1)
    completion_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    #chatbot tings
    prompt = request.form.get("prompt")
    if not prompt:
        prompt = "Hi how are you today? What questions can i ask you to start off our conversation?"
    print(tasks)
    print(prompt)
    output = chatbot(prompt,tasks)
    print(output)
    
    tasksplitfromhtml = request.form.get("tasksplit")
    if not tasksplitfromhtml:
        tasksplitfromhtml = "None"
        tasksplits = ""
    else:
        tasksplits = tasksplit(tasksplitfromhtml)
    
    conn.close()
    return render_template('index.html', tasks=tasks, completion_percentage=int(completion_percentage), output=output, splits = tasksplits)
def chatbot(prompt,tasks):
    tasks_string = "\n".join([f"ID: {task[0]}, Task: {task[1]}, Due Date: {task[2]}, Completed: {bool(task[3])}" for task in tasks])
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful ToDo list assistant. You are helping the user manage their tasks. The following are the tasks the user has and their due dates with what questions they have asked you. Respond to their questions with helpful answers."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "These are my tasks"},
            {"role": "assistant", "content": tasks_string}


        ]
    )
    response = completion.choices[0].message.content
    return response
def tasksplit(task):
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Split the following task into less than 5 subtasks in numbered form,"},
            {"role": "assistant", "content": task}
        ]
    )
    response = completion.choices[0].message.content
    return response
@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    due_date = request.form.get('due_date')
    message = random.choice(motivational_messages)

    if task:
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        if due_date:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            due_date_formatted = due_date_obj.strftime("%B %d, %Y")
            print("Formatted Due Date:", due_date_formatted)
        else:
            due_date_formatted = None
        
        cursor.execute("INSERT INTO tasks (task, due_date) VALUES (?, ?)", (task, due_date_formatted))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, date(due_date) DESC")

    tasks = cursor.fetchall()
    
    # Calculate completion percentage
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task[3] == 1)
    completion_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    conn.close()

    return render_template('index.html', tasks=tasks, message=message, completion_percentage=int(completion_percentage))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    current_status = cursor.fetchone()[0]

    new_status = 0 if current_status == 1 else 1

    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    return '', 204

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/groups')
def groups():
    return render_template('groups.html') 


user = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'classes': 'Math 101, Physics 102, Computer Science 103',
    'peer_preferences': 'Available for group work in the evenings',
    'find_peers': True
}

@app.route('/settings')
def settings():
    return render_template('settings.html', user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():

    user['name'] = request.form['name']
    user['email'] = request.form['email']
    user['classes'] = request.form['classes']
    
   
    return redirect(url_for('settings'))

@app.route('/update_peer_finding', methods=['POST'])
def update_peer_finding():

    user['peer_preferences'] = request.form['peer_preferences']
    user['find_peers'] = 'find_peers' in request.form 
    
    return redirect(url_for('settings'))



def read_users():
    users = []
    with open('users.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            users.append(row)
    return users

@app.route('/find_peer')
def find_peer():
    return render_template('find_peer.html')

@app.route('/submit', methods=['POST'])
def submit():
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']
    q4 = request.form['q4']
    q5 = request.form['q5']
    q6 = request.form['q6']
    q7 = request.form['q7']

    users = read_users()
    matched_user = None
    for user in users:
        name, email, answers = user[0], user[1], user[2:]
        matches = sum([1 for i in range(5) if answers[i] == [q3, q4, q5, q6, q7][i]])

        if matches >= 2:
            matched_user = user
            break

    if not matched_user:
        warning_message = "No matches found with 1 or more answers."
        return render_template('find_peer.html', warning_message=warning_message)

    return render_template('find_peer.html', user=matched_user)

@app.route('/reject/<user_id>', methods=['GET'])
def reject(user_id):
    print(f"User with ID {user_id} was rejected.")
    return redirect(url_for('find_peer'))

@app.route('/accept/<user_id>', methods=['GET'])
def accept(user_id):
    print(f"User with ID {user_id} was accepted.")
    return redirect(url_for('find_peer'))

def get_users():
    conn = sqlite3.connect('peer_matching.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
