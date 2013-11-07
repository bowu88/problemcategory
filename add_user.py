#!/usr/bin/env python
#coding=utf-8
import MySQLdb
import hashlib

conn = MySQLdb.connect('localhost', 'user', 'password', 'problemCategory', charset='utf8')
cur = conn.cursor()

pre = 'sA2lT7!54-'
name = raw_input("用户名：")
passwd = raw_input("密码：")
email = raw_input("邮箱：")
passwd = hashlib.sha1(pre + passwd).hexdigest()

sql_content = "insert into user (UserName, Password, Email, Permission) values ('%s', '%s', '%s', 1)" %(name, passwd, email)
try:
    cur.execute(sql_content)
    conn.commit()
    print '添加成功！'
except:
    print '添加失败！'
