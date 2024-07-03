# 初始化应用程序，创建Flask实例
from flask import Flask, session
from flask_cors import CORS
from config.test_config import TestConfig
from config.settings import Config
from .views import bp as auth_bp
# 设置session为永久性，并定义有效期限
from datetime import timedelta

def create_app(test_config=False) -> Flask:
    app = Flask(__name__)
    # 设置密钥，保证Session会话的正常使用
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.permanent_session_lifetime = timedelta(days=7)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        
    CORS(app,resources=r'/*')

    if test_config:
        # 加载测试配置
        app.config.from_object(TestConfig)
        return app
        
    else:
        # 加载常规配置
        app.config.from_object(Config)
        app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI

    # 注册蓝图
    app.register_blueprint(auth_bp)
    return app