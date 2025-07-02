import os, json
from flask import Blueprint, request, redirect, url_for, render_template
from datetime import datetime

record_bp = Blueprint('record', __name__)

DATA_DIR_VIP = 'data/vip'
DATA_DIR_NONVIP = 'data/non-vip'

def get_user_path(name):
    for folder in [DATA_DIR_VIP, DATA_DIR_NONVIP]:
        path = os.path.join(folder, f"{name}.plist")
        if os.path.isfile(path):
            return path
    return None

@record_bp.route('/user/<name>/add_record', methods=['GET', 'POST'])
def add_record(name):
    path = get_user_path(name)
    if not path:
        return f"用户{name}不存在", 404

    with open(path, encoding='utf-8') as f:
        user = json.load(f)

    if request.method == 'POST':
        change_str = request.form.get('change', '0').strip()
        note = request.form.get('note', '').strip()
        try:
            change = float(change_str)
        except ValueError:
            change = 0

        current_balance = user['records'][-1]['after_balance'] if user.get('records') else 0
        before_balance = current_balance
        after_balance = before_balance + change

        new_record = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "change": change,
            "before_balance": before_balance,
            "after_balance": after_balance
        }
        user.setdefault('records', []).append(new_record)

        # 更新备注
        user['note'] = note

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=2)

        return redirect(url_for('main.user_detail', name=name))

    return render_template('add_record.html', user=user)
