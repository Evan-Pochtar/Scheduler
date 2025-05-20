from flask import Flask, render_template, request, jsonify
import csv
import os
from datetime import datetime, timedelta
import pytz

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, 'data.csv')
app = Flask(__name__)

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return {"tasks": []}
    
    tasks = []
    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string representations back to appropriate data types
            task = {}
            for key, value in row.items():
                if key == 'id':
                    task[key] = int(value)
                elif key == 'completed':
                    task[key] = value.lower() == 'true'
                else:
                    task[key] = value
            tasks.append(task)
    
    return {"tasks": tasks}

def save_tasks(data):
    tasks = data['tasks']
    if not tasks:
        # Create empty file with headers if no tasks
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'title', 'description', 'date', 'completed', 'recurrence_type', 'recurrence_value'])
        return
    
    # Get all possible headers from all tasks
    fieldnames = set()
    for task in tasks:
        fieldnames.update(task.keys())
    
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(tasks)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    data = load_tasks()
    return jsonify(data)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = load_tasks()
    new_task = request.json
    
    if 'id' not in new_task:
        max_id = 0
        for task in data['tasks']:
            if task['id'] > max_id:
                max_id = task['id']
        new_task['id'] = max_id + 1
    
    data['tasks'].append(new_task)
    save_tasks(data)
    return jsonify(new_task)

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = load_tasks()
    updated_task = request.json
    
    for i, task in enumerate(data['tasks']):
        if task['id'] == task_id:
            data['tasks'][i] = updated_task
            save_tasks(data)
            return jsonify(updated_task)
    
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    data = load_tasks()
    
    for i, task in enumerate(data['tasks']):
        if task['id'] == task_id:
            del data['tasks'][i]
            save_tasks(data)
            return jsonify({"success": True})
    
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/compute-next-occurrence', methods=['POST'])
def compute_next_occurrence():
    task_data = request.json
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    if task_data['recurrence_type'] == 'days':
        days = int(task_data['recurrence_value'])
        # Use noon time to avoid timezone issues
        current_date = datetime.strptime(f"{task_data['date']}T12:00:00", '%Y-%m-%dT%H:%M:%S')
        next_date = (current_date + timedelta(days=days)).strftime('%Y-%m-%d')
        return jsonify({"next_date": next_date})
    
    elif task_data['recurrence_type'] == 'weekdays':
        weekdays = task_data['recurrence_value'].split(',')
        # Use noon time to avoid timezone issues
        current_date = datetime.strptime(f"{task_data['date']}T12:00:00", '%Y-%m-%dT%H:%M:%S')
        next_date = current_date + timedelta(days=1)
        
        for _ in range(7):  # Check next 7 days max
            day_name = next_date.strftime('%A').lower()
            if day_name in weekdays:
                return jsonify({"next_date": next_date.strftime('%Y-%m-%d')})
            next_date += timedelta(days=1)
            
    return jsonify({"error": "Could not compute next occurrence"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=1717)