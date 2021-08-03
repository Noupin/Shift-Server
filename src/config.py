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
from typing import Dict, List
from dotenv import load_dotenv
from apispec.ext.marshmallow import MarshmallowPlugin

#First Party Imports
from src.utils.ObjectIdConverter import ObjectIdConverter
from src.variables.constants import (ACCESS_EXPIRES, CELERY_RESULT_BACKEND,
                                     USER_CSRF_REFRESH_SCHEME, USER_REFRESH_TOKEN_COOKIE_SCHEME)


FERYV_DB_ALIAS = 'feryv'
SHIFT_DB_ALIAS = 'shift'

load_dotenv()
marshmallowPlugin = MarshmallowPlugin()

class Config:
    #JWT
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False #Should always be set to true in production.
    JWT_SECRET_KEY = open('keys/jwt-key').read()
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_REFRESH_COOKIE_NAME = USER_REFRESH_TOKEN_COOKIE_SCHEME.get('name')
    JWT_REFRESH_CSRF_COOKIE_NAME = USER_CSRF_REFRESH_SCHEME.get('name')

    #MongoDB
    MONGODB_SETTINGS: List[Dict[str, str]] = [
        {
            'ALIAS': SHIFT_DB_ALIAS,
            'DB': os.environ.get('DB_PROJECT'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': int(os.environ.get('DB_PORT'))
        },
        {
            'ALIAS': FERYV_DB_ALIAS,
            'DB': os.environ.get('FERYV_DB_PROJECT'),
            'HOST': os.environ.get('FERYV_DB_HOST'),
            'PORT': int(os.environ.get('FERYV_DB_PORT'))
        }
    ]
    OBJECTID = ObjectIdConverter

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
    
    #Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
