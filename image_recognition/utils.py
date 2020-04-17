def omit(my_dict: dict, keys: set):
    return {key: my_dict[key] for key in my_dict if key not in keys}
