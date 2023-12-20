from typing import List
from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.services.auth import auth_service



class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and takes in any arguments that are required to do so.
        In this case, we're taking in a list of allowed roles.

        :param self: Represent the instance of the class
        :param allowed_roles: List[Role]: Specify that the allowed_roles parameter is a list of role objects
        :return: The instance of the class
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.token_manager.get_current_user)):
        """
        The __call__ function is the function that will be called when a request comes in.
        It takes two arguments:
            - request: The incoming HTTP Request object. This contains all of the information about the incoming request, such as headers, body data, etc.
            - current_user: A User object representing who made this call (if authenticated). If not authenticated then it will be None.

        :param self: Access the class attributes
        :param request: Request: Get the request object
        :param current_user: User: Get the user from the token
        :return: A function
        """
        print(request.method, request.url)
        print(f"User role {current_user.roles}")
        print(f"Allowed roles {self.allowed_roles}")
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")
