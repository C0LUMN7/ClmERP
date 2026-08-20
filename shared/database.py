# -*- coding: utf-8 -*-
"""MySQL 连接封装。"""
import pymysql

from config import settings
from shared.logger import logs


class ConnectMysql:

    def __init__(self):
        self.conn = None
        self.cursor = None
        mysql_conf = {
            'host': settings.MYSQL_HOST,
            'port': int(settings.MYSQL_PORT),
            'user': settings.MYSQL_USERNAME,
            'password': settings.MYSQL_PASSWORD,
            'database': settings.MYSQL_DATABASE,
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
            for item in res:
                values.append(list(item.values()))
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
