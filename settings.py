import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    DISK_API_HOST = os.getenv('DISK_API_HOST')
    DISK_API_VERSION = 'v1'
