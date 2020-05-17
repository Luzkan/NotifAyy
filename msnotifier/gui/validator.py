example_users = [
  ["aa", "bb"],
  ["bb", "cc"],
  ["cc", "dd"],
]


def data_is_valid(login: str, password: str):
    for elem in example_users:
        if login == elem[0] and password == elem[1]:
            return True
    return False


def user_exists(login: str):
    for elem in example_users:
        if login == elem[0]:
            return True
    return False


def add_new_user(login: str, password: str):
    example_users.append([login, password])
