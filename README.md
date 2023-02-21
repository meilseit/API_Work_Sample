# API_Work_Sample
### Brief Description:
Created A simple API with Python Flask and Flask-Restful libraries while using Redis to host queues and workers to preform time intensive tasks outside of the API. I decided to use a simple csv to presist the metadata seeing as this was smaller project (big mistake) should have just commited to SQL. Even so everthing should be running smoothly  and the csv makes it very easy to check if data is being stored correctly! The app is split into 3 docker containers: flask-app, redis, worker. 

### Relevent Commands:
docker setup: [easiest way for me to get this running on docker desktop]
'''
docker-compose build --no-cache  
docker-compose up -d
'''
test setup: [this can be run in the docker flask-app container to execute test cases]
'''
python -m pytest OPTIONAL[SPECIFIC TEST FOLDERS]
'''
Most of my addtional testing was done with CURL commands in the flask-app container terminal since I was having trouble getting Postman API Software to communicate well
