# Sanjana Chowdary
# To Do List App

from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3
import random

app = Flask(__name__)


motivational_messages = [
    "You got this! 💪",
    "Keep going! 🚀",
    "Great job! 🎉",
    "Stay focused! 💡",
    "You're unstoppable! 🌟",
    "Believe in yourself! 🌈",
    "One step at a time! 🏃‍♂️",
    "You're making progress! 📈",
    "Keep pushing! 🔥",
    "Success is near! 🏆",
    "Stay strong! 💪",
    "You're doing amazing! 🌟",
    "Stay positive! 😊",
    "You've got the power! ⚡",
    "Every task is a victory! 🏅",
    "Keep crushing it! 🔨",
    "Your hard work will pay off! 💰",
    "Don't stop now! 🎯",
    "You're almost there! ⏳",
    "Let's make it happen! 🚀"
]

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        due_date TEXT,
                        completed BOOLEAN DEFAULT 0  -- Add a column to track completion status
                     )''')
    conn.commit()
    conn.close()

    
    
def convert_dates():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, due_date FROM tasks")
    tasks = cursor.fetchall()

    for task in tasks:
        task_id = task[0]
        old_date = task[1]
        try:
            datetime.datetime.strptime(old_date, "%Y-%m-%d")
            continue
        except ValueError:
            pass
            
        try:
            old_date_obj = datetime.datetime.strptime(old_date, "%B %d, %Y")
            new_date = old_date_obj.strftime('%Y-%m-%d')

            cursor.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (new_date, task_id))
        except:
            pass

    conn.commit()
    conn.close()
    

@app.route('/')
def index():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, due_date, completed FROM tasks ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date DESC")
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)



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
            print("Formatted Due Date:", due_date_formatted)  # Debugging print statement
        else:
            due_date_formatted = None
        
        cursor.execute("INSERT INTO tasks (task, due_date) VALUES (?, ?)", (task, due_date_formatted))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, date(due_date) DESC")

    tasks = cursor.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks, message=message)
    

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

    
