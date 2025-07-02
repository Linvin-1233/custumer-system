from flask import Flask
from views_main import main_bp
from views_record import record_bp
from monthly_backup import backup_and_clear_records

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'change-this-to-your-secret-key'

app.register_blueprint(main_bp)
app.register_blueprint(record_bp)

scheduler = BackgroundScheduler()

# 每天凌晨0点执行备份函数
scheduler.add_job(backup_and_clear_records, 'cron', hour=0, minute=0)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
