from typing import List, Dict
from flask import Flask,request,jsonify, flash, redirect, url_for
import json
import redis
from rq import Queue
from background_task import background_task_call as bt
from rq.job import Job
from rq.registry import StartedJobRegistry

import time
from werkzeug.utils import secure_filename
import os


# https://pythonise.com/series/learning-flask/flask-rq-task-queue

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379)
q = Queue(connection=r)

UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index() -> str:
    return "Hello World"


@app.route('/all')
def all() :
    global q
    json_response = []
    ll = []
    type_list = ["started","deferred","finished","failed","scheduled","Queue"]
    ll.append(q.started_job_registry.get_job_ids())  # Returns StartedJobRegistry
    ll.append(q.deferred_job_registry.get_job_ids())   # Returns DeferredJobRegistry
    ll.append(q.finished_job_registry.get_job_ids())  # Returns FinishedJobRegistry
    ll.append(q.failed_job_registry.get_job_ids())  # Returns FailedJobRegistry
    ll.append(q.scheduled_job_registry.get_job_ids())  # Returns ScheduledJobRegistry
    ll.append(q.job_ids)  # Returns ScheduledJobRegistry
    json_element1={}
    for i, jobs_list in enumerate(ll):
        # json_response[type_list[i]]=[]
        json_element1={}
       
        json_element={}
        for j_id in jobs_list:
            json_element[j_id]=json.dumps(get_status(j_id))
            
        json_element1[type_list[i]]=json_element
        json_response.append(json_element1)
   
    return json.dumps(json_response)
        

# [0]['testid1','query1','"metrics": { "ndcg@3": "1.0", "ndcg@7": "0.9" }']
#  [1]['testid2','query2','"metrics": { "ndcg@3": "1.0", "ndcg@7": "0.9" }']

# column_names=("test_id","querytext","metrics")
#     json_response={}
#     for entry in response:
#         if entry[0] not in json_response:
#             json_response[entry[0]]=[]
#         json_element={}
#         json_element[column_names[1]]=entry[1]
#         json_element[column_names[2]]=json.loads(entry[2])
#         json_response[entry[0]].append(json_element)
#     return json.dumps(json_response)



@app.route("/task")
def task():

    if request.args.get("n"):

        job = q.enqueue(bt, request.args.get("n"))

        return f"Task ({job.id}) added to queue at {job.enqueued_at}. Total Job {len(q)}"

    return "No value for count provided"

@app.route("/status")
def status():

    if request.args.get("jobid"):
        task_id = request.args.get("jobid")
        
        return jsonify(get_status(task_id))

    return "No value for count provided"

def get_status(task_id):
    task = q.fetch_job(task_id)
    if task:
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id(),
                "task_status": task.get_status(),
                "task_result": task.result,
            },
        }
    else:
        response_object = {"status": "No taskid"}
    return response_object



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        # files = request.files['file']
        files = request.files.getlist("file")
        # if user does not select file, browser also
        # submit an empty part without filename
        for file in files:
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                er = "Error in {}".format(filename)
                return er
        return "Success"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=file name=file>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0')