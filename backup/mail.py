
import textwrap
import datetime


def current_week():
    'Returns the current week.'
    return datetime.datetime.now().isocalendar()[1]


def generate_report(server_stats, week_nr):
    report_contents = textwrap.dedent(f'''
    Weekly backup report for week {week_nr}.

    List of backupped servers:

    ''')
    report_contents += '\n'.join([server.report for server in server_stats])
    report_contents += textwrap.dedent(f'''

    Sincerely,

    Your serverless backup service.
    ''')
    return report_contents


def send_backup_summary(backup_stats):
    week = current_week()
    report = generate_report(backup_stats, week)
