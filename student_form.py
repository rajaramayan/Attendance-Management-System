import os
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    tk = None
    messagebox = None
import mysql.connector


# ---------------------------------------------------
# FUNCTION TO CONNECT TO MYSQL
# ---------------------------------------------------

def connect_database():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "YOUR_DB_PASSWORD"),
        database=os.getenv("DB_NAME", "college")
    )

    return connection


# ---------------------------------------------------
# FUNCTION TO SAVE STUDENT
# ---------------------------------------------------

def save_student():

    # Get values from the Entry widgets
    roll_no = roll_entry.get()
    name = name_entry.get()
    address = address_entry.get()
    dob = dob_entry.get()

    # Check whether fields are empty
    if roll_no == "" or name == "" or address == "" or dob == "":
        messagebox.showwarning(
            "Missing Data",
            "Please enter all fields."
        )
        return

    try:

        # Connect to MySQL
        connection = connect_database()

        # Create cursor
        cursor = connection.cursor()

        # SQL INSERT statement
        sql = """
        INSERT INTO student
        (Roll_no, Name, Address, Dob)
        VALUES (%s, %s, %s, %s)
        """

        # Values to be inserted
        values = (
            roll_no,
            name,
            address,
            dob
        )

        # Execute SQL
        cursor.execute(sql, values)

        # Save permanently
        connection.commit()

        # Display success message
        messagebox.showinfo(
            "Success",
            "Student record saved successfully!"
        )

        # Clear the form
        clear_form()

        # Close cursor and connection
        cursor.close()
        connection.close()

    except mysql.connector.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Error while saving record:\n\n{error}"
        )


# ---------------------------------------------------
# FUNCTION TO CLEAR FORM
# ---------------------------------------------------

def clear_form():

    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    dob_entry.delete(0, tk.END)

    roll_entry.focus()


# ---------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------

root = tk.Tk()

root.title("College - Student Entry")

root.geometry("550x450")

root.resizable(False, False)


# ---------------------------------------------------
# HEADING
# ---------------------------------------------------

heading = tk.Label(
    root,
    text="COLLEGE DATABASE SYSTEM",
    font=("Arial", 20, "bold")
)

heading.pack(pady=(20, 5))


sub_heading = tk.Label(
    root,
    text="Student Entry Form",
    font=("Arial", 14)
)

sub_heading.pack(pady=(0, 20))


# ---------------------------------------------------
# FORM FRAME
# ---------------------------------------------------

form_frame = tk.Frame(root)

form_frame.pack()


# ---------------------------------------------------
# ROLL NUMBER
# ---------------------------------------------------

tk.Label(
    form_frame,
    text="Roll No:",
    font=("Arial", 12)
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="e"
)

roll_entry = tk.Entry(
    form_frame,
    width=30,
    font=("Arial", 12)
)

roll_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)


# ---------------------------------------------------
# NAME
# ---------------------------------------------------

tk.Label(
    form_frame,
    text="Name:",
    font=("Arial", 12)
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="e"
)

name_entry = tk.Entry(
    form_frame,
    width=30,
    font=("Arial", 12)
)

name_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)


# ---------------------------------------------------
# ADDRESS
# ---------------------------------------------------

tk.Label(
    form_frame,
    text="Address:",
    font=("Arial", 12)
).grid(
    row=2,
    column=0,
    padx=10,
    pady=10,
    sticky="e"
)

address_entry = tk.Entry(
    form_frame,
    width=30,
    font=("Arial", 12)
)

address_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=10
)


# ---------------------------------------------------
# DATE OF BIRTH
# ---------------------------------------------------

tk.Label(
    form_frame,
    text="Date of Birth:",
    font=("Arial", 12)
).grid(
    row=3,
    column=0,
    padx=10,
    pady=10,
    sticky="e"
)

dob_entry = tk.Entry(
    form_frame,
    width=30,
    font=("Arial", 12)
)

dob_entry.grid(
    row=3,
    column=1,
    padx=10,
    pady=10
)


# ---------------------------------------------------
# BUTTON FRAME
# ---------------------------------------------------

button_frame = tk.Frame(root)

button_frame.pack(pady=25)


# ---------------------------------------------------
# SAVE BUTTON
# ---------------------------------------------------

save_button = tk.Button(
    button_frame,
    text="Save",
    width=12,
    font=("Arial", 11, "bold"),
    command=save_student
)

save_button.grid(
    row=0,
    column=0,
    padx=10
)


# ---------------------------------------------------
# CLEAR BUTTON
# ---------------------------------------------------

clear_button = tk.Button(
    button_frame,
    text="Clear",
    width=12,
    font=("Arial", 11),
    command=clear_form
)

clear_button.grid(
    row=0,
    column=1,
    padx=10
)


# ---------------------------------------------------
# EXIT BUTTON
# ---------------------------------------------------

exit_button = tk.Button(
    button_frame,
    text="Exit",
    width=12,
    font=("Arial", 11),
    command=root.destroy
)

exit_button.grid(
    row=0,
    column=2,
    padx=10
)


# ---------------------------------------------------
# START APPLICATION
# ---------------------------------------------------

roll_entry.focus()

root.mainloop()