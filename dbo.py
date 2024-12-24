import datetime

import pymysql
import pandas as pd


def douban_connect():  # 连接数据库
    # 返回数据库连接的对象 con，调用需要手动关闭连接
    con = pymysql.Connect(
        # host='192.168.14.129',
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='qc010419qc',
        db='douban',
        charset='utf8')
    return con


def query(sql: str):  # 执行任何 sql 查询
    con = douban_connect()
    cursor = con.cursor()
    try:
        cursor.execute(sql)
        con.commit()
    except Exception:
        con.rollback()
        print("发生异常", Exception)
        print(sql)
    con.close()


def get_user(username: str) -> dict:  # 获取单个用户信息
    # 参数为用户名，返回包含用户信息的字典
    # 字典第一个元素 row 为 0 表示未查询到用户
    # 字典第一个元素 row 为 1 表示查询到用户
    # 返回示例：{'row': 1, 'uname': 'admin', 'email': 'admin@db.com', 'passwd': '123456'}
    user = {'row': 0, 'uname': '', 'email': '', 'passwd': '', 'viewed': '', 'collection': '', 'love': '', 'like': ''}
    con = douban_connect()
    cursor = con.cursor()
    # uname, email, passwd, viewed, collection, love, likes
    sql = "SELECT * FROM `user_list` WHERE BINARY `uname` = '%s';" % (username)
    cursor.execute(sql)
    row = cursor.rowcount  # 获取的行数
    if row == 1:
        result = cursor.fetchone()  # 返回元组
        user['row'] = row
        user['uname'] = result[0]
        user['email'] = result[1]
        user['passwd'] = result[2]
        user['viewed'] = result[3]
        user['collection'] = result[4]
        user['love'] = result[5]
        user['like'] = result[6]
    con.close()
    return user


def get_users() -> tuple:  # 获取用户列表
    # 无参，返回包含所有用户信息的集合 ()
    # 返回值示例：(('admin', 'admin@db.com', '123456'),)
    con = douban_connect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM `user_list`")
    users = cursor.fetchall()
    con.close()
    return users

def get_collection(username) ->tuple: # 获取用户收藏的列表
    # 输入：用户名
    # 返回值：收藏列表
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT collection FROM user_list WHERE uname = '%s'" % (username)
    cursor.execute(sql)
    result = cursor.fetchone()  # 返回元组
    con.close()
    return result

def get_likes(username) -> tuple:  # 获取用户点赞的列表
    # 输入：用户名
    # 返回值：点赞列表
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT likes FROM user_list WHERE uname = '%s'" % (username)
    cursor.execute(sql)
    result = cursor.fetchone()  # 返回元组
    con.close()
    return result

def update_collection(collection_str: str, username: str):
    """
    更新收藏字段
    :param collection_str: 收藏字符串
    :param username: 用户名
    :return:
    """
    msg = {'result': False, 'info': ''}
    try:

        # 创建连接
        con = douban_connect()
        # 创建游标对象
        cursor = con.cursor()
        # 构建sql
        sql = ("UPDATE user_list "
               "SET collection = %s "
               "WHERE uname = %s")
        # 执行插入操作
        cursor.execute(sql, (collection_str, username))

        # 提交事务
        con.commit()

        # 这是注册成功信息
        msg["result"] = True
        msg["info"] = '更新成功'
    except pymysql.connect.Error as err:
        msg["info"] = f'更新失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    return msg

def update_likes(likes_str: str, username: str):  # 跟新
    # 参数为喜欢的字符串
    # 注册成功 result = True, info = '注册成功'
    # 注册失败 result = Flase, info = '注册失败'
    msg = {'result': False, 'info': ''}
    try:

        # 创建连接
        con = douban_connect()
        # 创建游标对象
        cursor = con.cursor()
        # 构建sql
        sql = ("UPDATE user_list "
               "SET likes = %s "
               "WHERE uname = %s")
        # 执行插入操作
        cursor.execute(sql, (likes_str, username))

        # 提交事务
        con.commit()

        # 这是注册成功信息
        msg["result"] = True
        msg["info"] = '更新成功'
    except pymysql.connect.Error as err:
        msg["info"] = f'更新失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    return msg


def user_login(username: str, password: str) -> dict:  # 登陆校验函数
    # 参数为用户名，返回包含登陆结果信息的字典
    # 登陆成功：result = True，info = '登陆成功'
    # 登陆失败：result = False，info = '用户不存在' / '密码不正确'
    msg = {'result': False, 'info': ''}
    user = get_user(username)
    if user['row'] == 1:
        if user['passwd'] == password:
            msg = {'result': True, 'info': '登陆成功'}
        else:
            msg = {'result': False, 'info': '密码不正确'}
    else:
        msg = {'result': False, 'info': '用户不存在'}
    return msg


def user_register(username: str, password: str, email: str):  # 注册函数
    # 参数为用户名及密码，返回包含注册结果信息的字典
    # 注册成功 result = True, info = '注册成功'
    # 注册失败 result = Flase, info = '注册失败'
    msg = {'result': False, 'info': ''}
    try:

        # 创建连接
        con = douban_connect()
        # 创建游标对象
        cursor = con.cursor()
        # 构建sql
        sql = ("INSERT INTO user_list"
               "(uname, passwd, email, viewed, collection, love, likes)"
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        # 执行插入操作
        cursor.execute(sql,
                       (username, password, email, 'QlETwuKmIfEQPyzW', 'QlETwuKmIfEQPyzW', '喜剧', 'QlETwuKmIfEQPyzW'))

        # 提交事务
        con.commit()

        # 这是注册成功信息
        msg["result"] = True
        msg["info"] = '注册成功'
    except pymysql.connect.Error as err:
        msg["info"] = f'注册失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    return msg


def user_forget(username: str, password: str, email: str):  # 注册函数
    # 参数为用户名及密码，返回包含注册结果信息的字典
    # 注册成功 result = True, info = '注册成功'
    # 注册失败 result = Flase, info = '注册失败'
    msg = {'result': False, 'info': ''}
    try:

        # 创建连接
        con = douban_connect()
        # 创建游标对象
        cursor = con.cursor()

        # 构建修改密码sql
        sql = ("UPDATE user_list "
               "SET passwd = %s "
               "WHERE email = %s AND uname = %s")
        # 执行插入操作
        cursor.execute(sql, (password, email, username))

        if cursor.rowcount > 0:
            # 提交事务
            con.commit()

            # 这是注册成功信息
            msg["result"] = True
            msg["info"] = '密码更新成功'
        else:
            msg['info'] = '未找到匹配的用户记录'
    except pymysql.connect.Error as err:
        msg["info"] = f'密码更新失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    return msg


def user_modify(username: str, operation: dict):
    # 参数为用户名及操作字典，返回包含注册结果信息的字典
    # 注册成功 result = True, info = '注册成功'
    # 注册失败 result = Flase, info = '注册失败'
    msg = {'result': False, 'info': ''}
    try:
        # 创建连接
        con = douban_connect()
        # 创建游标对象
        cursor = con.cursor()

        # 构建修改密码sql
        sql = "UPDATE user_list SET "
        update_key = []
        update_value = []
        # 根据operation执行修改操作
        for key, value in operation.items():
            update_key.append(f'{key} = %s')
            update_value.append(value)

        sql += ', '.join(update_key)
        sql += ' WHERE uname = %s'
        print(sql)
        update_value.append(username)
        print(tuple(update_value))
        # 执行插入操作
        cursor.execute(sql, tuple(update_value))

        if cursor.rowcount > 0:
            # 提交事务
            con.commit()

            # 这是注册成功信息
            msg["result"] = True
            msg["info"] = '信息更新成功'
        else:
            msg['info'] = '未找到匹配的用户记录'
    except pymysql.connect.Error as err:
        msg["info"] = f'信息更新失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
    return msg


def get_film(subject: str) -> tuple:  # 获取单部电影的信息
    # 参数为 subject，返回包含单部电影信息的元组
    # 查询到则返回电影信息，未查询到返回空元组
    con = douban_connect()
    cursor = con.cursor()
    # print('subject ' + subject)
    sql = "SELECT * FROM film_list WHERE subject = '%s'" % (subject)
    cursor.execute(sql)
    result = cursor.fetchone()  # 返回元组
    con.close()
    return result


def get_all_films(like: str) -> tuple:  # 按分类获取分类下全部电影列表信息
    if like == '':  # 如果筛选值为空，则匹配全部
        like = '%'
    else:
        like = '%' + like + '%'
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT * FROM `film_list` WHERE `classification` LIKE '%s';" % (
        like)
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result


def get_films(like: str, sort: str, page: int) -> tuple:  # 按分类分页获取电影列表信息
    # 参数为：筛选值，排序规则(ASC:升序，DESC:降序)，页号
    # 返回包含一组电影信息的元祖
    if like == '':  # 如果筛选值为空，则匹配全部
        like = '%'
    else:
        like = '%' + like + '%'
    if sort != 'ASC' and sort != 'DESC':  # 默认降序
        sort = 'DESC'
    if page < 0:  # 如果页号小于 0，从第 0 条开始读取
        page = 0
    else:
        page = page * 30
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT * FROM `film_list` WHERE `classification` LIKE '%s' ORDER BY `score` %s LIMIT %s,30;" % (
        like, sort, page)
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result

def get_films_year(year: str, sort: str, page: int): # 按年份分页获取电影列表信息
    # 参数为：筛选值，排序规则(ASC:升序，DESC:降序)，页号
    # 返回包含一组电影信息的元祖
    if year == '':  # 如果筛选值为空，则匹配全部
        year = '%'
    else:
        year = '%' + year + '%'
    if sort != 'ASC' and sort != 'DESC':  # 默认降序
        sort = 'DESC'
    if page < 0:  # 如果页号小于 0，从第 0 条开始读取
        page = 0
    else:
        page = page * 30
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT * FROM `film_list` WHERE `release_date` LIKE '%s' ORDER BY `score` %s LIMIT %s,30;" % (
        year, sort, page)
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result

def updata_film(con, subject, key, value):  # 插入电影详细信息到数据库
    # 参数为：数据库连接对象，subject，字段，字段的值
    # 插入正常输出受影响的行数
    # 插入异常情况输出 sql 语句
    cursor = con.cursor()
    sql = "UPDATE `film_list` SET `" + str(key) + "` = '" + str(
        value) + "' WHERE `film_list`.`subject` = " + str(subject) + ";"
    try:
        cursor.execute(sql)
        con.commit()
        print("cursor.excute:", cursor.rowcount)
    except Exception:
        con.rollback()
        print("发生异常", Exception)
        print(sql)


def find_film(film_name: str):
    """
    查询一个电影
    :param film_name:
    :return: 电影记录
    """
    con = douban_connect()
    cursor = con.cursor()
    # "SELECT * FROM film_list WHERE subject = '%s'" % (subject)
    sql = "SELECT * FROM `film_list` WHERE `title` LIKE '%{}%';".format(film_name, )
    cursor.execute(sql)
    result = cursor.fetchall()
    con.close()
    return result


def get_user_collections(uname: str):
    # 参数为用户名，返回包含用户信息的字典
    # 字典第一个元素 row 为 0 表示未查询到用户
    # 字典第一个元素 row 为 1 表示查询到用户
    # 返回示例：{'row': 1, 'uname': 'admin', 'email': 'admin@db.com', 'passwd': '123456'}
    user = {'row': 0, 'uname': '', 'collection': ''}
    con = douban_connect()
    cursor = con.cursor()
    sql = "SELECT `uname`,`collection` FROM `user_list` WHERE BINARY `uname` = '%s';" % (uname)
    cursor.execute(sql)
    row = cursor.rowcount  # 获取的行数
    if row == 1:
        result = cursor.fetchone()  # 返回元组
        user['row'] = row
        user['uname'] = result[0]
        user['collection'] = result[1]
    con.close()
    return user


def get_users_collections_by_movie(movie: str) -> pd.DataFrame:
    """
    获得收藏了某部电影的全部用户的全部收藏
    :param movie: ...
    :return: ...
    """
    con = douban_connect()
    cursor = con.cursor()
    cursor.execute("SELECT `uname`,`collection` FROM `user_list` WHERE `collection` LIKE '%{}%';".format(movie, ))
    users = cursor.fetchall()
    con.close()
    return pd.DataFrame(users, columns=['uname', 'collection'])


def insert_evaluation(username: str, comment: str, score: float, subject: str, title: str):
    """
    插入评论及评分
    :param username: 用户名
    :param comment: 评论
    :param level: 评分
    :return: msg
    """
    msg = {'result': False, 'info': ''}
    current_time = datetime.datetime.now()
    date_formatted = current_time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        con = douban_connect()
        cursor = con.cursor()
        cursor1 = con.cursor()

        sql = "INSERT INTO user_comment (subject_id, username, comment, title, insert_time, score) values (%s, %s, %s, %s, %s, %s)"
        sql2 = "INSERT INTO user_score (subject_id, username, score) values (%s, %s, %s)"
        cursor.execute(sql, (subject, username, comment, title, date_formatted, score))
        cursor1.execute(sql2, (subject, username, score))
        if cursor.rowcount > 0 and cursor1.rowcount > 0:
            # 提交事务
            con.commit()

            # 这是注册成功信息
            msg["result"] = True
            msg["info"] = '评论成功'
        else:
            msg['info'] = '未找到匹配的用户记录'
    except pymysql.connect.Error as err:
        msg["info"] = f'评论失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()
            cursor1.close()
        if 'con' in locals():
            con.close()

    return msg


def get_comment(sub: str):
    """
    获取电影的评论
    :param sub: 电影id
    :return: 评论元组
    """
    msg = {'result': False, 'info': '', 'comments': ''}
    try:
        con = douban_connect()
        cursor = con.cursor()

        sql = "SELECT `username`, `comment`, `insert_time`, `score` FROM `user_comment` WHERE `subject_id` = %s;"

        cursor.execute(sql, (sub))

        if cursor.rowcount > 0:
            # 提交事务
            results = cursor.fetchall()
            print("results", results)
            # 这是注册成功信息
            msg["comments"] = [{'username': username, 'comment': comment, 'insert_time': insert_time, 'score': (score / 2) } for username, comment, insert_time, score in results]
            msg['result'] = True
            msg["info"] = '评论成功'
        else:
            msg['info'] = '未找到匹配的用户记录'
    except pymysql.connect.Error as err:
        msg["info"] = f'评论失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()

        if 'con' in locals():
            con.close()

    return msg

def get_latest_comment():
    """
    获取最新的10条评论
    :return:
    """
    msg = {'result': False, 'info': '', 'comments': ''}
    try:
        con = douban_connect()
        cursor = con.cursor()

        sql = "SELECT `username`, `comment`, `insert_time`, `score`, `title` FROM `user_comment` ORDER BY `insert_time` DESC  LIMIT 5"

        cursor.execute(sql)

        if cursor.rowcount > 0:
            # 提交事务
            results = cursor.fetchall()
            print("results", results)
            # 这是注册成功信息
            msg["comments"] = [{'username': username, 'comment': comment, 'insert_time': insert_time, 'score': (score / 2), 'title': title}
                               for username, comment, insert_time, score, title in results]
            msg['result'] = True
            msg["info"] = '评论成功'
        else:
            msg['info'] = '未找到匹配的用户记录'
    except pymysql.connect.Error as err:
        msg["info"] = f'评论失败:{err}'
    finally:
        # 关闭游标和连接
        if 'cursor' in locals():
            cursor.close()

        if 'con' in locals():
            con.close()

    return msg

def get_film_title_strb(film_sub):
    con = douban_connect()
    cursor = con.cursor()
    cursor.execute("SELECT `title`,`strb` FROM `film_list` WHERE `subject`='%s';" % (film_sub,))
    film = cursor.fetchall()
    con.close()
    return film[0]


def get_user_by_watched_movie(subject):
    con = douban_connect()
    cursor = con.cursor()
    cursor.execute("SELECT username,score FROM user_score WHERE subject_id='%s';" % (subject,))
    film = cursor.fetchall()
    con.close()
    return pd.DataFrame(film, columns=['username', 'score'])


def get_user_by_love(loves: tuple):
    con = douban_connect()
    cursor = con.cursor()
    reg_str = "|".join(loves)
    cursor.execute("SELECT uname FROM user_list WHERE love REGEXP '{}';".format(reg_str, ))
    res = cursor.fetchall()
    con.close()
    return [itm[0] for itm in res if itm]


def get_user_love_likes_me(username):
    my_loves = get_user_love(username)['love'].split('-')
    return get_user_by_love(my_loves)

    # return my_love


def get_multi_users_score(uname_list):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    format_strings = ','.join(['%s'] * len(uname_list))
    query = f"SELECT `username`,`subject_id`,`score` FROM user_score WHERE `username` IN ({format_strings});"
    # 打印实际执行的 SQL 命令
    sql = query % tuple(f"'{param}'" for param in uname_list)
    cursor.execute(sql)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['username', 'subject_id', 'score'])


def get_all_user_score():
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    cursor.execute("SELECT username,subject_id,score FROM user_score;")
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['username', 'subject_id', 'score'])


def get_multi_films(films_list: list):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    format_strings = ','.join(['%s'] * len(films_list))
    query = f"SELECT `subject`,title,strb,score,introduction,film_length,release_date,director,starring FROM film_list WHERE `subject` IN ({format_strings});"
    cursor.execute(query, tuple(films_list))
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['subject', 'title', 'strb', 'score', 'introduction', 'film_length',
                                      'release_date', 'director', 'starring'])


def get_multi_films_with_classification(films_list: list):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    format_strings = ','.join(['%s'] * len(films_list))
    query = f"SELECT `subject`,title,strb,score,introduction,film_length,release_date,director,starring,classification FROM film_list WHERE `subject` IN ({format_strings});"
    cursor.execute(query, tuple(films_list))
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['subject', 'title', 'strb', 'score', 'introduction', 'film_length',
                                      'release_date', 'director', 'starring', 'classification'])


def get_multi_films_with_all_info(films_list: list):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    format_strings = ','.join(['%s'] * len(films_list))
    query = f"SELECT * FROM film_list WHERE `subject` IN ({format_strings});"
    cursor.execute(query, tuple(films_list))
    res = cursor.fetchall()
    con.close()
    return res


def get_some_users_collections(num):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    query = f"SELECT `uname`,`collection` FROM user_list ORDER BY RAND() LIMIT %d;" % (num,)
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['uname', 'collection'])


def get_user_love(username):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    query = f"SELECT `uname`,`love` FROM user_list WHERE `uname`='%s';" % (username,)
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    username, love = res[0]
    return {'username': username, 'love': love}


def get_all_user_logs() -> pd.DataFrame:
    con = douban_connect()
    cursor = con.cursor()
    query = f"SELECT uname,`subject`,load_time,CF_target FROM user_log LIMIT 10000;"
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['uname', 'subject', 'load_time', 'CF_target'])


def get_all_film_type():
    con = douban_connect()
    cursor = con.cursor()
    query = f"SELECT `subject`,classification FROM film_list;"
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['subject', 'classification'])


def get_all_films_info():
    con = douban_connect()
    cursor = con.cursor()
    query = f"SELECT * FROM film_list;"
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return res


def get_all_films_score_date():
    con = douban_connect()
    cursor = con.cursor()
    query = f"SELECT `subject`,release_date,score FROM film_list;"
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res, columns=['subject', 'release_date', 'score'])


# def get_user_score_one(uname):
#     con = douban_connect()
#     cursor = con.cursor()
#     query = f"SELECT `subject`,release_date,score FROM film_list;"
#     cursor.execute(query)
#     res = cursor.fetchall()
#     con.close()
#     return pd.DataFrame(res, columns=['subject', 'release_date', 'score'])


def get_user_comment(username):
    con = douban_connect()
    cursor = con.cursor()
    query = "SELECT `id`,subject_id,username,`comment`,title,insert_time,score FROM user_comment  WHERE username='%s';" % (
        username,)
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return pd.DataFrame(res,
                        columns=['id', 'subject_id', 'username', 'comment', 'title', 'insert_time', 'score']).to_dict(
        orient='records')


def get_films_random(num):
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    query = f"SELECT * FROM film_list ORDER BY RAND() LIMIT %d;" % (num,)
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return res


def remove_comment(com_id):
    conn = douban_connect()
    cursor = conn.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    sql = f"DELETE FROM user_comment WHERE `id` = %d;" % (com_id,)
    try:
        # 执行 SQL 语句
        cursor.execute(sql)
        # 提交事务
        conn.commit()
        print(cursor.rowcount, "条记录删除成功")
    except pymysql.MySQLError as err:
        print("删除数据失败: {}".format(err))
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


def get_comments_num():
    con = douban_connect()
    cursor = con.cursor()
    # cursor.execute("SELECT username,subject_id,score FROM user_score;")
    query = f"SELECT COUNT(*) FROM user_comment;"
    cursor.execute(query)
    res = cursor.fetchall()
    con.close()
    return res[0][0]


def main():
    print(get_user('july'))
    print(get_users())
    print(user_login('july', '123'))
    print(get_film(1293116))
    like = '科幻'
    sort = ''
    page = 0
    result = get_films(like, sort, page)
    for i in result:
        print("%s \t %s " % (i[0], i[1]))


if __name__ == '__main__':
    # main()
    # print(get_users_collections_by_movie('bqBgwCZS600IxY2T'))
    print(find_film('燃'))
