import psycopg2
import psycopg2.extras
import hashlib
from datetime import datetime


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class user:
    def __init__(self, database, username, password, host, port):
        # 初始化
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    def connect_test(self):
        try:
            conn = psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            conn.close()
            return True
        except:
            # 连接出错
            return False

    def query(self, sql, args):
        # 使用with语句自动管理资源
        with psycopg2.connect(
            database=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
        ) as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # 执行SQL语句
            cursor.execute(sql, args)

            # 返回查询到的所有内容
            return cursor.fetchall()

    def insert(self, sql, args):
        with psycopg2.connect(
            database=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
        ) as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql, args)
            conn.commit()

    def modify(self, sql, args):
        msg = ""  # 错误返回信息
        status = 1  # 状态，1为成功，0为出错

        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(sql, args)
                conn.commit()

        except Exception as e:
            msg = str(e)
            print(msg)
            status = 0

        return {"status": status, "msg": msg}

    def get_role(self):
        # 定义角色字典
        role = {"inventory_manager": 0, "importi_manager": 0, "exporti_manager": 0}

        # 一次性查询用户的角色名
        sql = """
        SELECT r.rolname
        FROM pg_roles r
        JOIN pg_auth_members m ON r.oid = m.roleid
        WHERE m.member = (SELECT oid FROM pg_roles WHERE rolname = %s)
        """
        role_names = self.query(sql, (self.username,))

        # 更新角色字典
        for row in role_names:
            role_name = row["rolname"]
            if role_name in role:
                role[role_name] = 1

        return role

    def register(self, info):
        """
        注册新用户，数据插入至数据库
        """
        username = info["username"]
        password = info["password"]
        email = info["email"]
        sex = info["sex"]
        birthday = info["birthday"]
        address = info["address"]
        phone = info["phone"]
        # print(username, password, email, sex, birthday, address, phone)

        try:
            # SQL 插入语句
            query = """
                INSERT INTO users (username, password, sex, birthday, address, phone, email) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

            # 使用 query 方法执行插入操作
            self.insert(query, (username, password, sex, birthday, address, phone, email))
            return True
        except psycopg2.Error as e:
            print("An error occurred:", e)
            return False

    def user_exists(self, username):
        """
        目前用户身份是否为普通用户
        由于普通用户使用默认数据库账号初始化user, 所以需要传入特定username进行查询
        """
        # if username == None:
        #     username = self.username
        # print(f"username: {username}")
        sql_query = "SELECT username FROM users WHERE username = %s"
        result = self.query(sql_query, (username,))
        # print(result)
        if result != None and len(result) > 0:
            return True
        else:
            return False

    def user_login(self, username, password):
        """
        用户登录检测函数
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn, conn.cursor() as cur:
                # 准备 SQL 查询语句
                query = "SELECT password FROM users WHERE username = %s;"
                cur.execute(query, (username,))
                result = cur.fetchone()
                if result and result[0] == password:
                    return True
                else:
                    return False
        except psycopg2.Error as e:
            print("An error occurred:", e)
            return False

    def get_all_product(self):
        """
        返回所有商品名和价格列表
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    # 执行查询
                    cur.execute("SELECT product_name, price, discount, quantity FROM inventory ORDER BY product_id;")
                    # 提取结果
                    product_items = []
                    for record in cur.fetchall():
                        product_name, price, discount, quantity = record
                        item = {
                            "product_name": product_name,
                            "price": price,
                            "path": f"img/{product_name}.jpg",
                            "price_discount": round(price * discount, 2),
                            "quantity": quantity,
                        }
                        product_items.append(item)

                    return product_items

        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()
            return [], []

    def get_product_quantity_in_cart(self, username):
        """
        返回某个用户购物车商品数量
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    # 根据用户名查找user_id
                    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                    user_id = cur.fetchone()[0]

                    # 查询该用户购物车中所有商品的数量
                    cur.execute("SELECT SUM(quantity) FROM carts WHERE user_id = %s", (user_id,))
                    total_quantity = cur.fetchone()[0]

                    return total_quantity if total_quantity is not None else 0

        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()
            return -1

    def search_product(self, name):
        """
        返回指定的商品名和价格信息
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    # 执行查询
                    cur.execute(
                        "SELECT product_name, price, discount FROM inventory WHERE product_name ILIKE %s ORDER BY product_id;",
                        (f"%{name}%",),
                    )
                    product_items = []
                    for record in cur.fetchall():
                        product_name, price, discount = record
                        item = {
                            "product_name": product_name,
                            "price": price,
                            "path": f"img/{product_name}.jpg",
                            "price_discount": round(price * discount, 2),
                        }
                        product_items.append(item)
                    return product_items

        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()
            return []

    def add_to_cart(self, username, product_name):
        """
        将商品加入至购物车
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
                    user_id = cur.fetchone()
                    user_id = user_id[0]
                    # 根据用户名查找user_id
                    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                    user_id = cur.fetchone()[0]

                    # 根据商品名查找product_id
                    cur.execute("SELECT product_id FROM inventory WHERE product_name = %s", (product_name,))
                    product_id = cur.fetchone()[0]

                    # 检查商品是否已在购物车中
                    cur.execute(
                        "SELECT quantity FROM carts WHERE user_id = %s AND product_id = %s",
                        (user_id, product_id),
                    )
                    result = cur.fetchone()
                    if result:
                        # 购物车中已有该商品，更新数量
                        new_quantity = result[0] + 1
                        cur.execute(
                            "UPDATE carts SET quantity = %s WHERE user_id = %s AND product_id = %s",
                            (new_quantity, user_id, product_id),
                        )
                    else:
                        # 购物车中没有该商品，插入新记录
                        cur.execute(
                            "INSERT INTO carts (user_id, product_id, quantity) VALUES (%s, %s, 1)",
                            (user_id, product_id),
                        )

                    # 提交事务
                    conn.commit()

        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()

    def get_orders(self, username):
        """
        获取某个用户的订单信息
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT user_id
                        FROM users
                        WHERE username = %s
                    """,
                        (username,),
                    )
                    user_id = cur.fetchone()[0]
                    cur.execute(
                        """
                        SELECT order_id, totalprice, orderdate
                        FROM orders
                        WHERE user_id = %s
                    """,
                        (user_id,),
                    )
                    order_infos = cur.fetchall()

                    order_items = []
                    for order_info in order_infos:
                        order_id = order_info[0]
                        totalprice = order_info[1]
                        orderdate = order_info[2]
                        item = {
                            "order_id": order_id,
                            "totalprice": totalprice,
                            "orderdate": orderdate,
                        }
                        cur.execute(
                            """
                            SELECT product_name, bto.quantity
                            FROM belong_to_order bto
                            JOIN inventory g on bto.product_id = g.product_id
                            WHERE bto.order_id = %s
                        """,
                            (order_id,),
                        )
                        records = cur.fetchall()
                        product_string = ""
                        for record in records:
                            product_string += f"{record[0]}x{record[1]}\n"
                        item["product"] = product_string[:-1]
                        order_items.append(item)
                    return order_items
        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()
            return []

    def get_all_orders_from_user(self, username):
        """
        返回某个用户的所有订单信息
        """
        order_items = self.get_orders(username)
        # 修改展示的订单号
        for i in range(len(order_items)):
            order_items[i]["order_id"] = i + 1
        return order_items

    def show_cart(self, username):
        """
        返回某个用户的购物车信息
        """
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
                    user_id = cur.fetchone()

                    if user_id is None:
                        print("用户不存在")
                        return [], [], [], 0

                    user_id = user_id[0]

                    # 执行查询以获取购物车详情
                    query = """
                        SELECT g.product_id, g.product_name, c.quantity, g.price * g.discount, (c.quantity * g.price * g.discount) as total_price_per_item
                        FROM carts c
                        JOIN inventory g ON c.product_id = g.product_id
                        WHERE c.user_id = %s;
                    """
                    cur.execute(query, (user_id,))

                    # 提取结果
                    cart_items = []
                    cart_total_price = 0

                    for record in cur.fetchall():
                        product_id, product_name, quantity, price, total_price = record
                        item = {
                            "product_id": product_id,
                            "product_name": product_name,
                            "quantity": quantity,
                            "price": round(price, 2),
                            "total_price": round(total_price, 2),
                            "path": f"img/{product_name}.jpg",
                        }
                        cart_items.append(item)
                        cart_total_price += total_price
                    return cart_items, round(cart_total_price, 2)

        except psycopg2.Error as e:
            print("An error occurred:", e)
            if conn is not None:
                conn.close()
            return [], 0


    def make_order(self, username):
        """
        用户下单
        """
        try:
            # 连接数据库
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    # 获取用户ID
                    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                    user_id = cur.fetchone()[0]

                    # 获取购物车总价
                    _, cart_total_price = self.show_cart(username)

                    # 获取当前时间
                    orderdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 插入订单信息，并获取新订单的订单ID
                    cur.execute(
                        "INSERT INTO orders (user_id, totalprice, orderdate) VALUES (%s, %s, %s) RETURNING order_id",
                        (user_id, cart_total_price, orderdate),
                    )
                    order_id = cur.fetchone()[0]

                    # 获取购物车商品信息
                    cur.execute("SELECT product_id, quantity FROM carts WHERE user_id = %s", (user_id,))
                    cart_items = cur.fetchall()

                    for product_id, quantity_ordered in cart_items:
                        # 检查库存是否足够
                        cur.execute("SELECT quantity, sales, price, discount, total_sales FROM inventory WHERE product_id = %s", (product_id,))
                        inventory_quantity, old_sales, price, discount, total_sales = cur.fetchone()

                        # 检查库存是否足够
                        if inventory_quantity < quantity_ordered:
                            cur.execute("SELECT product_name FROM inventory WHERE product_id = %s", (product_id,))
                            product_name = cur.fetchone()[0]
                            raise Exception(f"Not enough stock for {product_name}, product_id {product_id}")

                        # 更新库存和销售数量
                        new_quantity = inventory_quantity - quantity_ordered
                        new_sales = old_sales + quantity_ordered
                        sales_amount = quantity_ordered * price * discount
                        new_total_sales = total_sales + sales_amount

                        cur.execute("UPDATE inventory SET quantity = %s, sales = %s, total_sales = %s WHERE product_id = %s", (new_quantity, new_sales, new_total_sales, product_id))

                        # 插入订单-商品关系
                        cur.execute(
                            "INSERT INTO belong_to_order (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                            (order_id, product_id, quantity_ordered),
                        )

                        # 更新销售记录
                        cur.execute(
                            "INSERT INTO exporti_log (product_id, delta_quantity, change_date, changed_by) VALUES (%s, %s, %s, %s)",
                            (product_id, -quantity_ordered, datetime.now(), "System"),
                        )

                    # 清空购物车
                    cur.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))
                    conn.commit()

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optional: Handle specific error types, e.g., insufficient stock
            if "Not enough stock" in str(e):
                # 提取 product_name 和 product_id
                import re

                match = re.search(r"Not enough stock for (.*), product_id (\d+)", str(e))
                if match:
                    product_name = match.group(1)
                    product_id = match.group(2)
                    return f"错误: 库存不足，无法购买 {product_name} (产品ID: {product_id})"
            # Roll back any changes if an error occurs
            conn.rollback()
            return f"订单处理错误: {str(e)}"

        return f"支付成功！订单号: {order_id}。"

    def update_cart_item(self, username, product_id, quantity):
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE carts
                        SET quantity = %s
                        WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND product_id = %s
                    """,
                        (quantity, username, product_id),
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error updating cart item: {e}")
            raise e

    def remove_cart_item(self, username, product_id):
        try:
            with psycopg2.connect(
                database=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM carts
                        WHERE user_id = (SELECT user_id FROM users WHERE username = %s) AND product_id = %s
                    """,
                        (username, product_id),
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error removing cart item: {e}")
            raise e
