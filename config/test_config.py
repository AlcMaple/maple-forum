# 测试类配置文件

class TestConfig(object):
    DEBUG = True
    TESTING = True
    # 使用内存数据库测试
    DATABASE_URI ='sqlite:///:memory:'