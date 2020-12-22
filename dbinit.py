import sqlite3


def init_db(dbname):
    sql = '''
        create table top250(
            id integer primary key autoincrement,
            link text,
            img text,
            cname varchar,
            fname varchar, 
            rating numeric,
            people numeric,
            quote text,
            bdinfo text
        )
    '''

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db('spider.db')
