from flask_sqlalchemy import SQLAlchemy
from Classes.User import *
import requests
import sys
import json

def getUserInfo(gglSession):
    