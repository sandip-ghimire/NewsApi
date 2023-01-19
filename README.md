### Application overview
An application backend to provide api for finding news from various sources based on different criteria.
It supports following operations:
- Managing channels
- Finding news articles based on channels or news source
- Saving the news with word count
- Filtering the saved news articles on the basis of word counts

An easy to use **Swagger UI** *(/doc/)* and **Redoc** *(/redoc/)* documentations embedded. <br />
Basic tests for all endpoints included.

### Running the application (Production like environment)
##### Requirements
- For running the application in docker container, **Docker** needs to be installed in the system if not already installed. Please follow the instruction for the installation: https://docs.docker.com/get-docker/

- Clone the project repo: git clone https://github.com/sandip-ghimire/NewsApi

##### Steps
- Open the command line from the root directory of the project, i.e. the path where Dockerfile is located.  Build the docker image with the command:
  >docker build -t newsfinder .

- Add the api key in app.env file and run the docker container with the command below: <br />
  >docker run --name=newsfinder-container --env-file app.env -d -p 8005:8005 newsfinder

  *(The application runs on port 8005)* <br />
  The swagger ui can be accessed at: <br />
  *http://localhost:8005/doc/* <br />
  Redoc can be accessed at: <br />
  *http://localhost:8005/redoc/* <br />

### Testing the application (Production like environment)
###### Unit Test
- While the application is running, it can be tested using unit test. Command for unit test:
  >docker exec -it newsfinder-container ./manage.py test
  - The output should be 'OK' if the test is successful.  

### Running the application (For debug in local machine - in windows)
##### Requirements
- Clone the project repo: git clone https://github.com/sandip-ghimire/NewsApi

##### Steps
- Set DEBUG=True in settings.py located inside newsfinder directory.
- Open the command line from the root directory of the project (NewsApi) and create virtual env:
  >python -m venv venv
- Activate virtual env:
  >venv\Scripts\activate
- Install dependencies:
  >pip install -r requirements.txt
- Make migrations:
  >python manage.py makemigrations newsfinder
- Migrate databases:
  >python manage.py migrate
- Runserver at port 8005:
  >python manage.py runserver 0.0.0.0:8005

  *(The application runs on port 8005)* <br />
