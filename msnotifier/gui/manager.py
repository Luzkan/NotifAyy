example_users = [
  ["aa", "bb", ["Alert: Alert1, URL: http://example1.pl"]],
  ["bb", "cc", ["Alert: Alert2, URL: http://example2.pl"]],
  ["cc", "dd", ["Alert: Alert3, URL: http://example3.pl",
                "Alert: Alert4, URL: http://example4.pl"]],
]

current_user = ""


def delete_alert(login: str, index: int) -> None:
    for user in example_users:
        if login == user[0]:
            user[2].pop(index)
    return []


def add_alert(login: str, alert: str) -> None:
    for user in example_users:
        if login == user[0]:
            user[2].append(alert)
    return []


def get_current_alerts(login: str) -> list:
    for user in example_users:
        if login == user[0]:
            return user[2]
    return []


def data_is_valid(login: str, password: str) -> bool:
    for user in example_users:
        if login == user[0] and password == user[1]:
            return True
    return False


def user_exists(login: str) -> bool:
    for user in example_users:
        if login == user[0]:
            return True
    return False


def add_new_user(login: str, password: str) -> None:
    example_users.append([login, password, []])
