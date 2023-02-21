from api import app
from unit.test_database import test_clear_database, test_populate_database

def test_single_get_request_based_on_populate():
    '''
    Populate database and make sure that a get request
    returns all the relevent data
    '''
    test_populate_database() #use unit test to populate database
    with app.test_client() as test_client:
        response = test_client.get("/status/ABCDE")
        test_clear_database() #clear data from database after test 
        assert response.status_code == 200
        assert b'test_1' in response.data
        assert b'ABCDE' in response.data
        assert b'completed' in response.data
        assert b'2023-02-21 05:41:40.714896' in response.data
        assert b'2023-02-21 05:42:15.308726' in response.data
        assert b'35' in response.data


def test_single_put_request():
    '''
    Issue a simple put request and 
    make sure we get a 200 OK response
    '''
    with app.test_client() as test_client:
        response = test_client.put("/start/test_put")
        test_clear_database() #clear database when finished
        assert response.status_code == 200
    
    