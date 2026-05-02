import re
import tkinter as tk

from ...base import AuthMode
from ...ui import Label, Card
from .sign_in import SignInFormCard
from .sign_up import SignUpFormCard

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthPage:
    def __init__(self, app):
        self.app = app
        self.sign_in_card = SignInFormCard(self)
        self.sign_up_card = SignUpFormCard(self)

    def render(self):
        self.app.clear_screen()
        wrapper = tk.Frame(self.app.main_frame, bg="#eef2f6")
        wrapper.pack(fill="both", expand=True)

        if self.app.auth_mode == AuthMode.SIGNUP.value:
            self.active_card = self.sign_up_card
            self.sign_up_card.render(wrapper)
            return

        self.active_card = self.sign_in_card
        self.sign_in_card.render(wrapper)

    def _build_card(self, wrapper, title, subtitle):
        card = Card(wrapper, padx=24, pady=24)
        card.pack(expand=True, ipadx=18, ipady=12)

        Label(card, "Project Approval Tracker", size=17, bold=True, fg="#1f2933").pack(anchor="w", pady=(14, 0))
        Label(card, title, size=14, bold=True, fg="#102a43").pack(anchor="w", pady=8)
        Label(card, subtitle, fg="#52606d", wraplength=500, justify="left").pack(anchor="w")

        self.auth_message = Label(card, "", bg="white", fg="#c0392b", size=9)
        self.auth_message.pack(anchor="w", pady=(10, 0))
        return card

    def _toggle_auth_mode(self):
        self.app.auth_mode = (
            AuthMode.SIGNUP.value
            if self.app.auth_mode == AuthMode.SIGNIN.value
            else AuthMode.SIGNIN.value
        )
        self.render()

    def _validate_email(self, email):
        if not email:
            raise ValueError("Email is required.")
        if not EMAIL_PATTERN.match(email):
            raise ValueError("Enter a valid email address.")

    def _validate_password(self, password):
        if not password:
            raise ValueError("Password is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

    def submit_auth(self):
        self.active_card.submit()
