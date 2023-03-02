from db_interface import DB_Interface



def test_clear_database():
    '''
    Simple way to override current database with an
    empty dataframe
    '''
    db_interface = DB_Interface()
    db_contents = db_interface.delete_all()
    assert db_contents.empty




def test_populate_database():
    '''
    Make sure that database updating works.
    Then confirm the contents of the default values
    '''
    metadata = {
            'object_id': 'test_1',
            'job_id': 'ABCDE',
            'status': 'completed',
            'start': '2023-02-21 05:41:40.714896',
            'end': '2023-02-21 05:42:15.308726',
            'interval': '35'
        }
    db_interface = DB_Interface()
    db_interface.put(metadata)
    db_content = db_interface.get_by_job_id('ABCDE')
    assert metadata['object_id'] in db_content['object_id']
    assert metadata['job_id'] in db_content['job_id']
    assert metadata['status'] in db_content['status']
    assert metadata['start'] in db_content['start']
    assert metadata['end'] in db_content['end']
    assert int(metadata['interval']) in db_content['interval']






    
    
    


