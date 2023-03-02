from api import app
from db_interface import DB_Interface

def test_single_get_request_based_on_populate():
    '''
    Populate database and make sure that a get request
    returns all the relevent data
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
    with app.test_client() as test_client:
        response = test_client.get("/status/ABCDE")
        assert response.status_code == 200
        assert b'test_1' in response.data
        assert b'ABCDE' in response.data
        assert b'completed' in response.data
        assert b'2023-02-21 05:41:40.714896' in response.data
        assert b'2023-02-21 05:42:15.308726' in response.data
        assert b'35' in response.data
    db_interface.delete_all()

def test_single_put_request():
    '''
    Issue a simple put request and 
    make sure we get a 200 OK response
    '''
    db_interface = DB_Interface()
    with app.test_client() as test_client:
        response = test_client.put("/start/test_put")
        db_interface.delete_all()
        assert response.status_code == 200
    
    