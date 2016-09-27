Spamnesty
========

[![build status](https://gitlab.com/stavros/Spamnesty/badges/master/build.svg)](https://gitlab.com/stavros/Spamnesty/commits/master)
[![coverage report](https://gitlab.com/stavros/Spamnesty/badges/master/coverage.svg)](https://gitlab.com/stavros/Spamnesty/commits/master)

Spamnesty is an amazing service that lets you make the most delicious countdown
timers on the entire web!


Running
-------

To run Spamnesty, just clone this repository, install docker-compose and start
everything up:

~~~
pip install docker-compose
docker-compose up
~~~

If you access [http://localhost/](http://localhost/), you should see the
Spamnesty home page!

To access the admin interface, create a user:

~~~
docker-compose run web /code/manage.py createsuperuser
~~~

and go to [http://localhost/entrary/](http://localhost/entrary/) the log in.


Contributing
------------

To contribute, just issue a merge request on our repository. Make sure tests
pass first, though:

~~~
docker-compose run web /code/manage.py test
~~~
