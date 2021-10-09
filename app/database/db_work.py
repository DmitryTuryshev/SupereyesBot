import sqlite3

conn = sqlite3.connect("app/database/dbBirthday.db")
cursor = conn.cursor()


def add_user(id, name, birthday, hidden=False):
    sql = "insert into users (name, id_tel, birthday, hidden_year)" \
          "values (?,?,?,?)"
    cursor.execute(sql, [name, id, birthday, hidden])
    conn.commit()


def get_book(id):
    sql = f"select * from books where id_book={id}"
    cursor.execute(sql)
    return cursor.fetchone()


def get_user(id):
    sql = f"select * from users where id_tel='{id}'"
    return cursor.execute(sql).fetchone()


def get_users(access=1):
    sql = f"select * from users where role<>'s_admin' and access={access}"
    return cursor.execute(sql).fetchall()


def get_users_by_notification(notification=1):
    sql = f"select * from users where role<>'s_admin' and notification={notification}"
    return cursor.execute(sql).fetchall()


def add_book(id, name, author, priority):
    sql = "insert into books (name_book, author, id_user, priority)" \
          "values(?,?,?,?)"
    cursor.execute(sql, [name, author, id, priority])
    conn.commit()


def get_books_by_user(id, status="active"):
    sql = f"select * from books where id_user='{id}' and status='{status}' order by priority"
    return cursor.execute(sql).fetchall()


def get_books_by_user_all(id):
    sql = f"select * from books where id_user='{id}' and status<>'remove' order by priority"
    return cursor.execute(sql).fetchall()


def remove_book_by_id(id):
    sql = f"update books set status='remove' where id_book = {id}"
    cursor.execute(sql)
    conn.commit()


def change_status_book_by_id(id, status="present"):
    sql = f"update books set status='{status}' where id_book = {id}"
    cursor.execute(sql)
    conn.commit()


def change_name(id, name):
    sql = f"update books set name_book='{name}' where id_book={id}"
    cursor.execute(sql)
    conn.commit()


def change_author_book(id, name):
    sql = f"update books set author='{name}' where id_book={id}"
    cursor.execute(sql)
    conn.commit()


def get_users_by_cur_date(before_notification=31):
    sql = f"select * from users where (role<>'s_admin' and access=1) and (" \
          f"((julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-julianday(date('now')) <{before_notification} " \
          f"and julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-julianday(date('now'))>-1)) " \
          f"or (julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-(julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', '2021-01-01')))" \
          f" +(julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', '2021-12-31'))-julianday(date('now'))))<{before_notification}+1);"
    cursor.execute(sql)
    return cursor.fetchall()


def get_users_by_cur_date_n(before_notification=31):
    sql = f"select * from users where ((role<>'s_admin' and access=1) and (" \
          f"((julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-julianday(date('now')) <{before_notification} " \
          f"and julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-julianday(date('now'))>-1)) " \
          f"or (julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', birthday))-(julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', '2021-01-01')))" \
          f" +(julianday(strftime(strftime('%Y', date('now'))||'-%m-%d', '2021-12-31'))-julianday(date('now'))))<{before_notification}+1)) and julianday(date('now'))-julianday(date_last_notification)>{before_notification};"
    cursor.execute(sql)
    return cursor.fetchall()


def set_last_notification_date(id):
    sql = f"update users set date_last_notification=CURRENT_DATE where id_tel='{id}'"
    cursor.execute(sql)
    conn.commit()


def change_priority_book(id, priority):
    sql = f"update books set priority='{priority}' where id_book={id}"
    cursor.execute(sql)
    conn.commit()


def block_user(id, access=0):
    sql = f"update users set access={access} where id_tel='{id}'"
    cursor.execute(sql)
    conn.commit()


def change_per(id, role="worker"):
    sql = f"update users set role='{role}' where id_tel={id}"
    cursor.execute(sql)
    conn.commit()


def change_notification(id, notification=1):
    sql = f"update users set notification={notification} where id_tel={id}"
    cursor.execute(sql)
    conn.commit()
