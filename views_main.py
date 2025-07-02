import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash

main_bp = Blueprint("main", __name__)
DATA_DIR_VIP = "data/vip"
DATA_DIR_NONVIP = "data/non-vip"

def get_user_path(name):
    for folder in [DATA_DIR_VIP, DATA_DIR_NONVIP]:
        path = os.path.join(folder, f"{name}.plist")
        if os.path.exists(path):
            return path
    return None

@main_bp.route("/")
def index():
    search = request.args.get("search", "").strip()
    customers = []
    for group, folder in [("vip", DATA_DIR_VIP), ("non-vip", DATA_DIR_NONVIP)]:
        for filename in os.listdir(folder):
            if filename.endswith(".plist"):
                with open(os.path.join(folder, filename), encoding="utf-8") as f:
                    data = json.load(f)
                    if search and search not in data["name"]:
                        continue
                    last_record = data["records"][-1]["date"] if data["records"] else "无记录"
                    balance = data["records"][-1]["after_balance"] if data["records"] else 0
                    customers.append({
                        "name": data["name"],
                        "age": data.get("age", ""),
                        "telephone": data.get("telephone", ""),
                        "email": data.get("email", ""),
                        "address": data.get("address", ""),
                        "heart_function": data.get("heart_function", ""),
                        "operation": data.get("operation", ""),
                        "metal": data.get("metal", ""),
                        "appetite": data.get("appetite", ""),
                        "excretion": data.get("excretion", ""),
                        "sleep_quality": data.get("sleep_quality", ""),
                        "group": group,
                        "last_date": last_record,
                        "balance": balance,
                        "disease": data.get("disease", ""),
                        "note": data.get("note", "")
                    })
    return render_template("index.html", customers=customers, search=search)

@main_bp.route("/user/<name>")
def user_detail(name):
    path = get_user_path(name)
    if not path:
        return "未找到", 404
    with open(path, encoding="utf-8") as f:
        user = json.load(f)
    return render_template("details.html", user=user)
@main_bp.route("/edit_user/<name>", methods=["GET", "POST"])
def edit_user(name=None):
    if not name:
        return "缺少用户名称", 400
    path = get_user_path(name)
    if not path:
        return f"找不到用户 {name}", 404

    with open(path, encoding='utf-8') as f:
        user = json.load(f)

    if request.method == "POST":
        for field in ["name", "age", "telephone", "email", "address",
                      "heart_function", "operation", "metal", "appetite",
                      "excretion", "sleep_quality", "disease", "note"]:
            user[field] = request.form.get(field, "")
        user["is_member"] = "is_member" in request.form

        with open(path, "w", encoding="utf-8") as f:
            json.dump(user, f, ensure_ascii=False, indent=2)
        return redirect(url_for("main.user_detail", name=name))

    return render_template("edit_user.html", user=user)

@main_bp.route("/confirm_delete/<name>")
def confirm_delete(name):
    return render_template("areyousure.html", name=name)

@main_bp.route("/delete/<name>", methods=["POST"])
def perform_delete(name):
    path = get_user_path(name)
    if path:
        os.remove(path)
        flash(f"成功删除：{name}")
    else:
        flash(f"未找到：{name}")
    return redirect(url_for("main.index"))


@main_bp.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        user = {}
        for field in ["name", "age", "telephone", "email", "address",
                      "heart_function", "operation", "metal", "appetite",
                      "excretion", "sleep_quality", "disease", "note"]:
            user[field] = request.form.get(field, "")
        user["is_member"] = "is_member" in request.form
        user["records"] = []  # 初始没有记录

        name = user["name"]
        if not name:
            flash("姓名不能为空")
            return redirect(url_for("main.add_user"))

        if get_user_path(name):
            flash("用户已存在")
            return redirect(url_for("main.add_user"))

        folder = DATA_DIR_VIP if user["is_member"] else DATA_DIR_NONVIP
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name}.plist")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user, f, ensure_ascii=False, indent=2)

        flash("用户添加成功")
        return redirect(url_for("main.index"))

    # GET 请求显示空表单
    empty_user = {
        "name": "", "age": "", "telephone": "", "email": "", "address": "",
        "heart_function": "", "operation": "", "metal": "", "appetite": "",
        "excretion": "", "sleep_quality": "", "disease": "", "note": "",
        "is_member": False
    }
    return render_template("add_user.html", user=empty_user)


# 备份文件查询 （完全的岁月史书）
BACKUP_DIR = "backup"

@main_bp.route("/backup_list/")
def backup_list():
    if not os.path.exists(BACKUP_DIR):
        return "暂无备份", 404
    # 列出所有备份年月文件夹，按时间倒序
    folders = sorted(os.listdir(BACKUP_DIR), reverse=True)
    return render_template("backup_list.html", folders=folders)

@main_bp.route("/backup_list/<year_month>/")
def backup_files(year_month):
    folder_path = os.path.join(BACKUP_DIR, year_month)
    if not os.path.exists(folder_path):
        return "备份不存在", 404
    files = [f for f in os.listdir(folder_path) if f.endswith(".plist")]
    return render_template("backup_files.html", year_month=year_month, files=files)

@main_bp.route("/backup_list/<year_month>/<filename>")
def backup_file_detail(year_month, filename):
    file_path = os.path.join(BACKUP_DIR, year_month, filename)
    if not os.path.exists(file_path):
        return "文件不存在", 404
    with open(file_path, encoding="utf-8") as f:
        user = json.load(f)
    return render_template("details.html", user=user)


