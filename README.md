# API_Work_Sample
### Brief Description:
Created A simple API test peice with Python Flask and Flask-Restful libraries. Used Redis to host queues and workers to preform mock time intensive tasks outside of the API. This async behavior make the API not only much more efficient at handling many request but also ensures TCP connections do not stay open for too long. I decided to use a simple csv to presist the metadata seeing as this was smaller project. The app is split into 3 docker containers: flask-app, redis, worker. The project also supports e2e testing.

### Relevent Commands:
docker setup: [easiest way for me to get this running on docker desktop]
```
docker-compose build --no-cache  
docker-compose up -d
```
test setup: [this can be run in the docker flask-app container to execute test cases]
```
python -m pytest OPTIONAL[SPECIFIC TEST FOLDERS]
```
Most of my addtional testing was done with CURL commands in the flask-app container terminal since I was having trouble getting Postman API Software to communicate well
