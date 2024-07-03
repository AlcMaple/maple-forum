# 启动Flask应用程序脚本
from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", threaded=True, port=8081,debug=True)