import mysql.connector
from mysql.connector import errorcode


class RetailStoreDB:
    def __init__(self, hostName, userName, pwd, db):
        try:
            cnx = mysql.connector.connect(host=hostName,
                                          user=userName,
                                          password=pwd,
                                          database=db)
            self.conn = cnx
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def getData(self, queryString):
        cursor = self.conn.cursor()
        cursor.execute(queryString)
        data = cursor.fetchall()
        cursor.close()
        return data

    def close_connection(self):
        self.conn.close()


"""
hm = RetailStoreDB('localhost','root','abcd@1234','retail_store_analytics')

dat=hm.getData('select * from heatmap limit 2')
print(dat)

hm.close_connection()
"""
