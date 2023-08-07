from django.core.management.base import BaseCommand
from datetime import datetime

# from dateutil.relativedelta import relativedelta

import jwt
import sys


class Command(BaseCommand):
    help = """
    Creates JWT tokens for use in authenticating requests to PostgREST
    """

    def add_arguments(self, parser):
        parser.add_argument("role", type=str)
        parser.add_argument("secret", type=str)

    def handle(self, *args, **kwargs):
        role = None
        secret = None

        if kwargs["role"] is None:
            print("You must specify a role. Exiting.")
            sys.exit(-1)
        else:
            role = kwargs["role"]

        if kwargs["secret"] is None:
            print("You must provide a secret. Exiting.")
            sys.exit(-1)
        else:
            secret = kwargs["secret"]
        # six_months = datetime.today() + relativedelta(months=+6)
        payload = {
            # PostgREST only cares about the role.
            "role": role,
            "created": datetime.today().isoformat(),
        }
        print(payload)
        encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
        print(encoded_jwt)
