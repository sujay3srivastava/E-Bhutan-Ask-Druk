# wsgi.py for Ask Druk - Bhutan's AI Citizen Assistant
from application import app

# WSGI application object that Elastic Beanstalk will use
application = app

if __name__ == "__main__":
    application.run()
