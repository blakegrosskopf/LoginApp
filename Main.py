from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import sqlite3
import re
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText

SENDER_EMAIL = "explodingbcraft@gmail.com"
SENDER_PASSWORD = "ambd tvct exae wchi"




class homeScreen(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def show_popup(self, title, message):
        if self.dialog:
            self.dialog.dismiss()  # Dismiss any existing dialog

        self.dialog = MDDialog(
            title=title,
            text=message,
            size_hint=(0.8, 0.4),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def verify(self, user, psswd):
        database = "users.db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        try:
            # Select only the password column
            cursor.execute('SELECT password FROM users WHERE email = ?', (user,))
            result = cursor.fetchone()

            if result:
                stored_hashed_password = result[0]

                # Ensure stored password is a string and correctly formatted
                if isinstance(stored_hashed_password, bytes):
                    stored_hashed_password = stored_hashed_password.decode('utf-8')
                elif isinstance(stored_hashed_password, int):
                    stored_hashed_password = str(stored_hashed_password)

                # Verify password
                if bcrypt.checkpw(psswd.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    self.show_popup("Success", "Login successful!")
                    self.clear_fields()
                    self.manager.current = 'sScreen'
                    conn.close()
                    return True
                else:
                    self.show_popup("Error", "Invalid email or password.")
                    self.clear_fields()
                    conn.close()
                    return False
            else:
                self.show_popup("Error", "User not found.")
                self.clear_fields()
                conn.close()
                return False
        except sqlite3.Error as e:
            self.show_popup("Error", f"Database error: {e}")
            conn.close()
            return False

    def clear_fields(self):
        """Function to clear input fields."""
        self.ids.user.text = ""
        self.ids.psswd.text = ""


def validateEmail(email):
    pattern = (r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
           r"@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")
    return re.match(pattern, email) is not None


class signUp(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    dialog = None  # Store the dialog to avoid creating multiple instances

    def show_popup(self, title, message):
        """Function to display pop-up dialogs."""
        if self.dialog:
            self.dialog.dismiss()  # Dismiss any existing dialog

        self.dialog = MDDialog(
            title=title,
            text=message,
            size_hint=(0.8, 0.4),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def create_user(self, username, password):
        if validateEmail(username):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            database = "users.db"
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password TEXT
                )
            ''')
            pattern = r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
            if re.match(pattern, password):
                try:
                    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (username, hashed_password))
                    conn.commit()
                    self.show_popup("Success!","Account created successfully!")
                except sqlite3.IntegrityError:
                    self.show_popup("Error.",'Account with email already exists.')
                finally:
                    conn.close()
                    self.clear_fields()
            else:
                self.show_popup("Error",'Password must contain at least 8 characters, a capital letter, special character, and a number.')
        else:
            self.show_popup("Error",'Email is invalid.')
            self.manager.current = 'signUp'

    def clear_fields(self):
        """Function to clear input fields."""
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""

class sScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        sm = ScreenManager()
        sm.add_widget(homeScreen(name='home'))
        sm.add_widget(signUp(name='signUp'))
        sm.add_widget(sScreen(name='sScreen'))
        return sm

if __name__ == "__main__":
    Window.size = (360, 640)
    Builder.load_file("main.kv")
    MyApp().run()




# Function to generate a verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))  # Generates a random 6-digit code


# Function to send verification email
def send_verification_email(user_email):
    verification_code = generate_verification_code()

    # Email content
    subject = "Your Email Verification Code"
    body = f"Your verification code is: {verification_code}"

    # Create email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = user_email

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Start encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        server.quit()

        print(f"Verification email sent to {user_email}")
        return verification_code  # Return code to verify later

    except Exception as e:
        print("Error sending email:", e)
        return None
