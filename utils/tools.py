import os
import subprocess

import pywhatkit


def play_youtube(query):
    """
    Search for and play a YouTube video.
    """

    pywhatkit.playonyt(
        query
    )

def send_whatsapp(phone, message):
    """
    Send a WhatsApp message using WhatsApp Web.
    """

    pywhatkit.sendwhatmsg_instantly(
        phone,
        message,
        wait_time=15,
        tab_close=False
    )


def open_file(file_path):
    """
    Open a file using the default Windows application.
    """

    file_path = os.path.abspath(
        file_path.strip()
    )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    os.startfile(file_path)


def open_app(app_path):
    """
    Open a Windows application using its exact path.
    """

    app_path = os.path.abspath(
        app_path.strip()
    )

    if not os.path.exists(app_path):

        raise FileNotFoundError(
            f"Application does not exist: {app_path}"
        )

    subprocess.Popen(
        [app_path]
    )