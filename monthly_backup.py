# monthly_backup.py（不变）

import os
import json
import shutil
import datetime

DATA_DIR_VIP = "data/vip"
DATA_DIR_NONVIP = "data/non-vip"
BACKUP_ROOT = "backup"

def backup_and_clear_records():
    today = datetime.date.today()
    if today.day != 1:
        # 不是每月1号，不备份
        return

    backup_dir = os.path.join(BACKUP_ROOT, str(today.year), f"{today.month:02d}")
    os.makedirs(backup_dir, exist_ok=True)

    for folder in [DATA_DIR_VIP, DATA_DIR_NONVIP]:
        for filename in os.listdir(folder):
            if not filename.endswith(".plist"):
                continue
            src_path = os.path.join(folder, filename)
            dst_path = os.path.join(backup_dir, filename)

            shutil.copy2(src_path, dst_path)

            with open(src_path, encoding="utf-8") as f:
                data = json.load(f)
            data["records"] = []
            with open(src_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Backup] {today} 备份完成，目录: {backup_dir}")
