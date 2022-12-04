from enum import Enum


class Roles(str, Enum):
    Admin = 'admin'
    Moder = 'moderator'
    User = 'user'
