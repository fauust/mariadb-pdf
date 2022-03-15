import plyer

def notify_html(r_time, g_time):
    plyer.notification.notify(
        title = "HTML Complete",
        message = f"Request Time: {r_time}\nGeneration Time: {g_time}",
        timeout = 3
    )


def notify_pdf(time):
    plyer.notification.notify(
        title = "PDF Complete",
        message = f"Time Taken: {time}",
        timeout = 3
    )

