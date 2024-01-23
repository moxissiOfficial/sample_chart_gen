# fmt: off
from datetime import datetime
from engineio.async_drivers import eventlet
from eventlet.hubs import epolls, kqueue, selects
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from RemoveFiles import RemoveFiles
from OutputDataframe import OutputDataframe
import pandas as pd
import os
import tkinter as tk
from tkinter import ttk
import ctypes
import json
import math

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import matplotlib
matplotlib.use('SVG')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


rf = RemoveFiles()
od = OutputDataframe()
selected_files = {}

# GLOBALS
annotations = []
tables = []
df = pd.DataFrame()

app = Flask(__name__, template_folder='./templates')
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

UPLOAD_FOLDER = ".\\uploads"
EXPORT_FOLDER = ".\\exports"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


###############################
# ROUTES
###############################
@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/upload", methods=["POST"])
def upload():
    socketio.emit('loading', "Loading data from files...")
    global selected_files
    selected_files = {}
    rf.remove_files(UPLOAD_FOLDER)
    if "files" not in request.files:
        return "No file part"

    files = request.files.getlist("files")
    key_file = request.files.getlist("key_file")

    for file in files:
        if file.filename == "":
            print("No file selected")
        else:
            # Save file to UPLOAD_FOLDER
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            # Link file names and paths to selected_files Dict
            selected_files[secure_filename(file.filename)] = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    
    if key_file[0].filename == "":
            print("No selected file IQRFSvr.dbf")
    else:
        key_file[0].save(os.path.join(app.config['UPLOAD_FOLDER'], key_file[0].filename))
        selected_files[secure_filename(key_file[0].filename)] = os.path.join(app.config["UPLOAD_FOLDER"], key_file[0].filename)

    annotations.clear()
    socketio.emit('update_annotations', {'message': annotations})
    return redirect("/table")


@app.route('/table', methods=("POST", "GET"))
def html_table():
    socketio.emit('loading', "Loading data from files...")
    global tables
    global df
    df = data_frame()

    if df is None:
        print("Dataframe not found.")
    else:
        sensor_list = list(df.columns)
        first_timestamp_row = df[['TIMESTAMP']].head(1).to_json(orient='records')
        last_timestamp_row = df[['TIMESTAMP']].tail(1).to_json(orient='records')

        socketio.emit('first_last_timestamp_row', {'first_timestamp_row': json.loads(first_timestamp_row), 'last_timestamp_row': json.loads(last_timestamp_row)})
        socketio.emit('sensor_list', {'message' : sensor_list})
        socketio.emit('loading', "Data from files loaded!")
        show_table_ttk()
        return '', 204

def show_table_ttk():
    socketio.emit('loading', "Creating table...")
    # Get screen dimensions
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # Create Tkinter main window with initial size
    root = tk.Tk()
    root.title(list(selected_files.keys())[0])
    initial_width = screen_width // 2
    initial_height = screen_height // 2
    root.geometry(f"{initial_width}x{initial_height}+0+0")
    root.attributes('-topmost', True) 

    # Create a tree widget
    tree = ttk.Treeview(root)

    # Definition of columns
    tree["columns"] = tuple(df.columns)
    tree["show"] = "headings"  # Skryje první prázdný sloupec

    # Add columns to tree widget with dynamic width
    for col in df.columns:
        max_len = max(df[col].astype(str).apply(lambda x: len(x)).max(), len(col))
        tree.heading(col, text=col)
        tree.column(col, width=max_len * 10, anchor="center")  # Nastavte šířku podle maximální délky textu

    # Adding data to the table
    for _, row_values in df.iterrows():
        tree.insert("", "end", values=tuple(row_values))

    # Create sliders
    y_scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    y_scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=y_scrollbar.set)

    x_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    x_scrollbar.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=x_scrollbar.set)

    # Location of the tree widget
    tree.pack(fill="both", expand=True)

    socketio.emit('loading', "Table loaded!")
    # Start Tkinter's main loop
    root.mainloop()

@socketio.on('add_annotation')
def add_annotation(data):
    date_time = data['data']['date_time']
    annotation = data['data']['annotation']
    annotations.append((date_time, annotation))
    socketio.emit('update_annotations', {'message': annotations})

@socketio.on('remove_annotation')
def remove_annotation(data):
    ann = data["data"].split("_")
    annotation_to_remove = ((ann[0], ann[1]))
    
    if annotation_to_remove in annotations:
        annotations.remove(annotation_to_remove)

    socketio.emit('update_annotations', {'message': annotations})

@socketio.on('create_chart')
def create_chart(data):
    print("CHART REQ...")
    print(data)
    socketio.start_background_task(target=create_chart_img2, data=data)

def create_chart_img2(data):
    pass
# More code removed..

###############################
# //ROUTES
###############################


##################################
# Functions
##################################

def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Folder '{folder}' created!")

def data_frame():
    return od.get_final_dataframe(selected_files.values())

##################################
# //Functions
##################################

if __name__ == "__main__":
    make_folder(UPLOAD_FOLDER)
    make_folder(EXPORT_FOLDER)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    #serve(app, host='127.0.0.1', port=5000)
