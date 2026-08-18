import schedule
import time


def start(job):

    schedule.every(
        7
    ).days.do(
        job
    )

    while True:

        schedule.run_pending()

        time.sleep(
            60
        )