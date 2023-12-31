from datetime import datetime
import firebase_admin
import requests
import json

from requests.exceptions import HTTPError
from pathlib import Path
from google.cloud.firestore import FieldFilter
from smartmonitor.model.user import User
from firebase_admin import credentials, firestore, auth, storage, messaging


class FirestoreClient:

    
    def __init__(self) -> None:
        creds = credentials.Certificate("./service_account_cred.json")

        token_file = open("token-virtual.json", "r")

        data = json.load(token_file)

        self.token = data['token']

        self.api_key = "AIzaSyCkH2RuaOcCxP8Xt-z6RQofCS6Qal5KvnI"

        config = {
            "authDomain": "smartsurveillance-37001.firebaseapp.com",
            "apiKey": self.api_key,
            "storageBucket": "gs://smartsurveillance-37001.appspot.com",
        }

        self._app = firebase_admin.initialize_app(
            (creds),
            {
                "storageBucket": "smartsurveillance-37001.appspot.com",
            },
        )

        self._db = firestore.client()
        self.bucket = storage.bucket()

    def get_user(self, user_id: str) -> User:
        """
        Returns the user with the given user_id

        Returns:
            A User object
        """
        doc = self._db.document(f"users/{user_id}").get()

        if not doc.exists:
            print("The given user was not found!")

        return User.from_doc(doc)

    def find_user_by_username(self, username: str) -> User | None:
        """
        finds the first user found with the given username

        Returns:
            A User object
        """
        docs = (
            self._db.collection("users")
            .where(filter=FieldFilter("username", "==", username))
            .stream()
        )

        for doc in docs:
            return User.from_doc(doc)

        return None

    def create_user(self, email: str, display_name: str, password: str) -> bool:
        user = auth.create_user(
            email=email, display_name=display_name, password=password
        )

        if user.id is not None:
            print(f"Successfully created new user: {user.uid}")
            return True

        return False

    def sign_in(self, email: str, password: str):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(
            self.api_key
        )

        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps(
            {"email": email, "password": password, "returnSecureToken": True}
        )

        request_object = requests.post(request_ref, headers=headers, data=data)

        self.raise_detailed_error(request_object)
        self.current_user = request_object.json()

        return request_object.json()

    def raise_detailed_error(self, request_object):
        try:
            request_object.raise_for_status()
        except HTTPError as e:
            raise HTTPError(e, response=request_object.text)

    def upload_image(self, path: Path):
        blob = self.bucket.blob(datetime.now().strftime('%d-%m-%y_%H-%M-%S-%f'))

        blob.upload_from_filename(path.as_posix())

        print(f"File {path.as_posix()} uploaded to {blob}.")

    def send_notification(self):
        message = messaging.Message(
            token=self.token,
            notification= messaging.Notification("Person Detected!","Somebody is running in your property!")
        )

        response = messaging.send(message)
        print(response)
