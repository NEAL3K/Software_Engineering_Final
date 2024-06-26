from django.shortcuts import render, redirect, HttpResponse
from postgresql import sql
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

# 用户登录使用信息
User = {
    "username": "Software_Engineering_User",
    "pwd": 123456,
}


# Create your views here.
def home(request):
    # return redirect("/login/")
    # 从detail或cart接受error参数
    context = {}
    error_message = request.GET.get("error", "")
    context["error"] = error_message
    logined = False
    try:
        # 尝试从 cookie 获取用户名和密码
        # cookie会一直保存在浏览器上，退出登录时清除
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")
        # 默认使用给定账户进入主界面
        user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
        # print(f"cookie username: {username}, pwd: {pwd}")
        if user.user_exists(username):
            # 若cookie存储普通账户，则购物车数量显示为购物车中商品数量
            cart_quantity = user.get_product_quantity_in_cart(username)
        else:
            # 若cookie存储管理员账户，则购物车数量显示为0
            user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
            cart_quantity = 0
        logined = True
        # print(f"username: {username}, pwd: {pwd}")
    except KeyError:
        # 如果没有 cookie 或 cookie 验证失败
        user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
        cart_quantity = 0

    product_items = []
    if request.method == "POST":
        if "search_query" in request.POST:
            # 处理搜索请求
            name = request.POST.get("search_query")
            # print(f"搜索关键字：{name}")
            product_items = user.search_product(name)
        elif "product_name" in request.POST:
            if user.user_exists(username):
                product_name = request.POST.get("product_name")
                user.add_to_cart(username, product_name)
                # 获取所有商品
                product_items = user.get_all_product()
                return redirect("/home/")
            else:
                # 可能出现此时登录的是管理员账户，但却点击了购物车按钮，不能添加到购物车
                # print("获取所有商品")
                product_items = user.get_all_product()
                context["error"] = "管理员账户不可添加购物车！"
    else:
        # 获取所有商品
        # print("获取所有商品")
        product_items = user.get_all_product()

    context["product_data"] = product_items
    if logined:
        context["username"] = username
    else:
        context["username"] = "请登录"
    context["cart_quantity"] = cart_quantity
    return render(request, "home.html", context)
    # return render(request, "home.html", {"product_data": product_items, "username": username, "cart_quantity": cart_quantity})

    # return render(request, "home.html")


def login(request):
    context = {}
    if request.method == "POST":
        # 获取用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        hash_pwd = sql.hash_password(pwd)
        # 默认是管理员登录
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        # 测试用户名和密码是否正确
        # if not user.connect_test():
        #     context["error"] = "用户名或密码错误！"
        #     return render(request, "login.html", context)

        # 测试是否管理员用户连接
        if user.connect_test():
            # 获取角色
            role = user.get_role()
            if role["inventory_manager"] or role["importi_manager"] or role["exporti_manager"]:
                # 管理员用户跳转到 /inventory/
                ret = redirect("/inventory/")
                # 登录和角色信息写入cookie
                ret.set_signed_cookie("username", username, salt="yonghuming")
                ret.set_signed_cookie("pwd", pwd, salt="mima")
                ret.set_signed_cookie("inventory_manager", role["inventory_manager"], salt="cunhuo")
                ret.set_signed_cookie("importi_manager", role["importi_manager"], salt="jinhuo")
                ret.set_signed_cookie("exporti_manager", role["exporti_manager"], salt="xiaoshou")
                return ret
        else:
            # 非管理员则所用用户使用指定账号User登录
            user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")

        # 以下是普通用户登录
        # print("用户登录中！")
        # print(f"用户名：{username}, 密码：{pwd}")
        if user.user_exists(username):
            # print("用户存在！")
            valid_login = user.user_login(username, hash_pwd)
            if valid_login:
                # 普通用户跳转到首页
                # print("登录成功！")
                ret = redirect("/home/")
            else:
                # 页面上显示"用户名或密码错误！"
                context["error"] = "用户名或密码错误！"
                return render(request, "login.html", context)
        else:
            # 页面上显示"请先注册用户"
            context["error"] = "请先注册用户"
            return render(request, "login.html", context)

        # 登录和角色信息写入cookie
        ret.set_signed_cookie("username", username, salt="yonghuming")
        ret.set_signed_cookie("pwd", pwd, salt="mima")
        ret.set_signed_cookie("inventory_manager", 0, salt="cunhuo")
        ret.set_signed_cookie("importi_manager", 0, salt="jinhuo")
        ret.set_signed_cookie("exporti_manager", 0, salt="xiaoshou")
        return ret
    else:
        return render(request, "login.html", context)


def register(request):
    # return HttpResponse("注册页面开发中")
    context = {}
    if request.method == "POST":
        user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            confirm_password = request.POST["confirm_password"]
            email = request.POST["email"]
            sex = request.POST["sex"]
            birthday = request.POST["birthday"]
            address = request.POST["address"]
            phone = request.POST["phone"]

            if password != confirm_password:
                # return HttpResponse("Passwords do not match!")
                context["error"] = "密码不匹配!"
                return render(request, "register.html", context)

            if user.user_exists(username):
                # return HttpResponse("Username already taken!")
                context["error"] = "用户名已被注册!"
                return render(request, "register.html", context)

            info = {
                "username": username,
                "password": sql.hash_password(password),
                "email": email,
                "sex": sex,
                "birthday": birthday,
                "address": address,
                "phone": phone,
            }  # hash pwd，保护用户密码信息

            # print("注册中！")
            if user.register(info):
                return redirect("/login/")
            else:
                # return HttpResponse("An error occurred during registration.")
                context["error"] = "注册失败!"

    return render(request, "register.html", context)


def show_personal_info(request):
    """
    展示用户订单信息
    """
    context = {}
    order_items = []
    cart_quantity = 0
    try:
        # 尝试从 cookie 获取用户名和密码
        # cookie会一直保存在浏览器上，退出登录时清除
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")
        # 默认使用给定账户进入主界面
        user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
        # print(f"cookie username: {username}, pwd: {pwd}")
        if user.user_exists(username):
            # 若cookie存储普通账户，则个人主页显示订单信息
            order_items = user.get_all_orders_from_user(username)
            cart_quantity = user.get_product_quantity_in_cart(username)
        else:
            # 若cookie存储管理员账户，则个人主页无订单信息
            user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
            # 可能出现此时登录的是管理员账户，但却点击了个人信息，无个人信息
            context["error"] = "管理员账户没有个人信息！"
            return redirect(f'/home?error={context["error"]}')
        # print(f"username: {username}, pwd: {pwd}")
    except KeyError:
        # 如果没有 cookie 或 cookie 验证失败，跳转登录界面
        return redirect("/login/")

    context["username"] = username
    context["order_data"] = order_items
    context["cart_quantity"] = cart_quantity
    return render(request, "detail.html", context)


def cart(request):
    """
    购物车页面
    """
    context = {}
    cart_items = []
    cart_quantity = 0
    try:
        # 尝试从 cookie 获取用户名和密码
        # cookie会一直保存在浏览器上，退出登录时清除
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")
        # 默认使用给定账户进入主界面
        user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
        # print(f"cookie username: {username}, pwd: {pwd}")
        if user.user_exists(username):
            # 若cookie存储普通账户，则购物车正常显示
            cart_quantity = user.get_product_quantity_in_cart(username)
        else:
            # 若cookie存储管理员账户，则购物车为空
            # 可能出现此时登录的是管理员账户，但却点击了购物车，无购物车信息
            user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
            context["error"] = "管理员账户没有购物车信息！"
            return redirect(f'/home?error={context["error"]}')
        # print(f"username: {username}, pwd: {pwd}")
    except KeyError:
        # 如果没有 cookie 或 cookie 验证失败，跳转登录界面
        return redirect("/login/")

    if request.method == "GET":
        if user.user_exists(username):
            cart_items, cart_total_price = user.show_cart(username)
            # print(f"cart_quantity: {cart_quantity}")
            # print(f"cart_items: {cart_items}, cart_total_price: {cart_total_price}")
            context["cart_items"] = cart_items
            context["cart_total_price"] = cart_total_price
            context["cart_quantity"] = cart_quantity
            context["username"] = username
        return render(request, "cart.html", context)

    if request.method == "POST":
        cart_items, cart_total_price = user.show_cart(username)
        if len(cart_items) == 0:
            # return render(request, "cart.html", context)
            return redirect("/cart/")
        # 提交支付
        order_msg = user.make_order(username)
        # cart_items, cart_total_price = user.show_cart(username)
        # context["cart_items"] = cart_items
        # context["cart_total_price"] = cart_total_price
        # context["cart_quantity"] = cart_quantity
        # context["username"] = username
        # 添加支付成功的消息
        messages.success(request, order_msg)
        return redirect("/cart/")


def update_cart(request):
    print("update_cart")
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        print(f"product_id: {product_id}")
        quantity = data.get("quantity")
        username = request.get_signed_cookie("username", salt="yonghuming")

        try:
            # 能进入购物车，说明是普通用户
            user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
            user.update_cart_item(username, product_id, quantity)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


def remove_from_cart(request):
    print("remove_from_cart")
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        username = request.get_signed_cookie("username", salt="yonghuming")

        try:
            user = sql.user("Software_Final_Project", User["username"], User["pwd"], "127.0.0.1", "5432")
            user.remove_cart_item(username, product_id)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


def inventory(request):
    """
    存货信息列表
    """
    # 提取角色信息
    flag = request.get_signed_cookie("inventory_manager", salt="cunhuo")
    if flag != "1":
        return render(request, "layout.html", {"flag": 1})

    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    i_sqllist = user.query(
        "select product_id, product_name, quantity, price, alert_quantity, is_below_alert, sales, discount from inventory order by product_id",
        "",
    )

    # 结果分页
    # paginator = Paginator(i_sqllist, 1000)
    # posts = paginator.page(1)
    paginator = Paginator(i_sqllist, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "inventory.html", {"posts": posts})


def edit_product(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        field = request.POST.get("field")
        value = request.POST.get("value", None)
        file = request.FILES.get("image", None)

        # 获取当前用户
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")

        # 创建数据库连接
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        try:
            # print(f"product_id: {product_id}, field: {field}, value: {value}, file: {file}")
            if field == "name":
                # 获取旧的商品名称
                old_product_name = user.query("SELECT product_name FROM inventory WHERE product_id = %s", [product_id])[0][0]

                # 更新商品名称
                user.modify("UPDATE inventory SET product_name = %s WHERE product_id = %s", [value, product_id])

                # 重命名对应的图片文件
                old_filename = f"{old_product_name}.jpg"
                new_filename = f"{value}.jpg"
                fs = FileSystemStorage(location=os.path.join(settings.STATICFILES_DIRS[0], "img"))

                old_file_path = os.path.join(fs.location, old_filename)
                new_file_path = os.path.join(fs.location, new_filename)

                if os.path.exists(old_file_path):
                    os.rename(old_file_path, new_file_path)
            elif field == "alert_quantity":
                user.modify("UPDATE inventory SET alert_quantity = %s WHERE product_id = %s", [value, product_id])
            elif field == "price":
                user.modify("UPDATE inventory SET price = %s WHERE product_id = %s", [value, product_id])
            elif field == "discount":
                user.modify("UPDATE inventory SET discount = %s WHERE product_id = %s", [value, product_id])
            elif field == "image" and file:
                product_name = user.query("SELECT product_name FROM inventory WHERE product_id = %s", [product_id])[0][0]
                filename = f"{product_name}.jpg"
                file_path = os.path.join(settings.STATICFILES_DIRS[0], "img", filename)

                # 删除原本的图片
                if os.path.exists(file_path):
                    os.remove(file_path)

                # 保存新图片
                fs = FileSystemStorage(location=os.path.join(settings.STATICFILES_DIRS[0], "img"))
                filename = fs.save(filename, file)
            print("修改成功！")
            return JsonResponse({"status": True})
        except Exception as e:
            return JsonResponse({"status": False, "msg": str(e)})

    return JsonResponse({"status": False, "msg": "Invalid request method"})


def importi(request):
    """
    进货信息列表
    :param request:封装了请求相关的所有信息
    :return:返回模板和数据
    """
    flag = request.get_signed_cookie("importi_manager", salt="jinhuo")
    if flag != "1":
        return render(request, "layout.html", {"flag": 1})

    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    im_list = user.query(
        "select product_id, product_name, quantity, price, alert_quantity, is_below_alert, sales, discount from inventory order by product_id",
        "",
    )

    # 结果分页
    paginator = Paginator(im_list, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "importi.html", {"posts": posts})


def importilog(request):
    flag = request.get_signed_cookie("importi_manager", salt="jinhuo")
    if flag != "1":
        return render(request, "layout.html", {"flag": 1})

    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    im_list = user.query(
        "select log_id, product_id, delta_quantity, change_date, changed_by from importi_log order by log_id",
        "",
    )

    # 获取所有产品信息
    products = user.query("SELECT product_id, product_name FROM inventory", "")
    product_dict = {product[0]: product[1] for product in products}

    # 将product_name添加到im_list中
    im_list_with_name = []
    for item in im_list:
        product_id = item[1]
        product_name = product_dict[product_id]
        item_dict = dict(item)
        item_dict["product_name"] = product_name
        im_list_with_name.append(item_dict)

    im_list = im_list_with_name
    # 结果分页
    paginator = Paginator(im_list, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "importilog.html", {"posts": posts})


def exporti(request):
    """
    销售信息列表
    :param request:封装了请求相关的所有信息
    :return:返回模板和数据
    """
    flag = request.get_signed_cookie("exporti_manager", salt="xiaoshou")
    if flag != "1":
        return render(request, "layout.html", {"flag": 1})

    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询选课信息
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    ex_list = user.query(
        "select product_id, product_name, quantity, price, alert_quantity, is_below_alert, sales, discount, total_sales from inventory order by product_id",
        "",
    )

    # 结果分页
    paginator = Paginator(ex_list, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "exporti.html", {"posts": posts})


def exportilog(request):
    flag = request.get_signed_cookie("exporti_manager", salt="xiaoshou")
    if flag != "1":
        return render(request, "layout.html", {"flag": 1})

    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    ex_list = user.query(
        "select log_id, product_id, delta_quantity, change_date, changed_by from exporti_log order by log_id",
        "",
    )

    # 将 delta_quantity 转为正数
    for i in range(len(ex_list)):
        delta_quantity = ex_list[i]["delta_quantity"]
        # ex_list[i] = (log_id, product_id, abs(delta_quantity), change_date, changed_by)
        ex_list[i]["delta_quantity"] = abs(delta_quantity)

    # 结果分页
    paginator = Paginator(ex_list, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "exportilog.html", {"posts": posts})


def modify(request):
    # 获取所需sql语句
    sql_query = request.POST.get("sql")
    # 获取sql的参数
    args = request.POST.getlist("args[]")  # 传进来的数组后面会加上[]
    if args[0] == "":
        args[0] = None
    # 提取用户信息后执行
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")
    u = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    res = u.modify(sql_query, args)
    # 返回模板
    return JsonResponse(res)


def importi_modify(request):
    if request.method == "POST":
        # 处理 importi_log 更新
        importi_sql = request.POST.get("importi_sql")
        importi_args = request.POST.getlist("importi_args[]")

        # 处理 inventory 更新
        inventory_sql = request.POST.get("inventory_sql")
        inventory_args = request.POST.getlist("inventory_args[]")

        # 获取当前用户
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")

        # 更新 importi_log 参数中的 username
        importi_args = [arg if arg != "<username>" else username for arg in importi_args]

        # 创建数据库连接
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        # 更新两个表
        importi_res = {"status": 0, "msg": "Failed"}  # 如果没有更新就肯定是失败的
        inventory_res = user.modify(inventory_sql, inventory_args)
        # 如果在库中出错，那就不能这么记录了
        if inventory_res["status"] != 0:
            importi_res = user.modify(importi_sql, importi_args)

        return JsonResponse({"importi_result": importi_res, "inventory_result": inventory_res})
    else:
        return JsonResponse({"error": "Invalid request"})


def importi_modify_add(request):
    if request.method == "POST":
        # 处理 importi_log 更新
        importi_sql = request.POST.get("importi_sql")
        print(f"importi_sql: {importi_sql}")
        importi_args = json.loads(request.POST.get("importi_args[]"))
        print(f"importi_args: {importi_args}")

        # 处理 inventory 更新
        inventory_sql = request.POST.get("inventory_sql")
        print(f"inventory_sql: {inventory_sql}")
        inventory_args = json.loads(request.POST.get("inventory_args[]"))
        print(f"inventory_args: {inventory_args}")
        if inventory_args[0] == "":
            inventory_args[0] = None

        # 获取当前用户
        username = request.get_signed_cookie("username", salt="yonghuming")
        print(f"username: {username}")
        pwd = request.get_signed_cookie("pwd", salt="mima")

        # 更新 importi_log 参数中的 username
        importi_args = [arg if arg != "<username>" else username for arg in importi_args]
        print(f"importi_args: {importi_args}")

        # 创建数据库连接
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        file = request.FILES.get("image")
        if file:
            product_name = request.POST.get("add_product_name")  # 假设你在表单中有一个字段为add_product_name
            filename = f"{product_name}.jpg"  # 用商品名命名文件
            fs = FileSystemStorage(location=os.path.join(settings.STATICFILES_DIRS[0], "img"))  # 指定文件保存目录
            filename = fs.save(filename, file)  # 保存文件
            uploaded_file_url = fs.url(filename)  # 获取文件URL

        # 更新两个表
        importi_res = {"status": 0, "msg": "Failed"}  # 如果没有更新就肯定是失败的
        inventory_res = user.modify(inventory_sql, inventory_args)
        # 如果在库中出错，那就不能这么记录了
        if inventory_res["status"] != 0:
            # 新添加的id最大，所以找到最新id
            product_id = user.query("SELECT max(product_id) FROM inventory", [])[0][0]
            importi_args[0] = product_id
            importi_res = user.modify(importi_sql, importi_args)

        print(f"importi_res: {importi_res}")
        print(f"inventory_res: {inventory_res}")
        if file:
            print(f"uploaded_file_url: {uploaded_file_url}")

        return JsonResponse({"importi_result": importi_res, "inventory_result": inventory_res, "file_url": uploaded_file_url})
    else:
        return JsonResponse({"error": "Invalid request"})


def exporti_modify(request):
    if request.method == "POST":
        # 处理 exporti_log 更新
        exporti_sql = request.POST.get("exporti_sql")
        exporti_args = request.POST.getlist("exporti_args[]")

        # 处理 inventory 更新
        inventory_sql = request.POST.get("inventory_sql")
        inventory_args = request.POST.getlist("inventory_args[]")

        # 获取当前用户
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")

        # 更新 exporti_log 参数中的 username
        exporti_args = [arg if arg != "<username>" else username for arg in exporti_args]

        # 创建数据库连接
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        # 更新两个表
        exporti_res = {"status": 0, "msg": "Failed"}  # 如果没有更新就肯定是失败的
        inventory_res = user.modify(inventory_sql, inventory_args)
        # 如果在库中出错，那就不能这么记录了
        if inventory_res["status"] != 0:
            exporti_res = user.modify(exporti_sql, exporti_args)

        return JsonResponse({"exporti_result": exporti_res, "inventory_result": inventory_res})
    else:
        return JsonResponse({"error": "Invalid request"})


def exporti_modify_add(request):
    if request.method == "POST":
        # 处理 exporti_log 更新
        exporti_sql = request.POST.get("exporti_sql")
        exporti_args = request.POST.getlist("exporti_args[]")

        # 处理 inventory 更新
        inventory_sql = request.POST.get("inventory_sql")
        inventory_args = request.POST.getlist("inventory_args[]")
        if inventory_args[0] == "":
            inventory_args[0] = None

        # 获取当前用户
        username = request.get_signed_cookie("username", salt="yonghuming")
        pwd = request.get_signed_cookie("pwd", salt="mima")

        # 更新 exporti_log 参数中的 username
        exporti_args = [arg if arg != "<username>" else username for arg in exporti_args]

        # 创建数据库连接
        user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")

        # 更新两个表
        exporti_res = {"status": 0, "msg": "Failed"}  # 如果没有更新就肯定是失败的
        inventory_res = user.modify(inventory_sql, inventory_args)
        # 如果在库中出错，那就不能这么记录了
        if inventory_res["status"] != 0:
            # 新添加的id最大，所以找到最新id
            product_id = user.query("SELECT max(product_id) FROM inventory", [])[0][0]
            exporti_args[0] = product_id
            exporti_res = user.modify(exporti_sql, exporti_args)

        return JsonResponse({"exporti_result": exporti_res, "inventory_result": inventory_res})
    else:
        return JsonResponse({"error": "Invalid request"})


def superadmin(request):
    # 提取用户名和密码
    username = request.get_signed_cookie("username", salt="yonghuming")
    pwd = request.get_signed_cookie("pwd", salt="mima")

    # 查询
    user = sql.user("Software_Final_Project", username, pwd, "127.0.0.1", "5432")
    i_sqllist = user.query(
        "select product_id, product_name, quantity, price, alert_quantity, is_below_alert, sales, discount from inventory order by product_id",
        "",
    )

    # 结果分页
    paginator = Paginator(i_sqllist, 10)
    current_page = request.GET.get("page")
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger as e:
        posts = paginator.page(1)
    except EmptyPage as e:
        posts = paginator.page(1)

    return render(request, "superadmin.html", {"posts": posts})


def logout(request):
    # 删除cookie
    response = HttpResponseRedirect("/login/")
    response.delete_cookie("username")
    response.delete_cookie("pwd")
    response.delete_cookie("inventory_manager")
    response.delete_cookie("importi_manager")
    response.delete_cookie("exporti_manager")
    # 重定向到登录页面
    return response
