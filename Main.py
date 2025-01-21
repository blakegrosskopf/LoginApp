from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
import sqlite3
import re

class homeScreen(Screen):
    dialog = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    def verify(self, user, psswd):
        database = "users.db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (user, psswd))
        result = cursor.fetchone()
        if result:
            self.show_popup("Success", "Login successful!")
            self.manager.current = 'sScreen'
        else:
            self.show_popup("Error", "Invalid email or password.")
        conn.close()
        self.clear_fields()
    def clear_fields(self):
        """Function to clear input fields."""
        self.ids.user.text = ""
        self.ids.psswd.text = ""

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
                cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (username, password))
                conn.commit()
                self.show_popup("Success!","Account created successfully!")
            except sqlite3.IntegrityError:
                self.show_popup("Error.",'Account with email already exists.')
            finally:
                conn.close()
                self.clear_fields()
        else:
            self.show_popup("Error",'Password must contain at least 8 characters, a capital letter, special character, and a number.')
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
