import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    YADISK_API_HOST = os.getenv('YADISK_API_HOST')
    YADISK_API_VERSION = 'v1'