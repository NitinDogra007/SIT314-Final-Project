import tkinter as tk
from tkinter import ttk
from pymongo.mongo_client import MongoClient
import json
import serial
import time

uri = "mongodb+srv://ndogra:sit314@sit314.rxnvgsq.mongodb.net/?retryWrites=true&w=majority"

# MongoDB connection
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["smart_lighting"]
collection = db["lighting_configurations"]

ser = serial.Serial('COM8', 9600)

# Function to send a command to the Arduino
def send_command(command):
    ser.write(command.encode('utf-8'))
    ser.write('\n'.encode('utf-8'))
    time.sleep(1)  # Allow some time for Arduino to process the command

# Functions to control individual color channels
def toggle_orange():
    orange_state = "on" if state_orange_var.get() == "off" else "off"
    state_orange_var.set(orange_state)# Update MongoDB and send commands to Arduino
    update_mongodb()

def toggle_green():
    green_state = "on" if state_green_var.get() == "off" else "off"
    state_green_var.set(green_state)
    # Update MongoDB and send commands to Arduino
    update_mongodb()

def toggle_blue():
    blue_state = "on" if state_blue_var.get() == "off" else "off"
    state_blue_var.set(blue_state)
    # Update MongoDB and send commands to Arduino
    update_mongodb()

# Function to save current settings to MongoDB
def update_mongodb():
    room_name = room_name_var.get()
    orange_state = state_orange_var.get()
    green_state = state_green_var.get()
    blue_state = state_blue_var.get()

    # Creates a document with the new settings
    new_settings = {
        "name": room_name,
        "color_channels": {
            "orange": orange_state,
            "green": green_state,
            "blue": blue_state
        }
    }

    # Update/insert the document in MongoDB
    collection.update_one({"name": room_name}, {"$set": new_settings}, upsert=True)

    # Send the updated settings to Arduino as a JSON command
    send_command(json.dumps(new_settings))

def load_settings():
    room_name = room_name_var.get()
    lighting_settings = collection.find_one({"name": room_name})
    
    if lighting_settings:
        # Debugging: Print the entire lighting_settings document
        print("Loaded Settings:", lighting_settings)
        
        state_orange = lighting_settings["color_channels"].get("orange")
        state_green = lighting_settings["color_channels"].get("green")
        state_blue = lighting_settings["color_channels"].get("blue")
        
        # Debugging: Print LED states
        print("Orange State:", state_orange)
        print("Green State:", state_green)
        print("Blue State:", state_blue)
        
        state_orange_var.set(state_orange)
        state_green_var.set(state_green)
        state_blue_var.set(state_blue)

        update_leds_based_on_settings()

            
    else:
        pass

# Updates the LEDs based on settings
def update_leds_based_on_settings():
    # Get the current state of the LED buttons
    orange_state = state_orange_var.get()
    green_state = state_green_var.get()
    blue_state = state_blue_var.get()
    
    # Create a dictionary with the new settings
    new_settings = {
        "color_channels": {
            "orange": orange_state,
            "green": green_state,
            "blue": blue_state
        }
    }

    # Send the updated settings to Arduino as a JSON command
    send_command(json.dumps(new_settings))

# Create the main application window
app = tk.Tk()
app.title("Smart Lighting Control")
app.configure(background='#1B2329')

# Sets the initial window size 
app.geometry("300x300")

button_width = 20  # button width
button_height = 2  # button height
button_padding = 5  # padding value

button_frame = tk.Frame(app, highlightbackground='white', highlightthickness=1)

# Create Room Name dropdown to select the room to load
ttk.Label(app, text="Select Room:").pack(pady=10)
room_names = [doc["name"] for doc in collection.find({}, {"name": 1, "_id": 0})]
room_name_var = tk.StringVar()
room_name_dropdown = ttk.Combobox(app, textvariable=room_name_var, values=room_names)
room_name_dropdown.pack(pady=button_padding)

# Create Orange LED button
orange_button = tk.Button(button_frame, text="Toggle Orange LED", command=toggle_orange, background='orange', foreground='white', width=button_width, height=button_height)
orange_button.pack()
button_frame.pack(pady=button_padding)
state_orange_var = tk.StringVar()
state_orange_var.set("off")  # Initial state is off

# Create Green LED button
green_button = tk.Button(button_frame, text="Toggle Green LED", command=toggle_green, background='lime green', foreground='white', width=button_width, height=button_height)
green_button.pack()
button_frame.pack(pady=button_padding)
state_green_var = tk.StringVar()
state_green_var.set("off")  # Initial state is off

# Create Blue LED button
blue_button = tk.Button(button_frame, text="Toggle Blue LED", command=toggle_blue, background='blue', foreground='white', width=button_width, height=button_height)
blue_button.pack()
button_frame.pack(pady=button_padding)
state_blue_var = tk.StringVar()
state_blue_var.set("off")  # Initial state is off

# Load button to load selected settings
load_button = tk.Button(app, text="Load Settings", command=load_settings)
load_button.pack(pady=3)

# Save button to save current settings
save_button = tk.Button(app, text="Save Settings", command=update_mongodb)
save_button.pack(pady=3)

# Run the application
app.mainloop()