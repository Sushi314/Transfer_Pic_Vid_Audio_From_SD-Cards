import os
import shutil
import datetime
import time
import subprocess
import win32gui
import win32con
import win32api

#Note to future self it uses current year for "start_date" and "end_date"

source_folder = r"C:\Users\Sushi\Pictures\Random Pics"
screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)


def user_input_yes_no_to_confirm(prompt, no_message):
    while True:
        user_input_confirm = input(prompt +" Yes / No: ").lower()
        if user_input_confirm in ["yes", "ya", "y", "true"]:
            return True
        elif user_input_confirm in ["no", "nope", "na", "n", "false"]:
            print(no_message)
            return False  
        else:
            print("Not a valid response. Please try again.")


def move_terminal_window():

    terminal_handle = win32gui.GetForegroundWindow()

    window_width = screen_width // 2  
    window_height = screen_height // 2  
    x = screen_width - window_width
    y = 0
    win32gui.MoveWindow(terminal_handle, x, y, window_width, window_height, True)

move_terminal_window()


def open_file_explorer(folder_path):
    # Convert folder path to absolute path
    folder_path = os.path.abspath(folder_path)

    # Open File Explorer window
    process = subprocess.Popen(f'explorer "{folder_path}"')
    process.wait()
    time.sleep(.1)

    # Get the handle of the File Explorer window
    file_explorer_handle = None
    while not file_explorer_handle:
        file_explorer_handle = win32gui.FindWindow("CabinetWClass", None)
    
    x_window_postion = 0
    y_window_postion = 0
    width = screen_width // 2  
    height = screen_height // 1
    win32gui.MoveWindow(file_explorer_handle, x_window_postion, y_window_postion, width, height, True)
    details_view_message = win32con.WM_COMMAND
    details_view_command = 41504  # Command ID for "Details" view
    win32gui.SendMessage(file_explorer_handle, details_view_message, details_view_command, 0)

open_file_explorer(source_folder)

def get_start_end_dates():
    today = datetime.date.today()
    current_year = today.year
    print(today)
    start_date = None
    end_date = None

    # Get the start date from the user
    while start_date is None:
        if user_input_yes_no_to_confirm("Use todays date for start date?", ""):
            start_date = today
        else:
            while True:
                start_date_input = input("Enter the start date (older) (MM DD): ")
                try:
                    start_date = datetime.datetime.strptime(f"{current_year} {start_date_input}", "%Y %m %d").date()
                    if start_date >= today:
                        print("Start date cannot be in the future.")
                    else:
                        break
                except ValueError:
                    print("Invalid date format. Please use the format: MM DD")

    print("Start date is", start_date)

    # Get the end date from the user
    while end_date is None:
        if user_input_yes_no_to_confirm("Use todays date for end date?", ""):
            end_date = today
        else:
            while True:
                end_date_input = input("Enter the end date (newer)(MM DD): ")
                try:
                    end_date = datetime.datetime.strptime(f"{current_year} {end_date_input}", "%Y %m %d").date()
                    if end_date <= today and end_date >= start_date:
                        break
                    elif end_date < start_date:
                        print("End date cannot be before the start date.")
                    elif end_date > today:
                        print("End date cannot be in the future.")
                except ValueError:
                    print("Invalid date format. Please use the format: MM DD")
            break
    print("End date is", end_date)

    select_files_from_date_range(start_date, end_date)
                

def select_files_from_date_range(start_date, end_date):
    selected_dates = []
    selected_files = []

    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            if file_name.lower().endswith((".arw", ".jpg")):
                file_path = os.path.join(root, file_name)
                modified_date = datetime.date.fromtimestamp(os.path.getmtime(file_path))
                if start_date <= modified_date <= end_date:
                    selected_files.append((file_path, modified_date))
                    formatted_date = modified_date.strftime("%Y-%m-%d")
                    if formatted_date not in selected_dates:
                        selected_dates.append(formatted_date)
            else:
                print(file_name, "is not a .jpg or .arw")

    if len(selected_files) == 0:
        print("No files selected.")
        while True:
            if user_input_yes_no_to_confirm("Would you like to startover?", "Program will terminate."):
                get_start_end_dates()
            else:
                time.sleep(1)
                quit()
                
    if len(selected_files) >= 1:
        for item in selected_dates:
            print("Date of file:", item)
        for item in selected_files:
            print("File selected:", item[0], " - ", item[1])

        create_folders_by_date(selected_dates, selected_files)


def create_folders_by_date(selected_dates, selected_files):
    target_directory_base = r"C:\Users\Sushi\Pictures\\"     
    if user_input_yes_no_to_confirm("Create folders at: " + target_directory_base, "Will not create folders at: " + target_directory_base):
        open_file_explorer(target_directory_base)
        for item in selected_dates:
            folder_name = item
            target_directory = os.path.join(target_directory_base, folder_name)
            os.makedirs(target_directory, exist_ok=True)
            
            arw_folder_path = os.path.join(target_directory, "ARW")
            os.makedirs(arw_folder_path, exist_ok=True)

            print("Created folder:", target_directory)
            print("Created folder:", arw_folder_path)

    else:
        while True:
            input_target_directory = input("What directory would you like to use?").strip('"\'')
            if not os.path.isdir(input_target_directory):
                print("Not a valid directory. Please try again.")
            else:
                open_file_explorer(input_target_directory)
                for item in selected_dates:
                    folder_name = item
                    target_directory = os.path.join(input_target_directory, folder_name)
                    os.makedirs(target_directory, exist_ok=True)
                    
                    arw_folder_path = os.path.join(target_directory, "ARW")
                    os.makedirs(arw_folder_path, exist_ok=True)

                    print("Created folder:", target_directory)
                    print("Created folder:", arw_folder_path)
                break
    copy_files_to_folders(selected_files, target_directory_base)

def copy_files_to_folders(selected_files, target_directory_base):
    for item in selected_files:
        file_name = item[0]
        file_date = item[1]
        destination_file_path = os.path.join(target_directory_base, str(file_date))

        if item[0].lower().endswith("jpg"):
            shutil.copy(file_name, destination_file_path)
            print("Copied file:", file_name, "to", destination_file_path)
        elif item[0].lower().endswith(".arw"):
            arw_destination_file_path = os.path.join(destination_file_path, "ARW")
            shutil.copy(file_name, arw_destination_file_path)
            print("Copied file:", file_name, "to", arw_destination_file_path)
        else:
            print("File is not a .jpg or .arw", file_name)         

    print("Files transferred successfully!")
    input("Process completed. Press Enter to exit...")

get_start_end_dates()
