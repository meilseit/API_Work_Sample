import pandas as pd

path = './task_data.csv'

def test_clear_database():
    '''
    Simple way to override current database with an
    empty dataframe
    '''
    new_df = pd.DataFrame(columns=['object_id','job_id','status','timestamp_start','timestamp_end','sleep_time'])
    new_df.to_csv(path, index=False)
    df = pd.read_csv(path)
    assert df.empty is True #check to make sure the data frame is in fact empty



def test_populate_database():
    '''
    Make sure that database updating works.
    Then confirm the contents of the default values
    '''
    new_df = pd.DataFrame({
            'object_id': ['test_1'],
            'job_id': ['ABCDE'],
            'status': ['completed'], 
            'timestamp_start': ['2023-02-21 05:41:40.714896'],
            'timestamp_end': ['2023-02-21 05:42:15.308726'], 
            'sleep_time': ['35']
        })
    new_df.to_csv(path, index = False)
    new_df = pd.read_csv(path)
    values = (new_df.values[-1:])[0]
    
    assert len(values) == 6
    assert values[0] == 'test_1'
    assert values[1] ==  'ABCDE'
    assert values[2] == 'completed'
    assert values[3] == '2023-02-21 05:41:40.714896'
    assert values[4] == '2023-02-21 05:42:15.308726'
    assert values[5] == 35
    
    


