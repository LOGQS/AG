# main.py

import tkinter as tk
from tkinter import scrolledtext, font
import pyautogui
import os
import threading
import re
from llm import query_llm, update_text_list
from codetable import external_execute_code  # Make sure this is correctly defined in codetable.py

llm_chat_history = ""  # Initialize the chat history variable

# Define the main application window
root = tk.Tk()
root.title("LLM Chat Interface")
root.attributes('-topmost', True)

# Define fonts and colors
large_font = font.Font(family="Helvetica", size=14)
user_bg = '#A9A9A9'  # Dark grey for user messages
llm_bg = '#696969'  # Darker grey for LLM messages
first_msg_bg = '#FF2700'  # Red background for the first message
text_color = 'black'  # Black text for better contrast on dark background


def send_message(event=None):
    user_message = user_input.get()
    if user_message.strip() != "":
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, f"You: {user_message}\n", 'user')
        chat_history.config(state=tk.DISABLED)
        user_input.delete(0, tk.END)

        # Run LLM query in a separate thread to avoid freezing the GUI
        threading.Thread(target=query_llm_thread, args=(user_message,)).start()


def query_llm_thread(user_message):
    global llm_chat_history
    screenshot_path = r"current_screen\current_screen.png"
    if os.path.exists(screenshot_path):
        update_text_list(screenshot_path)  # Update text_list before calling query_llm

    response = query_llm(screenshot_path, user_message, chat_history=llm_chat_history)

    chat_response, execute_code, summary = "", "", ""

    try:
        content = response['choices'][0]['message']['content']
        print(content)

        # Extracting chat history from the model's response
        llm_chat_history_match = re.search(r"Chat history for the next assistant##(.*)", content)
        if llm_chat_history_match:
            llm_chat_history = llm_chat_history_match.group(1).strip()
            print(f"this is the {llm_chat_history}")

        chat_match = re.search(r"CHAT##(.*)", content)
        if chat_match:
            chat_response = chat_match.group(1).strip()
            print(chat_response)

        # Updated regex to match the new output format without triple backticks
        execute_match = re.search(r"EXECUTE_CODE##(.*?)Summary##", content, re.DOTALL)
        if execute_match:
            execute_code = execute_match.group(1).strip()
            # Assuming the external_execute_code function is defined elsewhere to handle the code execution
            external_execute_code(execute_code)

        summary_match = re.search(r"Summary##(.*)", content)
        if summary_match:
            summary = summary_match.group(1).strip()

        # GUI update with chat response
        chat_history.config(state=tk.NORMAL)
        if chat_response:
            chat_history.insert(tk.END, f"LLM: {chat_response}\n", 'llm')
        chat_history.config(state=tk.DISABLED)

        # Execute code if it's present in the response
        if execute_code:
            print("Code to execute:", execute_code)  # For debugging

        chat_history.see(tk.END)  # Scroll to the bottom

    except KeyError:
        # Handle case where expected data isn't in the response
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "LLM: Error retrieving response.\n", 'llm')
        chat_history.config(state=tk.DISABLED)

    # Attempt to delete the screenshot after processing
    try:
        os.remove(screenshot_path)
    except OSError as e:
        print(f"Error: {screenshot_path} : {e.strerror}")


def take_screenshot():
    # Temporarily hide the window to take a screenshot
    root.attributes('-alpha', 0.0)
    root.update()
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    screenshot_path = r"current_screen\current_screen.png"
    # Make sure the directory exists
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    # Save the screenshot
    screenshot.save(screenshot_path)
    # Make the window visible again
    root.attributes('-alpha', 1.0)


# Text widget for the chat history
chat_history = scrolledtext.ScrolledText(root, font=large_font, bg=text_color, fg=text_color, padx=10, pady=10)
chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_history.tag_configure('user', background=user_bg)
chat_history.tag_configure('llm', background=llm_bg)
chat_history.tag_configure('first', background=first_msg_bg)

# Entry widget for user input
user_input = tk.Entry(root, font=large_font, bg='white', fg=text_color)
user_input.pack(padx=10, pady=10, fill=tk.X)
user_input.bind("<Return>", send_message)  # Bind the Enter key to send message

# Buttons for adding a screenshot and sending a message
add_ss_button = tk.Button(root, text="Add Current SS", font=large_font, command=take_screenshot)
add_ss_button.pack(side=tk.RIGHT, padx=10, pady=10)

send_button = tk.Button(root, text="Send Message", font=large_font, command=send_message)
send_button.pack(side=tk.LEFT, padx=10, pady=10)

# Static message added when the GUI starts
chat_history.config(state=tk.NORMAL)
chat_history.insert(tk.END, "Welcome to your Personal PC Assistant. What can I do for you?\n", 'first')
chat_history.config(state=tk.DISABLED)

# Start the Tkinter event loop
root.mainloop()
