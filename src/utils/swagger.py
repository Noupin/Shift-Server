#pylint: disable=C0103, C0301
"""
API swagger helpers
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from apispec import APISpec


def swaggerToYAML(spec: APISpec, filename="shift.yaml",
                  path=os.path.join(os.getcwd(), os.pardir,
                                    "Shift Webapp", "Client", "OpenAPI")) -> None:
    """
    Generates the YAML for the api from the swagger documetation and saves to filename.

    Args:
        spec (APISpec): The spec to get the YAMl from.
        filename (str, optional): The file to save the yaml to. Defaults to "shift.yaml".
        path (str, optional): The path to save the YAML file to. Defaults to the OpenAPI \
            folder of Shift Webapp.
    """

    with open(os.path.join(path, filename), 'w') as swaggerFile:
        swaggerFile.write(spec.to_yaml())


def swaggerToJSON(spec: APISpec, filename="shift.json",
                  path=os.path.join(os.getcwd(), os.pardir,
                                    "Shift Webapp", "Client", "OpenAPI")) -> None:
    """
    Generates the JSON for the api from the swagger documetation and saves to filename.

    Args:
        spec (APISpec): The spec to get the JSON from.
        filename (str, optional): The file to save the yaml to. Defaults to "shift.yaml".
        path (str, optional): The path to save the YAML file to. Defaults to the OpenAPI \
            folder of Shift Webapp.
    """

    with open(os.path.join(path, filename), 'w') as swaggerFile:
        json.dump(spec.to_dict(), swaggerFile)
