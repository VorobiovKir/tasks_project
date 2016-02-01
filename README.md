# CRUD TEST by Vorobiov Kyrylo

Mini project on Django 1.9 with jQuery library. This project allows you:

  - View List Leads
  - Create/Update Lead
  - Delete one or more Lead(s)

### Version
1.0 (Beta)

### Tech

Dillinger uses a number of open source projects to work properly:

* [Django] - great Python framework for web apps!
* [Twitter Bootstrap] - great UI boilerplate for modern web apps
* [jQuery] - duh

### Installation

You need Virtualenv, PIP installed globally:

```sh
$ [sudo] pip install virtualenv
$ [sudo] pip install -U pip
```
Next:
```sh
$ git clone https://github.com/VorobiovKir/crud.git
$ cd crud
$ virtualenv .virtenv
$ source .virtenv/bin/activate
$ pip install -r requirements.txt
$ cd project
$ python manage.py migrate
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

### Plugins

Crud is currently extended with the following plugins

* Virtualenv
* Github
* Pip

License
----

&copy; 2016 Vorobiov Kir


**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Django]: <https://www.djangoproject.com/>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>


