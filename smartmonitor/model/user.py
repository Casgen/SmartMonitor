
class User():

    def __init__(self, username:str="", password="", email="", id="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.email = email

    def to_dict(self, include_id: bool = False) -> dict:

        id = None

        if include_id:
            id = self.id
        
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "id": id
        }

    @staticmethod
    def from_doc(source):

        source_dict = source.to_dict()

        return User(source_dict["username"],
             source_dict["password"],
             source_dict["email"],
             source.id)

