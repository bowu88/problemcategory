#coding=utf-8

import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path)

import web
import hashlib

web.config.debug = False

urls = (
    '/', 'index',
    '/admin', 'admin',
    '/logout', 'logout',
    '/edit', 'edit',
    '/addcategory', 'addcategory',
    '/addsubcategory', 'addsubcategory',
    '/addproblem', 'addproblem',
    '/changepassword', 'changepassword',
    '/edituser', 'edituser',
    '/adduser', 'adduser',
)

app = web.application(urls, globals())
#session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'login': 0, 'privilege':0})
db = web.database(dbn='mysql', db='problemCategory', user='user', pw='password')
curdir = os.path.dirname(__file__)
session = web.session.Session(app, web.session.DiskStore(curdir + '/' + 'sessions'), initializer={'login': 0, 'privilege':0})


def logged():
    if session.login == 0:
        return False
    else:
        return True

def create_render(privilege):
    if logged():
        if privilege == 0:
            render = web.template.render('templates/reader/')
        elif privilege == 1:
            render = web.template.render('templates/user/')
        elif privilege == 2:
            render = web.template.render('templates/admin/')
        else:
            render = web.template.render('templates/communs/')
    else:
        render = web.template.render('templates/communs/')
    #web.template.Template.globals['render'] = render
    return render

def hashpasswd(passwd):
    pre = 'sA2lT7!54-'
    return hashlib.sha1(pre + passwd).hexdigest()

def dbselect():
    category = db.select('category', vars=locals())
    subcategory = db.select('SubCategory sc, category c', where='sc.CID=c.CID', 
                            what='c.CID, c.CName, sc.SubCID, sc.SubCName', 
                            vars=locals())
    problem = db.select('problem p, user u', where='p.AddUserID=u.UID', 
                       what='p.ID, p.OJName, p.PID, p.PUrl, u.UserName', vars=locals())
    procate = db.select('ProCate pc, SubCategory sc, problem p, user u', 
                        where='sc.SubCID=pc.SubCID and pc.PID=p.ID and u.UID=p.AddUserID', 
                       what='p.ID, p.OJName, p.PID, p.PUrl, sc.SubCID, sc.SubCName, u.UserName', 
                        vars=locals())
    solution = db.select('solution s, user u', where='s.AddUserID=u.UID',
                        what='s.SID, s.SUrl, s.PID, u.UserName', vars=locals())
    ojname = db.query('select distinct OJName from problem order by OJName asc')
    category = list(category)
    subcategory = list(subcategory)
    problem = list(problem)
    procate = list(procate)
    solution = list(solution)
    ojname = list(ojname)
    for pro in problem:
        if not pro.PUrl.startswith('http://'):
            pro.PUrl = 'http://' + pro.PUrl
    for solu in solution:
        if not solu.SUrl.startswith('http://'):
            solu.SUrl = 'http://' + solu.SUrl
    return (category, subcategory, problem, procate, solution, ojname)


class index:
    def GET(self):
        if logged():
            render = create_render(session.privilege)
            category, subcategory, problem, procate, solution, ojname = dbselect()
            username = session.username
            users = db.query('select * from user')
            users = list(users)
            return render.index(category, subcategory, problem, procate, solution, username, ojname, users)
        else:
            render = create_render(session.privilege)
            category, subcategory, problem, procate, solution, ojname = dbselect()
            return render.index(category, subcategory, problem, procate, solution)
    def POST(self):
        username = web.input().username
        password = web.input().password
        category, subcategory, problem, procate, solution, ojname = dbselect()
        try:
            ident = db.select("user", where="UserName=$username",vars=locals())[0]
            if hashpasswd(password) == ident['Password']:
                session.login = 1
                session.username = username
                session.privilege = ident['Permission']
                render = create_render(session.privilege)
                users = db.query('select * from user')
                users = list(users)
                return render.index(category, subcategory, problem, procate, solution, username, ojname, users)
            else:
                session.login = 0
                session.privilege = 0
                render = create_render(session.privilege)
                return render.index(category, subcategory, problem, procate, solution)
        except:
            session.login = 0
            session.privilege = 0
            render = create_render(session.privilege)
            return render.index(category, subcategory, problem, procate, solution)

class logout:
    def GET(self):
        session.login = 0
        session.privilege = 0
        session.kill()
        raise web.seeother('/')

class edit:
    def POST(self):
        for key in web.input().keys():
            value = web.input().get(key)
            if value:
                if key.startswith('editsps'):
                    l = key[7:].split('-')
                    sqlcontent = 'update solution set SUrl="%s" where SID="%s"' %(value, l[2])
                    db.query(sqlcontent)
                elif key.startswith('editsp'):
                    l = key[6:].split('-')
                    sqlcontent = 'update problem set PUrl="%s" where ID="%s"' %(value, l[1])
                    db.query(sqlcontent)
                elif key.startswith('editaddsurl'):
                    l = key[11:].split('-')
                    username = session.username
                    user = db.query('select * from user where UserName="%s"' %username)[0]
                    sqlcontent = 'insert into solution (SID, SUrl, PID, AddUserID) values(null, "%s", "%s", "%s")' %(value, l[1], user.UID)
                    db.query(sqlcontent)
                elif key.startswith('editpp'):
                    l = key[6:].split('-')
                    subc = db.query('select * from SubCategory where SubCName="%s"' %value)[0]
                    sqlcontent = 'update ProCate set SubCID="%s" where PID="%s" and SubCID="%s"' %(subc.SubCID, l[0], l[1])
                    db.query(sqlcontent)
                elif key.startswith('editaddsubc'):
                    l = key[11:].split('-')
                    subc = db.query('select * from SubCategory where SubCName="%s"' %value)[0]
                    sqlcontent = 'insert into ProCate (PID, SubCID) values("%s", "%s")' %(l[1], subc.SubCID)
                    db.query(sqlcontent)
            else:
                print 'aaa'
        raise web.seeother('/')

class addcategory:
    def POST(self):
        category = web.input().addcategory
        if category and not db.query('select * from category where CName="%s"' %category):
            db.query('insert into category values(null, "%s")' %category)
        raise web.seeother('/')

class addsubcategory:
    def POST(self):
        category = web.input().addsubcatecate
        subcategory = web.input().addsubcategory
        cate = db.query('select * from category where CName="%s"' %category)[0]
        if subcategory and not db.query('select * from SubCategory where SubCName="%s"' %subcategory):
            db.query('insert into SubCategory values(null, "%s", "%s")' %(subcategory, cate.CID))
        raise web.seeother('/')

class addproblem:
    def POST(self):
        ojname = web.input().addproblemojname
        ojnameadd = web.input().addproblemaddojname
        pid = web.input().addproblempid
        purl = web.input().addproblempurl
        surl = web.input().addproblemsurl
        subc = web.input().addproblemsubc.split('-')[-1]
        if ojnameadd != '':
            ojname = ojnameadd
        if pid and purl and surl:
            user = db.query('select * from user where UserName="%s"' %session.username)[0]
            db.query('insert into problem values(null, "%s", "%s", "%s", "%s")' %(ojname, pid, user.UID, purl))
            pinfoid = db.query('select * from problem where OJName="%s" and PID="%s" and AddUserID="%s" and PUrl="%s"' %(ojname, pid, user.UID, purl))[0].ID
            db.query('insert into solution values(null, "%s", "%s", "%s")' %(surl, pinfoid, user.UID))
            subcate = db.query('select * from SubCategory where SubCName="%s"' %subc)[0]
            db.query('insert into ProCate values(null, "%s", "%s")' %(pinfoid, subcate.SubCID))
        raise web.seeother('/')

class changepassword:
    def POST(self):
        oldpassword = web.input().oldpassword
        newpassword1 = web.input().newpassword1
        newpassword2 = web.input().newpassword2
        username = session.username
        ident = db.select("user", where="UserName=$username",vars=locals())[0]
        if newpassword1 == newpassword2 and hashpasswd(oldpassword) == ident['Password']:
            newpassword = hashpasswd(newpassword1)
            db.query('update user set Password="%s" where UserName="%s"' %(newpassword, username))
            raise web.seeother('/logout')
        raise web.seeother('/')

class edituser:
    def POST(self):
        keys = web.input().keys()
        l = keys[0].split('-')[-1]
        for key in keys:
            if key.startswith('edituseremail'):
                email = web.input().get(key)
            elif key.startswith('edituserpermission'):
                permission = web.input().get(key)
                if permission == 'root':
                    permission = 2
                elif permission == 'user':
                    permission = 1
                else:
                    permission = 0
            elif key.startswith('edituserpassword'):
                password = web.input().get(key)
        if email and permission:
            if not password:
                db.query('update user set Email="%s", Permission="%s" where UID="%s"' %(email, permission, l))
            else:
                password = hashpasswd(password)
                db.query('update user set Password="%s", Email="%s", Permission="%s" where UID="%s"' %(password, email, permission, l))
        raise web.seeother('/')

class adduser:
    def POST(self):
        username = web.input().addusername
        password = web.input().adduserpassword
        password = hashpasswd(password)
        email = web.input().adduseremail
        permission = web.input().adduserpermission
        if username and password and email and permission:
            if permission == 'root':
                permission = 2
            elif permission == 'user':
                permission = 1
            else:
                permission = 0
            db.query('insert into user values(null, "%s", "%s", "%s", "%s")' %(username, password, email, permission))
        raise web.seeother('/')

if __name__ == '__main__':
    app.run()
    #app.wsgifunc()
