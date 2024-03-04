# codetable.py

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import venv
import shutil
import atexit
import textwrap

# Directory for the virtual environment
venv_dir = "AG\\temp_pipinstalls"

# Ensure the directory exists and create a virtual environment there
if not os.path.exists(venv_dir):
    venv.create(venv_dir, with_pip=True)

# Path to the Python executable in the virtual environment
venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')


# Function to clean up the virtual environment directory upon program exit
def cleanup_venv():
    if os.path.exists(venv_dir):
        shutil.rmtree(venv_dir)


# Register the cleanup function with atexit
atexit.register(cleanup_venv)


# Function to execute pip install commands within the virtual environment
def execute_pip_install(command):
    try:
        subprocess.run(f"{venv_python} -m pip install {command}",
                       shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "Package installed successfully.\n"
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}\n"


# Function to execute the code from the text field within the virtual environment
def execute_code(code_to_run):
    # Check if the code contains a pip install command
    if 'pip install' in code_to_run:
        # Split the code into pip install command and the rest of the Python code
        pip_command, _, rest_of_code = code_to_run.partition('\n')  # This assumes pip install is on its own line
        pip_result = execute_pip_install(pip_command.strip())

        # Dedent the rest of the code to ensure proper indentation
        dedented_code = textwrap.dedent(rest_of_code)

        # Execute the dedented Python code
        python_result = execute_python_code(dedented_code)
        return pip_result + python_result
    else:
        # If no pip install, execute the code as normal
        return execute_python_code(code_to_run)


def execute_python_code(commands):
    try:
        process = subprocess.run([venv_python, '-c', commands],
                                 capture_output=True, text=True, check=True)
        return process.stdout if process.stdout else "Execution completed successfully.\n"
    except subprocess.CalledProcessError as e:
        return e.stderr + "\n"


# New function to be called from main.py for direct code execution
def external_execute_code(code):
    result = execute_code(code)
    return result


# GUI setup for standalone execution
def setup_gui(window):
    global code_input, output_text, output_label, execute_button

    window.title("Code Execution Table")
    code_input = scrolledtext.ScrolledText(window, height=20, width=60)
    code_input.pack()

    output_text = tk.StringVar()
    output_label = tk.Label(window, textvariable=output_text, bg='white', relief='sunken', anchor='w', justify='left')
    output_label.pack(fill='both', expand=True)

    execute_button = tk.Button(window, text="Execute",
                               command=lambda: output_text.set(external_execute_code(code_input.get("1.0", tk.END))))
    execute_button.pack()


# For standalone operation, create a root window and set up the GUI
if __name__ == "__main__":
    root = tk.Tk()
    setup_gui(root)
    root.mainloop()
