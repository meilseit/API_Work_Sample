import pandas as pd 
from datetime import datetime

class DB_Interface():
    path = './task_data.csv'

    def get_by_job_id(self, job_id):
        df = pd.read_csv(self.path)
        data = df.loc[df['job_id'] == job_id]
        if data.empty:
            return None
        metadata = {
            'object_id':data['object_id'].to_list(),
            'job_id':data['job_id'].to_list(),
            'status':data['status'].to_list(),
            'start':data['timestamp_start'].to_list(),
            'end':data['timestamp_end'].to_list(),
            'interval':data['sleep_time'].to_list()
        }
        return metadata
    
    def get_by_object_id(self, object_id):
        df = pd.read_csv(self.path)
        data = df.loc[df['object_id'] == object_id]
        metadata = {
            'object_id':data['job_id'].to_list(),
            'job_id':data['object_id'].to_list(),
            'status':data['status'].to_list(),
            'start':data['timestamp_start'].to_list(),
            'end':data['timestamp_end'].to_list(),
            'interval':data['sleep_time'].to_list()
        }
        return metadata
    
    def get_by_status(self, status):
        df = pd.read_csv(self.path)
        data = df.loc[df['status'] == status]
        metadata = {
            'object_id':data['job_id'].to_list(),
            'job_id':data['object_id'].to_list(),
            'status':data['status'].to_list(),
            'start':data['timestamp_start'].to_list(),
            'end':data['timestamp_end'].to_list(),
            'interval':data['sleep_time'].to_list()
        }
        return metadata

    def put(self, metadata):
        df = pd.read_csv(self.path) #read in current data
        new_df = pd.DataFrame({
            'object_id': [metadata['object_id']],
            'job_id': [metadata['job_id']],
            'status': [metadata['status']], 
            'timestamp_start': [metadata['start']],
            'timestamp_end': [metadata['end']], 
            'sleep_time': [metadata['interval']]
        })
        new_df.astype(str) #ensure all csv entries will be strings
        df = pd.concat([df, new_df]) #add new dataframe to exsisting dataframe
        df.to_csv(self.path, index=False) #save appended data back to mock database

    def delete():
        pass

    def delete_all(self):
        new_df = pd.DataFrame(columns=['object_id','job_id','status','timestamp_start','timestamp_end','sleep_time'])
        new_df.to_csv(self.path, index=False)
        df = pd.read_csv(self.path)
        return df

    def callback_update(self, status, job):
        df = pd.read_csv(self.path)
        df.loc[df['job_id'] == job.id, ['timestamp_end','status', 'sleep_time']] = [datetime.now(), status, job.result]
        df.to_csv(self.path, index=False) #save data to storage





#set up callback functions to execute when task is completed
def process_success(job, connection, result, *args, **kwargs):
    '''
    Requires all the default parameters above based on the documentation
    This function connects to the mock data base to update 
    timestamp_end, status, and result based on exacution results
    '''
    db_conn = DB_Interface()
    db_conn.callback_update("completed", job)

    
def process_failure(job, connection, result, *args, **kwargs):
    '''
    Requires all the default parameters above based on the documentation
    This function connects to the mock data base to update 
    timestamp_end, status, and result based on exacution results
    '''
    db_conn = DB_Interface()
    db_conn.callback_update("failed", job)

    
