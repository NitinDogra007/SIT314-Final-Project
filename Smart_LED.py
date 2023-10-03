import tkinter as tk
from tkinter import ttk
from pymongo.mongo_client import MongoClient
import json
import serial
import time

uri = "mongodb+srv://ndogra:sit314@sit314.rxnvgsq.mongodb.net/?retryWrites=true&w=majority"

# MongoDB connection
client = MongoClient(uri)  # Update with your MongoDB connection details

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

# Function to save current settings to MongoDB
def save_settings():
    room_name = room_name_var.get()
    orange_state = state_orange_var.get()
    green_state = state_green_var.get()
    blue_state = state_blue_var.get()
    
    # Create a document with the new settings
    new_settings = {
        "name": room_name,
        "color_channels": {
            "orange": orange_state,
            "green": green_state,
            "blue": blue_state
        }
    }
    
    # Update or insert the document in MongoDB
    collection.update_one({"name": room_name}, {"$set": new_settings}, upsert=True)
    
    # Send the updated settings to Arduino as a JSON command
    send_command(json.dumps(new_settings))

    # Update LEDs based on the new settings
    update_leds_based_on_settings(orange_state, green_state, blue_state)

# Functions to control individual color channels
def toggle_orange():
    orange_state = "on" if state_orange_var.get() == "off" else "off"
    state_orange_var.set(orange_state)# Update MongoDB and send commands to Arduino
    update_mongodb()
    # Add the following line to send the 'G' command to Arduino
    send_command('O')

def toggle_green():
    green_state = "on" if state_green_var.get() == "off" else "off"
    state_green_var.set(green_state)
    # Update MongoDB and send commands to Arduino
    update_mongodb()
    # Add the following line to send the 'G' command to Arduino
    send_command('G')

def toggle_blue():
    blue_state = "on" if state_blue_var.get() == "off" else "off"
    state_blue_var.set(blue_state)
    # Update MongoDB and send commands to Arduino
    update_mongodb()
    # Add the following line to send the 'G' command to Arduino
    send_command('B')

# Function to save current settings to MongoDB
def update_mongodb():
    room_name = room_name_var.get()
    orange_state = state_orange_var.get()
    green_state = state_green_var.get()
    blue_state = state_blue_var.get()

    # Create a document with the new settings
    new_settings = {
        "name": room_name,
        "color_channels": {
            "orange": orange_state,
            "green": green_state,
            "blue": blue_state
        }
    }

    # Update or insert the document in MongoDB
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
        
        #Update the LEDs based on the loaded settings
        if state_orange == "on":
            toggle_orange()
        elif state_orange == "off":
            pass
        if state_green == "on":
            toggle_green()
        elif state_green == "off":
            pass
        if state_blue == "on":
            toggle_blue()
        elif state_blue == "off":
            pass

            
    else:
        # Handle case when no settings are found in MongoDB
        pass

# Define the function that updates the LEDs based on settings
def update_leds_based_on_settings(orange_state, green_state, blue_state):
    if orange_state == "on":
        toggle_orange()
    elif orange_state == "off":
        pass

    if green_state == "on":
        toggle_green()
    elif green_state == "off":
        pass

    if blue_state == "on":
        toggle_blue()
    elif blue_state == "off":
        pass

# Create the main application window
app = tk.Tk()
app.title("Smart Lighting Control")
app.configure(background='#1B2329')

# Set the initial window size (width x height)
app.geometry("300x300")  # Adjust the dimensions as needed

button_width = 20  # Set your desired button width
button_height = 2  # Set your desired button height
button_padding = 5  # Set your desired padding value

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
save_button = tk.Button(app, text="Save Settings", command=save_settings)
save_button.pack(pady=3)

# Run the application
app.mainloop()