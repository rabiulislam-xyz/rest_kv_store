### Simple restful key value store using *django*


**Build and run with docker**
 
if you have docker and docker-compose installed on your machine, just clone this repo, cd into it and enter `sudo docker-compose up` in the terminal.
it may take a few minutes to download and build Docker images, based on your internet speed and previous downloaded images.

**Build and run manually**

To run this project manually, here are the steps:
- clone this repo and cd into it
- (optional) create a virtual environment and activate
- install python packages from requirements.txt
- enter command `python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000`
- (optional) to delete expired data periodically, install and run redis, celery, and celery beat! 


after successfully run the server, you can **get**, **create** and **update** Key/Values on [http://0.0.0.0:8000/values](http://0.0.0.0:8000/values "`http://0.0.0.0:8000/values`")


**Test**

Enter `python3 manage.py test` command in terminal for testing.