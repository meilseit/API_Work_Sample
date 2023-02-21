
import redis
import string
import importlib
import pandas as pd
from flask import Flask
from flask_restful import Resource, Api, abort
from rq import Queue
from datetime import datetime, timedelta
from random import choice 

#local imports
from jobs import complex_task

#set up path to mock data base in this case a simple csv to easily see presisted values
path = './task_data.csv'

#queue worker struggles to find callback function is the appropriate module so this line will make it explicit
module = importlib.import_module('api') 

#set up api and underlying flask app 
app = Flask(__name__) #init flask application
api = Api(app)        #init flask api

#set up queue and connection to redis for for async task proccess
preconfigured_timeout = 180 #set a default timeout for tasks that take long 
connection = redis.Redis(host='redis', port=6379) #start up a connection on default port 
queue = Queue('pipeline', connection=connection, default_timeout=preconfigured_timeout) #initilize queue and name it pipline

#set up callback functions to execute when task is completed
def process_success(job, connection, result, *args, **kwargs):
    '''
    Requires all the default parameters above based on the documentation
    This function connects to the mock data base to update 
    timestamp_end, status, and result based on exacution results
    '''
    df = pd.read_csv(path)
    df.loc[df['job_id'] == job.id, ['timestamp_end','status', 'sleep_time']] = [datetime.now(), "completed", job.result]
    df.to_csv(path, index=False) #save data to storage

def process_failure(job):
    '''
    Requires all the default parameters above based on the documentation
    This function connects to the mock data base to update 
    timestamp_end, status, and result based on exacution results
    '''
    df = pd.read_csv(path)
    df.loc[df['job_id'] == job.id, ['timestamp_end','status', 'sleep_time']] = [datetime.now(), 'failure', job.result]
    df.to_csv(path, index=False) #save data to storage

#set up a function that gives us short ids for testing
def random_job_id_gen(size):
    '''
    Required desired job_id length as a parameter.
    If this program was scaled up it would be desirable
    to ensure the uniqueness of job_ids but for now this works.
    Returns a string of random letters and digets
    '''
    return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(size))

#set up abort functions for invalid informations for the api
def abort_if_job_id_doesnt_exist(job_id, data):
    """
    Requires a job_id and a dataframe object from pandas.
    If job_id is not in the mock data base we cannot get meta data
    so we abort the request
    """
    if job_id not in set(data['job_id']):
        abort(404, message= "Task {} doesn't exist".format(job_id))


def abort_if_object_id_is_proccessing(object_id, data):
    """
    Requires a object_id and a dataframe object from pandas.
    If a second object_id is submitted matching one proccessed in 
    the last 5min we want to abort the request
    """
    matching_tasks = data.get(data['object_id'] == object_id) #query for matching object_id
    #compare there timestamp_start value to now return a boolean. Abort request if any matching object_id is Flase
    if not matching_tasks.empty: 
        cond = matching_tasks['timestamp_start'] \
            .astype(dtype='datetime64[ns]') \
            .apply(lambda date:  (date + timedelta(minutes=5)) <= datetime.now()) \
            .all() 
        if not cond:
            abort(406, message= "Object: {} is still proccessing. This action is not accepted".format(object_id))


class StartTask(Resource):
    #Set up resource class to handle put request with object_id parameters

    def put(self, object_id):
        '''
        Accepts object_id parameter
        Return message about task with job_id
        '''
        job_id = random_job_id_gen(5) #generate job_id

        df = pd.read_csv(path) #read in current data
        abort_if_object_id_is_proccessing(object_id, df)
        
        new_df = pd.DataFrame({
            'object_id': [object_id],
            'job_id': [job_id],
            'status': ['queued'], 
            'timestamp_start': [datetime.now()],
            'timestamp_end': ['Pending'], 
            'sleep_time': ['Pending']
        })

        new_df.astype(str) #ensure all csv entries will be strings
        df = pd.concat([df, new_df]) #add new dataframe to exsisting dataframe
        df.to_csv(path, index=False) #save appended data back to mock database

        task = queue.enqueue(complex_task, job_id = job_id, on_success=module.process_success, on_failure=module.process_failure)
        

        return {
            'message': 'Your task is being processed. Use job_id to check status',
            'job_id': job_id
        }, 200

class TaskStatus(Resource):
    #set up resource class for to handle get request with job_id parameter 

    def get(self, job_id):
        '''
        Accepts job_id parameter
        Return metadata relating to the 
        jobs progress.
        '''
        df = pd.read_csv(path)
        abort_if_job_id_doesnt_exist(job_id, df)
        data = df.loc[df['job_id'] == job_id]

        return {'metadata':{
            'job_id': data['job_id'].to_string(index = False),
            'object_id':data['object_id'].to_string(index = False),
            'status':data['status'].to_string(index = False),
            'time_start':data['timestamp_start'].to_string(index = False),
            'time_finished': data['timestamp_end'].to_string(index = False),
            'job_duration':data['sleep_time'].to_string(index = False),

        }, 'message': 'data retrival successful'}, 200

 #add resources and corresponding endpoints to api
api.add_resource(StartTask, '/start/<string:object_id>') #define endpoints for put request 
api.add_resource(TaskStatus, '/status/<string:job_id>') #define endpoints for get request 

#add function to handle server restarts if the service does down
@app.before_first_request
def requeue_if_server_crash():
    '''
    Takes no parmeters but will run on server restarts.
    Searchs data base and requeues any objects marked as queued 
    '''
    df = pd.read_csv(path)
    print("Checking for interupted task and requeueing if needed.")
    unfinished_tasks = df.get(df['status'] ==  'queued')
    if not unfinished_tasks.empty:
        unfinished_tasks.apply(lambda row : queue.enqueue(
            complex_task, job_id = row['job_id'], on_success = module.process_success, on_failure = module.process_failure
            ))

#run app as script when dockerfile runs cmd api.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

