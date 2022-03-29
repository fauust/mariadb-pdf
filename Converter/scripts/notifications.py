import plyer

def notify(formatted_time):
    plyer.notification.notify(
        title = "HTML Complete",
        message = f"Pdf Completion\nTime Taken: {formatted_time}",
        timeout = 3
    )