Introduction
============

ReVot is a web application focused to an agile management of
e-votings.

The author considers that for an average user any e-voting system is a
kind of blackbox he should make confidence in a blindy way due to its
complex technological nature. The more complexity we add to the system
to best guarantee the characteristics of a "good" e-voting system the
higher level of blind confidence the user should apply. At the end the
author thinks that it is better to build simpler and understandable
but robust enough systems and let the end user decide the confidence
level he gives to the system.


Install the system
------------------

1. To install the system on a GNU/Debian system first install the
   following packages:

   * virtualenv
     
   * python_dev
       
   * redis-server
       
   * subversion
	   
   * gcc

2. Create a local python environment::

     $ virtualenv env

3. Download the source code from subversion::

     $ svn export http://    revot

4. Activate the python environment and install the packages referred
   to in the file `requirements.txt`::
  
     $ . env/bin/activate
     $ pip install -r revot/requirements.txt

5. Compile the localization catalogues::

     $ cd revot/revot
     $ pybabel compile -d translations
     
    




Running the system
------------------

To run the system we need to issue two commands:

1. To start the web server, tunning the network interface and port::

     ./manage.py runserver -h 0.0.0.0 -p 5000

2. To start the celery workers, assuming that redis service is running::

     export MAIL_PASSWORD='apaswordformail'
     celery worker -A celery_worker.celery --loglevel=info



   
     
