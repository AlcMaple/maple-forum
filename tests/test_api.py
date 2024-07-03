# 测试代码 - 测试API端点
import unittest
import sys,os

"""
__file__：当前文件路径
os.path.abspath(__file__)：将__file__文件的绝对路径转换为相对路径
os.path.dirname()：返回指定路径的目录名
os.path.dirname(os.path.dirname(os.path.abspath(__file__)))：项目的根目录路径
"""
# 将项目的根目录添加到Python的系统路径中，以便导入应用模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

class APITestCase(unittest.TestCase):
    def setUp(self):
        # 创建Flask应用的测试客户端
        self.app = create_app(test_config=True)
        self.client = self.app.test_client()

    def test_register(self):
        # 测试注册API
        url = "http://localhost:8081/register"
        data = {
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com",
            "phone": "1234567890",
            "code": "123456"
        }

        # 使用requests库发送POST请求
        response = self.client.post(url, json=data)

        # 解析json数据
        response_data = response.get_json()

        # 断言响应状态码和响应数据
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {'code':201,'msg':'注册成功'})

    # def test_send_verification_code(self):
    #     # 测试注册API
    #     url = "http://localhost:8081/send_verification_code"
    #     data = {
    #         "phone": "13825600730"
    #     }

    #     # 使用requests库发送POST请求
    #     response = self.client.post(url, json=data)

    #     # 解析json数据
    #     response_data = response.get_json()

    #     # 断言响应状态码和响应数据
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response_data, {'msg':'Verification code sent successfully'})


if __name__ == '__main__':
    unittest.main()