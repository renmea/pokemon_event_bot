from plyer import notification


def send(message):

    notification.notify(

        title="Pokemon Champions",

        message=message,

        timeout=10
    )