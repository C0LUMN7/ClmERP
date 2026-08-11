import traceback

import pymysql
from common.recordlog import logs


def _mysql_option(option):
    """MySQL 配置由 config/settings.py 统一读取：环境变量优先，config/local.ini 兜底。"""
    from config import settings
    values = {
        'host': settings.MYSQL_HOST,
        'port': settings.MYSQL_PORT,
        'username': settings.MYSQL_USERNAME,
        'password': settings.MYSQL_PASSWORD,
        'database': settings.MYSQL_DATABASE,
    }
    return values[option]


class ConnectMysql:

    def __init__(self):
        self.conn = None
        self.cursor = None

        mysql_conf = {
            'host': _mysql_option('host'),
            'port': int(_mysql_option('port')),
            'user': _mysql_option('username'),
            'password': _mysql_option('password'),
            'database': _mysql_option('database')
        }

        try:
            self.conn = pymysql.connect(**mysql_conf, charset='utf8', ssl_disabled=True)
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""成功连接到mysql---
            host：{host}
            port：{port}
            db：{database}
            """.format(**mysql_conf))
        except Exception as e:
            logs.error(f"except:{e}")

    def close(self):
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
            self.cursor = None
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
        return True

    def query_all(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchall()

            values = []
            for ite in res:
                values.append(list(ite.values()))

            return values

        except Exception as e:
            logs.error(e)
        finally:
            self.close()

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            logs.info('删除成功')
        except Exception as e:
            logs.error(e)
        finally:
            self.close()
