Tasks
---------------------------

# Description

Tasks is a website and an API application that provides an overview and data about all the tasks set with their current status.
The Website part has two simple pages
1- An Index which shows a summary of the tasks.
2- A table listing all the task details. Every task has an ID, when pressing the ID button, the name of the Owner and the Priority.

Each task has 7 attributes and 2 properties.
the attributes of the task are:
1- id
2- name
3- owner
4- start date
5- end date
6- priority
7- parent task

the task properties are:
1- status
2- the duration

The status is calculated based on the start and end time of the task / subtasks.
The duration is the number of minutes from the start to the end of a task.

Both properties are calculated in the models, but they could have been set in the view.

To add or modify a task, the admin page is available to do so.
you can go to the browser and to the webserver http://127.0.0.1:8000/admin . Login with a test account I created, username 'admin' and pass 'test1234' .

The API part only accept a GET request with the TaskID provided, It returns the Owner's first and last name with the Priority. 

# Requirements

1. python3
2. bootstrap v4
3. jquery v3

# Installation

from the command line execute the following commands.
1. `virtualenv -p python3.6 tasks`. This will create a virtual environment inside the new created folder
   tasks with python3.6 version.
2. `cd tasks; source bin/activate`. change directory and activate the virtual environment.

3.A get project through git

3.A.1. `git clone https://github.com/omaraljazairy/tasks`  this will clone the project.
3.A.2. `cd tasks`. change the directory to be in the main folder.

3.B get project through the attached compressed folder Tasks-1.0.tar.gz

3.B.1. `tar -zxf Tasks-1.0.tar.gz` uncompress the file Tasks-1.0.tar.gz downloaded from the attachment with this command.
3.B.2. `cd Tasks-1.0` . change the directory to be in the main folder.

4. `python setup.py install`. this will setup the the application and install all the requirements.
5. `cd webtasks` move to the main project folder.
6. `python manage runserver 8000` to run the webserver of the application. when it starts, it will show the server url example: http://127.0.0.1:8000/ .

# Usage

A. Website

To use the website application open your browser and go to the address shown when the webserver started. example for this case http://127.0.0.1:8000/ .*
This will show you the main index page with two menu items. Home and Task Details. 

B. API
B.1. To make requests to the API, you can make a GET request to the http://127.0.0.1:8000/tasks/task/ API and append the id of any task. So if you have taskid 3, the call will be curl "http://127.0.0.1:8000/tasks/task/3/". this will return a json response back with the task_priority, owner's first_name and owner's last_name.
example response: {"task_priority":"H","first_name":"foo","last_name":"bar"}

B.2. If the taskId doesn't exist, it will return the http statuscode 404 Not Found response.

C. If you intend to modify the application and want to distribute it, you will need to adjust the setup.py file by mainly changing the version number and packages if you add any. If you add non python files, you can add them in the MANIFEST.in file.
   when done, you can execute the following command to create a compressed application files: `python setup.py sdist`. This will create the file in the dist folder.

D. The admin page is available http://127.0.0.1:8000/admin . you can use the admin user 'admin' and password 'test1234' to login.

   
# Troubleshooting

- In the case of have issues with pip downloading and installing packages with error related to cerificates like "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:777) -- Some packages may not be found!", you can run the following command manually: `pip install certifi`. 

- If the python interpreter doesn't find any required package, make sure `python` command is using the correct interpreter in the virtual environment. you can check it with the command `which python`. This will return you back the location of the python interpreter. 

- If you try to view the website or make call to the api and get the http status 400 (Bad Request), then you need to add your ipaddress to the settings.py file in the ALLOWED_HOST list. Currently I added the default 127.0.0.1 localhost.  

# Unit testing

The application is unit tested using the django-nose module. The tests are located in the webtasks/tests folder. The setting.py in the test folder needs to be used with the test.
example of executing the unit tests: `python manage.py test --settings=tests.settings`
There is also the html coverage folder which holds all the html coverage report.
The report will also export xml files needs for the Jenkins coverage.
