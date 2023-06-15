from .extensions import * 
import MySQLdb.cursors


def _queryAllMembers(sql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)

    return cursor.fetchall()

def _isMember(sql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)

    member = cursor.fetchone()

    if member:
        return True
    else:
        return False
    
def _queryOneMember(sql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)

    return cursor.fetchone()

    
def _addMember(sql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)
    mysql.connection.commit()
    

