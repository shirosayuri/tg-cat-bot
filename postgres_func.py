import os
import psycopg2
from bot import bot
import os

log_chat = os.environ['admin_chat_id']

DATABASE_URL = os.environ['DATABASE_URL']


def select_random(table, column,  condition='', limit=1):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    sql = 'SELECT {column} FROM {table} {condition} ORDER BY RANDOM() LIMIT {limit}'\
        .format(column=column,
                table=table,
                condition=' where {}'.format(condition) if condition else '',
                limit=limit)
    cur.execute(sql)
    if limit == 1:
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def select_condition(table, column, condition='', distinct=False):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    sql = 'select {distinct} {column} ' \
          'from {table}{condition}'.format(table=table,
                                           column=column,
                                           condition=' where {}'.format(condition) if condition else '',
                                           distinct='distinct' if distinct else '')
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def check_superuser(login):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    sql = "select user_role from superusers where login = '{login}'".format(login=login)
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def insert_condition(table, values, columns=''):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    values_length = '({})'.format(('%s,'*len(values))[0:-1])
    try:
        sql = 'INSERT INTO {table} {column} VALUES {values_length}'.format(table=table,
                                                                           column=columns,
                                                                           values_length=values_length)
        cur.execute(sql, values)
        conn.commit()
        result = True
    except Exception as e:
        result = False
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in postgres_func at insert_condition func'.format(e)
                         )
    cur.close()
    conn.close()
    return result


def update_condition(table, items, condition=''):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        sql = 'UPDATE {table} SET {items}{condition}'.format(table=table,
                                                             items=items,
                                                             condition=' where {} '.format(
                                                                 condition) if condition else '')
        cur.execute(sql)
        conn.commit()
        result = True
    except Exception as e:
        result = False
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in postgres_func at update_condition func'.format(e)
                         )
    cur.close()
    conn.close()
    return result


def delete_condition(table, condition):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        sql = "delete from {table} where {condition}".format(table=table, condition=condition)
        cur.execute(sql)
        conn.commit()
        result = True
    except Exception as e:
        bot.send_message(chat_id=log_chat,
                         text='Exception {} in postgres_func at delete_condition func'.format(e)
                         )
        result = False
    cur.close()
    conn.close()
    return result


