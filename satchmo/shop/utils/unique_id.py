"""
Create a unique user id given a first and last name.
First, we try simple concatenation of first and last name.
If that doesn't work, we add random numbers to the name
"""

from django.contrib.auth.models import User
from satchmo.shop.utils import random_string

def generate_id(first_name=None, last_name=None):
    valid_id = False
    test_name = first_name + last_name
    while valid_id is False:
        try:
            User.objects.get(username=test_name)
        except User.DoesNotExist:
            valid_id = True
        else:
            test_name = first_name + last_name + "_" + random_string(7, True)
    return(test_name)
