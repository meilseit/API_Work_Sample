
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
from db_interface import DB_Interface, process_failure, process_success


#set up api and underlying flask app 
app = Flask(__name__) #init flask application
api = Api(app)        #init flask api

#set up queue and connection to redis for for async task proccess
preconfigured_timeout = 180 #set a default timeout for tasks that take long 
connection = redis.Redis(host='redis', port=6379) #start up a connection on default port 
queue = Queue('pipeline', connection=connection, default_timeout=preconfigured_timeout) #initilize queue and name it pipline


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
def abort_if_job_id_doesnt_exist(job_id, metadata):
    """
    Requires a job_id and a dataframe object from pandas.
    If job_id is not in the mock data base we cannot get meta data
    so we abort the request
    """
    if metadata is None:
        abort(404, message= "Task {} doesn't exist".format(job_id))


def abort_if_object_id_is_proccessing(object_id, metadata):
    """
    Requires a object_id and a dataframe object from pandas.
    If a second object_id is submitted matching one proccessed in 
    the last 5min we want to abort the request
    """
    if metadata is not None:
        for date in metadata['start']:
            if datetime.strptime(str(date),'%Y-%m-%d %H:%M:%S.%f') + timedelta(minutes=5) >= datetime.now():
                abort(406, message= "Object: {} is still proccessing. This action is not accepted".format(object_id))


class StartTask(Resource):
    #Set up resource class to handle put request with object_id parameters
    def put(self, object_id):
        '''
        Accepts object_id parameter
        Return message about task with job_id
        '''
        job_id = random_job_id_gen(5) #generate job_id
        db_interface = DB_Interface()
        metadata = db_interface.get_by_object_id(object_id)
        abort_if_object_id_is_proccessing(object_id, metadata)
        metadata = {
            'object_id': object_id,
            'job_id': job_id,
            'status': 'queued',
            'start': datetime.now(),
            'end': 'Pending',
            'interval': 'Pending'
        }
        db_interface.put(metadata)
        queue.enqueue(complex_task, job_id = job_id, on_success=process_success, on_failure=process_failure)
        
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
        db_interface = DB_Interface()
        metadata = db_interface.get_by_job_id(job_id)
        abort_if_job_id_doesnt_exist(job_id, metadata)
        return {
            'message': 'data retrival successful',
            'metadata': metadata
                }, 200

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
    print("Checking for interupted task and requeueing if needed.")
    db_interface = DB_Interface()
    metadata = db_interface.get_by_status("queued")
    if metadata is not None:
        for job_id in metadata['job_id']:
            queue.enqueue(complex_task, job_id = job_id, on_success=process_success, on_failure=process_failure)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

