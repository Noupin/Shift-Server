#pylint: disable=C0103, C0301, R0903, E1101
"""
The configuration variables for the Shift server
"""
__author__ = "Noupin"

#Third Party Imports
import os
import yaml
import datetime
from apispec import APISpec
from dotenv import load_dotenv
from apispec.ext.marshmallow import MarshmallowPlugin

#First Party Imports
from src.constants import CELERY_RESULT_BACKEND


load_dotenv()
marshmallowPlugin = MarshmallowPlugin()

class Config:
    #JWT
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False #Should always be set to true in production.
    JWT_SECRET_KEY = open(f"{os.path.join(os.pardir, os.pardir, 'keys', 'jwt.key')}").read()
    

    #SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True


    #Authentication
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=5)
    SEND_FILE_MAX_AGE_DEFAULT = 0


    #Celery
    CELERY_BROKER_URL = "amqp://localhost//"
    result_backend = CELERY_RESULT_BACKEND
    timezone = 'UTC'


    #OpenAPI
    OPENAPI_SPEC = f"""
    info:
        description: Shift Server API documentation
    host: \\
    schemes:
        - http
        - https
    """
    APISPEC_SPEC = APISpec(
        title='Shift',
        version='1.0.0',
        plugins=[marshmallowPlugin],
        openapi_version='2.0',
        **yaml.safe_load(OPENAPI_SPEC)
    )
    APISPEC_SWAGGER_URL = '/api/oas/'  # URI to access API Doc JSON 
    APISPEC_SWAGGER_UI_URL = '/api/oasUI/'  # URI to access UI of API Doc


    #Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID')    
