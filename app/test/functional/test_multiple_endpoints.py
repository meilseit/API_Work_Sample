
import json
import time

#local imports
from api import app
from db_interface import DB_Interface


def test_put_request_object_id_collsions():
    '''
    Issue two get of the same get request in quick succession
    to make sure we complete the first and abort the second 
    because our 5 min window has not elapsed
    '''
    db_interface = DB_Interface()
    with app.test_client() as test_client:
        first_response = test_client.put("/start/collision")
        second_response = test_client.put("/start/collision")
        db_interface.delete_all()
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
    db_interface = DB_Interface()
    with app.test_client() as test_client:
        put_response = test_client.put("/start/delay") #initial put request 
        job_id = json.loads(put_response.text)['job_id'] #retrieve job_id from reponse to put request
        get_response = test_client.get("/status/{}".format(job_id)) #issue initail get request
        
        time.sleep(160) #wait for a while until we can be sure that the job is completed
        
        delayed_get_response = test_client.get("/status/{}".format(job_id)) #issue same get request 
        delayed_status = json.loads(delayed_get_response.text)["metadata"]["status"]
        assert delayed_status == 1
        db_interface.delete_all()
        assert b"Pending" in get_response.data #expect for some metadata to be pending
        assert put_response.status_code == 200 #double check that response was 200 OK
        assert delayed_status == ["completed"] #make sure status updated from queued to completed