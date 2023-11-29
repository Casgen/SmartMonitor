import sys
import re

from requests.models import HTTPError
from smartmonitor.firebase_client import FirestoreClient
from smartmonitor.model.user import User


class UserInterface:
    def __init__(self, firebase_client: FirestoreClient) -> None:
        self.fb_db = firebase_client
        pass

    def run(self) -> int:
        print("Welcome to the SmartMonitor!")

        while True:
            print(
                "Please choose one of the options below by selecting one of the numbers."
            )
            print("1. Create a new User for the App")
            print("2. Run the app")

            for line in sys.stdin:
                match line.rstrip():
                    case "1":
                        self.run_new_user()
                        break
                    case "2":
                        if self.run_login():
                            return 2
                        print("Run Login failed!")
                        continue
                    case _:
                        print("Wrong option!")
                        continue

    def request_email(self, prompt: str = "Email:") -> str:
        print(prompt)

        for line in sys.stdin:
            if len(line.rstrip()) < 0:
                print("Failed to provide an email! Email doesn't match the criteria!")
                print(prompt)
                continue

            match = re.match(
                "[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
                line.rstrip(),
            )

            if match is not None:
                return line.rstrip()

            print("Failed to provide an email! Email doesn't match the criteria!")
            print(prompt)

        return ""

    def request_password(self, msg="Password:") -> str:
        print(msg)

        for line in sys.stdin:
            first_password: str = line.rstrip()
            if len(first_password) < 6:
                print(
                    "failed to set a password!\nPassword has to be atleast 6 characters long!"
                )
                print("Please provide atleast a six character long password: ")
                continue

            return first_password

        return ""

    def run_login(self) -> bool:
        while True:
            email = self.request_email("Please provide an e-mail:")

            if len(email) == 0:
                print("Failed to request email! string was empty!")
                continue

            password = self.request_password(
                "Please provide atleast a six character long password:"
            )

            if len(password) == 0:
                print("Failed to password email! string was empty!")
                continue

            try:
                self.fb_db.sign_in(email, password)
            except HTTPError as e:
                print(f"Failed to login!: {e.response}")
                continue

            print('Login was successful!')
            return True
        


    def run_new_user(self):
        new_user: User = User()
        password_success: bool = False

        # User input for a username
        print("Please provide a username (display name):")

        for line in sys.stdin:
            if len(line.rstrip()) > 0:
                new_user.username = line.rstrip()
                break

            print("Failed to provide a username! Username was empty!")
            print("Please provide a username (display name):")

        # User input for an email

        new_email = self.request_email("Please provide an Email:")

        if new_email is None:
            raise RuntimeError("Email returned was None!")

        new_user.email = new_email

        # User input for an password
        while not password_success:
            first_password = self.request_password(
                "Please provide atleast a six character long password: "
            )

            if first_password is None:
                raise RuntimeError("Password provided was None!")

            second_password: str

            for line in sys.stdin:
                second_password = line.rstrip()

                if not second_password == first_password:
                    print("Failed to provide a password! Passwords do not match!")
                    break

                new_user.password = second_password
                password_success = True
                break

        print("Password provided successfully!")
        self.fb_db.create_user(new_user.email, new_user.username, new_user.password)
