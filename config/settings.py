# 常规配置文件
from quanmsms import sdk  # pip install quanmsms
import secrets

class Config(object):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 7777
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'loveat2024a+.'
    # CREATE DATABASE forum CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    MYSQL_DB = 'forum'
    MYSQL_CHARSET = 'utf8mb4'
    # 例：SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@host:port/database?charset=utf8mb4'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_CHARSET
    )

    # 调用短信接口，将验证码发送给用户手机号
    sms = sdk.SDK(
        '844',  # OpenID
        '2ec1400212c511efa4d70242ac110002' # Apikey
    )

    # 设置密钥，保证Session会话的正常使用
    SECRET_KEY = "b3dc63aa632729f8daa44f7ea4b7f3a2"