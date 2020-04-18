import random
import string


def omit(my_dict: dict, keys: set):
    return {key: my_dict[key] for key in my_dict if key not in keys}


def random_str(k=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))
