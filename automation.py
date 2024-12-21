from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

def run_pipeline():
    subprocess.run(["ploomber", "build"], check=True)

scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, 'cron', hour=23, minute=59)
scheduler.start()