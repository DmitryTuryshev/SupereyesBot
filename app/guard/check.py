from app.database.db_work import get_user


def check_access(id):
    user = get_user(id)
    if user is not None:
        if not user[3]:
            return False

    return True


def check_permision(id):
    user = get_user(id)
    if user is not None:
        if user[2] == 'admin' or user[2] == 's_admin':
            return True
    return False


def check_reg(id):
    user = get_user(id)
    if user is None:
        return False
    return True


def check(id):
    if not check_reg(id):
        answer = 'Вы не зарегистрированы.\n\n' \
                 'Для регистрации: /reg\n' \
                 'Меню: /cancel'
        return answer
    if not check_access(id):
        answer = 'У вас нет доступа\n\n' \
                 'Меню: /cancel'
        return answer
    if not check_permision(id):
        answer = 'У вас нет на это прав\n\n' \
                 'Меню: /cancel'
        return answer
    return False
