import sqlite3

from utils import Logger

logger = Logger(name='repository').logger


class DB:
    def __init__(self):
        self.session: sqlite3.Cursor = None
        self.con: sqlite3.Connection = None
        self._prepare()

    def _connect(self):
        self.con = sqlite3.connect("db/lite_db.db")
        self.session = self.con.cursor()

    def _prepare(self):
        self._connect()
        try:
            self.session.execute("CREATE TABLE cart("
                                 "id INTEGER not null constraint cart_pk primary key autoincrement,"
                                 "product,"
                                 "amount,"
                                 "user_id not null,"
                                 "product_screen_name,"
                                 "product_id not null)")
            self.session.execute("CREATE TABLE product("
                                 "id INTEGER not null constraint product_pk primary key autoincrement,"
                                 "product_name not null,"
                                 "amount,"
                                 "product_screen_name,"
                                 "price)")
        except Exception as e:
            logger.error(e.__str__())

    def add_to_cart(self, user_id, product, amount, screen_name, product_id):
        pr = self.get_product_from_cart_by_id(product_id, user_id)
        if pr:
            try:
                am = pr[2] + 1
                self.session.execute("UPDATE cart SET amount = ?"
                                     "WHERE product_id = ? AND user_id = ?",
                                     (am, product_id, user_id))
                self.con.commit()
            except Exception as e:
                logger.error(e.__str__())
                self.con.rollback()
        else:
            try:
                self.session.execute("INSERT INTO cart(product, amount, user_id, product_screen_name, product_id) "
                                     "VALUES(?, ?, ?, ?, ?)",
                                     (product, amount, user_id, screen_name, product_id))
                self.con.commit()
            except Exception as e:
                logger.error(e.__str__())
                self.con.rollback()
        self.change_product_count(product_id=product_id, plus=False)

    def remove_from_cart(self, user_id, product_id):
        pr = self.get_product_from_cart_by_id(product_id, user_id)
        try:
            self.session.execute("DELETE FROM cart "
                                 "WHERE product_id = ? AND user_id = ?",
                                 (product_id, user_id))
        except Exception as e:
            logger.error(e.__str__())
        if pr:
            self.change_product_count(product_id=product_id, counter=int(pr[2]))

    def get_cart_by_user_id(self, user_id):
        try:
            res = self.session.execute("SELECT * FROM cart WHERE user_id = ?", (user_id,))
            return res.fetchall()
        except Exception as e:
            logger.error(e.__str__())
        return None

    def get_product_from_cart_by_id(self, pr_id, user_id):
        try:
            res = self.session.execute("SELECT * FROM cart "
                                       "WHERE product_id = ? "
                                       "AND user_id = ?", (pr_id, user_id))
            return res.fetchone()
        except Exception as e:
            logger.error(e.__str__())
        return None

    def change_product_count(self, product_id, plus=True, counter=1):
        pr = self.get_product_by_id(product_id)
        if pr:
            try:
                if plus:
                    am = pr[2] + counter
                else:
                    am = pr[2] - counter
                self.session.execute("UPDATE product SET amount = ? "
                                     "WHERE id = ?",
                                     (am, product_id))
                self.con.commit()
            except Exception as e:
                logger.error(e.__str__())
                self.con.rollback()

    def get_product_by_name(self, name):
        try:
            res = self.session.execute("SELECT * FROM product WHERE product_screen_name = ?", (name,))
            return res.fetchone()
        except Exception as e:
            logger.error(e.__str__())
        return None

    def get_product_by_id(self, pr_id):
        try:
            res = self.session.execute("SELECT * FROM product WHERE id = ?", (pr_id,))
            return res.fetchone()
        except Exception as e:
            logger.error(e.__str__())
        return None

    def get_all_product(self):
        try:
            res = self.session.execute("SELECT * FROM product ORDER BY id").fetchall()
            return res
        except Exception as e:
            logger.error(e.__str__())
        return []

    def add_product(self, name, amount, screen_name, price):
        try:
            self.session.execute("INSERT INTO "
                                 "product(product_name, amount, product_screen_name, price) "
                                 "VALUES(?, ?, ?, ?)",
                                 (name, amount, screen_name, price))
            self.con.commit()
        except Exception as e:
            logger.error(e.__str__())
            self.con.rollback()
