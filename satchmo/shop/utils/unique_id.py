"""
Create a unique user id given a first and last name.
First, we try simple concatenation of first and last name.
If that doesn't work, we add random numbers to the name
"""

from django.contrib.auth.models import User
import random

def generate_id(first_name=None, last_name=None):
    valid_id = False
    test_name = first_name + last_name
    while valid_id is False:
        try:
            User.objects.get(username=test_name)
        except User.DoesNotExist:
            valid_id = True
        else:
            test_name = first_name + last_name + str(random.randrange(1,9999))
    return(test_name)
