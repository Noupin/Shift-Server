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
from src.utils.ObjectIdConverter import ObjectIdConverter
from src.variables.constants import SERVER_URL, SERVER_PORT


FERYV_DB_ALIAS = 'feryv'
SHIFT_DB_ALIAS = 'shift'

load_dotenv()
marshmallowPlugin = MarshmallowPlugin()

class Config:
    SECRET_KEY = open('keys/jwt-key').read()

    #MongoDB
    MONGO_URI = f"mongodb://{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_PROJECT')}"
    MONGODB_SETTINGS = [
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
    CELERY_RESULT_BACKEND = "mongodb://localhost:27017"
    
    #OpenAPI
    OPENAPI_SPEC = f"""
    info:
        description: Shift Server API documentation
    host: {SERVER_URL}
    """
    APISPEC_SPEC = APISpec(
        title='Shift',
        version='1.0.0',
        plugins=[marshmallowPlugin],
        openapi_version='2.0',
        **yaml.safe_load(OPENAPI_SPEC)
    )
    APISPEC_SWAGGER_URL = '/swagger/'  # URI to access API Doc JSON 
    APISPEC_SWAGGER_UI_URL = '/swagger-ui/'  # URI to access UI of API Doc
