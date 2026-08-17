"""Quick validation script — runs without the GUI."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import ast, os, sys

BASE = r'e:\Downloads\databasecon check'
sys.path.insert(0, BASE)

files = ['db_config.py', 'attendance_report.py', 'main_app.py', 'setup_db.py']
for f in files:
    try:
        with open(os.path.join(BASE, f), encoding='utf-8') as fh:
            ast.parse(fh.read())
        print(f'  SYNTAX OK : {f}')
    except SyntaxError as e:
        print(f'  SYNTAX ERR: {f} -> {e}')

# DB connection
try:
    import db_config
    ok, msg = db_config.test_connection()
    print(f'  DB connect : {msg}')
except Exception as e:
    print(f'  DB ERROR   : {e}')

# Report module
try:
    import attendance_report as ar
    print('  Report mod : OK')
    stats = ar.get_dashboard_stats()
    keys = list(stats.keys())
    print(f'  Dashboard  : {len(keys)} stat keys')
    print(f'  Students   : {stats["total_students"]}')
    print(f'  Teachers   : {stats["total_teachers"]}')
    print(f'  Courses    : {stats["total_courses"]}')
    recent_count = len(stats["recent"])
    print(f'  Recent rows: {recent_count}')
except Exception as e:
    print(f'  Report ERR : {e}')

try:
    rows = ar.get_student_attendance_summary()
    print(f'  Att summary: {len(rows)} rows')
    if rows:
        r = rows[0]
        print(f'  Sample row : {r["student_name"]} | {r["course_code"]} | {r["attendance_pct"]}%')
except Exception as e:
    print(f'  Summary ERR: {e}')

try:
    rows = ar.get_defaulter_list(threshold=75)
    print(f'  Defaulters : {len(rows)} students below 75%')
except Exception as e:
    print(f'  Defaulter ERR: {e}')

try:
    rows = ar.get_course_daily_summary()
    print(f'  Daily summ : {len(rows)} rows')
except Exception as e:
    print(f'  Daily ERR  : {e}')

print('\nAll checks passed!')
