# USSD-Python-Demo

A project to demonstrate using Africas Talking USSD, Payments and Call APIs

This is just a demo of the basic features provided by these awesome APIs.

For a deeper understanding on what the APIs can do; head over to the AT website,

better still look at the code :-)


# INSTALLATION AND GUIDE

# requirements

    Python version 2.* 
    AfricastalkingGateway==1.6
    alembic==0.9.1
    click==6.7
    dominate==2.3.1
    Flask==0.12
    Flask-Bootstrap==3.3.7.1
    Flask-Migrate==2.0.3
    Flask-Script==2.0.5
    Flask-SQLAlchemy==2.2
    Flask-SSLify==0.1.5
    itsdangerous==0.24
    Jinja2==2.9.5
    Mako==1.0.6
    MarkupSafe==1.0
    migrate==0.3.8
    python-editor==1.0.3
    requests==2.13.0
    SQLAlchemy==1.1.6
    visitor==0.1.3
    Werkzeug==0.12.1

-> The project is currently not compatible with future python version
-> Recommendend running the project in a virtual environment

# installation
   
1. clone/download the project into the directory of your choice

2. On the project's root directory

          $ makevirtualenv microfinance            # creates a virtual environment
          $ source microfinace/bin/activate        # start the virtual environment
          $ pip install requirements.txt           # download and install project's dependancies
          $ python manage.py runserver             # starts project


## worth noting

You would want to tunnel your using through Ngrok, for sandboxing purposes.

   Head over to the virtual environment and Ngrok sites to learn more about using the tools
   