from ...ui import Button, Label, EntryField


class SignInFormCard:
    def __init__(self, page):
        self.page = page

    def render(self, wrapper):
        card = self.page._build_card(
            wrapper,
            "Sign In",
            "Sign in with the email and password you created in this app.",
        )

        self.page.email_field = EntryField(card, "Email")
        self.page.email_field.pack(fill="x")

        self.page.password_field = EntryField(card, "Password", show="*")
        self.page.password_field.pack(fill="x")
        self.page.password_field.bind("<Return>", lambda _event: self.submit())

        Button(
            card, 
            "Sign In",
            self.submit,
            primary=True
        ).pack(fill="x", pady=(18, 10))

        Button(
            card,
            text="Need an account? Create one",
            command=self.page._toggle_auth_mode,
            relief="flat", 
            bd=0
        ).pack(anchor="w")

        Label(
            card,
            "No demo accounts exist. Teachers can create classes and teams after signing in.",
            size=9,
            bg="white",
            fg="#7b8794",
            wraplength=500,
            justify="left",
        ).pack(anchor="w", pady=10)

        self.page.email_field.focus_set()

    def submit(self):
        email = self.page.email_field.get().strip().lower()
        password = self.page.password_field.get().strip()

        try:
            self.page._validate_email(email)
            self.page._validate_password(password)
            self.page.app.current_user = self.page.app.auth_repo.sign_in(email, password)
            self.page.auth_message.config(text="")
        except ValueError as error:
            self.page.auth_message.config(text=str(error))
            return
        self.page.app.show_dashboard()
