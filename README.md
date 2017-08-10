___
[![Build Status](https://travis-ci.org/Alweezy/cp2-bucketlist-api.svg?branch=develop)](https://travis-ci.org/Alweezy/cp2-bucketlist-api)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/Alweezy/cp2-bucketlist-api/badge.svg?branch=develop)](https://coveralls.io/github/Alweezy/cp2-bucketlist-api?branch=develop)
___
# cp2-bucketlist-api

A Bucket List is a list of things that one has not done
before but wants to do before dying(kicking the bucket)​.
This project is an API for an online Bucket List service created using the python framework, Flask.

___
### Prerequisites
* PostgreSQL
* Python 3.6

____
#### Installation
clone the repo:
```
$ git clone https://github.com/Alweezy/cp2-bucketlist-api.git
```
and cd into the folder:
```
$ /cp2-bucketlist-api
```
create a virtual environment for the project.
```
$ virtualenv --python=python3.6 virtualenv-name
```
and activate virtual environment
```
$ source virtualenv-name/bin/activate
```
Alternatively you can create it using virtualenvwarapper if installed:
```
$ mkvirtualenv --python=python3.6 virtualenv-name
```
> It will be automatically activated, in the future to use it just type:
```
$ workon virtualenv-name
```
Run the command `$ pip install -r requirements.txt` to install necessary libraries.

Create the database by running thr command `$ createdb flask_api`:

Handle migrations by running the following commands one after the other:

```
$ python manage.py db init
$ python manage.py db migrate
$  python manage.py db upgrade

```

### Api Endpoints
```

| Endpoint | Functionality |
| -------- | ------------- |
| POST /auth/login | Logs a user in |
| POST /auth/register | Register a user |
| POST /bucketlists/ | Create a new bucket list |
| GET /bucketlists/	| List all the created bucket lists |
| GET /bucketlists/<id> | Get single bucket list |
| PUT /bucketlists/<id> | Update this bucket list |
| DELETE /bucketlists/<id> | Delete this single bucket list |
| GET /bucketlists/<id>/items/<item_id> | Get a single bucket list item |
| POST /bucketlists/<id>/items/ | Create a new item in bucket list |
| PUT /bucketlists/<id>/items/<item_id> | Update a bucket list item |```

###Lincense
This project is licensed with the [MIT LICENCE]: https://opensource.org/licenses/MIT

