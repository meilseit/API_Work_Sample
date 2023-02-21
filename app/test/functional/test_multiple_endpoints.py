from api import app
from unit.test_database import test_clear_database
import json
import time

def test_put_request_object_id_collsions():
    '''
    Issue two get of the same get request in quick succession
    to make sure we complete the first and abort the second 
    because our 5 min window has not elapsed
    '''
    with app.test_client() as test_client:
        first_response = test_client.put("/start/collision")
        second_response = test_client.put("/start/collision")
        test_clear_database()
        assert first_response.status_code == 200 #make sure we get a 200 OK response 
        assert second_response.status_code == 406 #ensure second request is aborted

def test_get_unknown_job_id():
    '''
    Issue a get request with an unknown id to make sure 
    the endpoint aborts the search
    '''
    with app.test_client() as test_client:
        response = test_client.get("/status/unknown")
        assert response.status_code == 404 #make sure we get an abort signal

def test_callback_function_update():
    '''
    Issue a put request followed by the same get 
    request twice with a time delay to ensure that
    the database is updating
    '''
    with app.test_client() as test_client:
        put_response = test_client.put("/start/delay") #initial put request 
        job_id = json.loads(put_response.text)['job_id'] #retrieve job_id from reponse to put request
        get_response = test_client.get("/status/{}".format(job_id)) #issue initail get request
        
        time.sleep(120) #wait for a while until we can be sure that the job is completed
        
        delayed_get_response = test_client.get("/status/{}".format(job_id)) #issue same get request 
        status = json.loads(delayed_get_response.text)["metadata"]["status"]
        test_clear_database()
        assert b"Pending" in get_response.data #expect for some metadata to be pending
        assert put_response.status_code == 200 #double check that response was 200 OK
        assert status == "completed" #make sure status updated from queued to completed