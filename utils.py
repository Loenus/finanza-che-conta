import datetime

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def check_jobs(job_queue):
    job_names = [job.name for job in job_queue.jobs()]
    print(job_names)
    primo = job_queue.jobs()[0]
    next_run_time = primo.next_t
    print(f"Next run of the job is scheduled at: {next_run_time}")

