'''

para usar:

import backend
backend.create_user('Nico Cesar','nico@nicocesar.com')
backend.create_kilink('sdkjj', 1, 'import mindread')
k = backend.get_kilink(1)
print k
backend.get_content('sdkjj',1)


'''
import sqlobject
import datetime
import difflib
import os

db_filename = os.path.abspath('data.db')
if os.path.exists(db_filename):
    firsttime = False
else:
    firsttime = True

connection_string = 'sqlite:' + db_filename
#connection ='sqlite:/:memory:?debug=1'
connection = sqlobject.connectionForURI(connection_string)
sqlobject.sqlhub.processConnection = connection

class UserError:
    pass

class WrongTimestamp:
    def __init__(self, d):
        self.d=d

    def __repr__(self):
        return "wrong datetime: %s. Should be a datetime.datetime instance" % str(self.d)

class MissingKilink:
    def __init__(self, kid, revno):
        self.kid = kid
        self.revno = revno

    def __repr__(self):
        return "Missing kilink for kid = %s. and revno = %s" % (str(self.kid), str(self.revno))

class MultipleKilink:
    def __init__(self, kid, revno):
        self.kid = kid
        self.revno = revno

    def __repr__(self):
        return "Multiple kilink for kid = %s. and revno = %s. This shouldn't happen ever!" % (str(self.kid), str(self.revno))

class ExistingKilink:
    def __init__(self, kid):
        self.kid = kid

    def __repr__(self):
        return "There is already kilink for kid = %s" % str(self.kid)

class KiUser(sqlobject.SQLObject):
    name = sqlobject.UnicodeCol()
    email = sqlobject.StringCol()

class Kilink(sqlobject.SQLObject):
    kid = sqlobject.StringCol()
    revno = sqlobject.IntCol()
    parent_revno = sqlobject.IntCol()
    user = sqlobject.ForeignKey('KiUser')
    content = sqlobject.PickleCol() ## in the future we can store preprocessed HTML objects
    timestamp  = sqlobject.DateTimeCol()


def create_user(name, email):
    p = KiUser(name = name, email = email)
    return p.id

def create_kilink(kid, user, content, timestamp=None):
    results = Kilink.selectBy(kid=kid)
    if results.count() > 0:
        raise ExistingKilink(kid)
    

    try:
        u = KiUser.get(user)
    except Exception,e:
        raise UserError
    
    if not timestamp:
        timestamp = datetime.datetime.now()
    else:
        if not isinstance(timestamp,datetime.datetime):
            raise WrongTimestap(datetime)


    k = Kilink(kid = kid, revno=1, parent_revno=-1, user=u, content=content, timestamp=timestamp)
    return "ok "+ str(k.id)

def get_kilink(kid):
    k = Kilink.get(kid)
    return k

def update_kilink(kid, revno=None, parent_revno=None, user_id=None, content=None, timestamp=None):
    k = Kilink.get(kid)
    u = None
    if user_id:
        try:
            u = KiUser.get(user_id)
        except Exception,e:
            raise UserError

    if revno:
        k.revno = revno
    if parent_revno:
        k.parent_revno = parent_revno
    if u:
        k.user = u
    if content:
        k.content = content
    if timestamp:
        k.timestamo = timestamp
    
    return "ok"

def get_content(kid, revno):
    results = Kilink.selectBy(kid=kid, revno=revno)
    if results.count() == 0:
        raise MissingKilink(kid, revno)
    elif results.count() > 1:
        raise MultipleKilink(kid, revno)

    return k[1].content

def get_diff(kid, revno1, revno2):
    kilink1 = get_content(kid, revno1)
    kilink2 = get_content(kid, revno1)
    return difflib.context_diff(kilink1,kilink2)

def get_kilinks(user_id):
    if user_id:
        try:
            u = KiUser.get(user_id)
        except Exception,e:
            raise UserError

    kilink_list = Kilink.select(user = u)
    return kilink_list


if firsttime:
    KiUser.createTable()
    Kilink.createTable()