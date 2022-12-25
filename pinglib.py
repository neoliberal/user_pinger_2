"""Common functions for the various user_pinger services"""

import string

def group_name_is_valid(group_name):
    """Return bool indicating whether group name is valid"""
    # TODO add emoji?
    if group_name == "":
        return False
    valid_group_characters = string.ascii_uppercase + string.digits + "-"
    if set(group_name) - set(valid_group_characters):
        return False
    return True
