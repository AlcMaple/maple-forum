# 辅助函数和工具
import random,requests,os
import time
import json
from werkzeug.security import generate_password_hash,check_password_hash
from .database import *

# 请求数据处理 -> json
def json_response(data):
    return data.json

# 数组 → json字符串
def array_to_json(data):
    return json.dumps(data)

# 字符串 -> 字典
def str_to_dict(data):
    return json.loads(data)

# 定义四位数的随机验证码
def generate_verification_code():
    verification_code = str(random.randint(1000, 9999))
    # verification_code=7420
    return verification_code

def send_sms(phone_number,session):

    # 生成验证码
    verification_code = generate_verification_code()
    # 保存验证码到session中
    session['verification_code'] = verification_code
    session['code_timestamp'] = int(time.time())
    session['code_phone'] = phone_number

    return verification_code,session

def check_phone(current_phone,session):
    if session['code_phone'] == None or session['code_phone'] == current_phone:
        return True
    return False

def verify_code(phone,code,session):
    user_phone = phone
    user_code = str(code)
    code_timestamp = 70 if session['code_timestamp'] == None else session['code_timestamp']
    current_timestamp = int(time.time())

    # print("code_timestamp：",code_timestamp)
    # print("current_timestamp：",current_timestamp)
    # print("code_phone：" ,session.get('code_phone'))
    print("user_code：" ,user_code)
    print("session.get('verification_code')：" ,session['verification_code'])
    # print("code_phone：",session['code_phone'])

    if check_phone(user_phone,session) == False:
        return {'message': '手机号码错误', 'status': 'error','code':400}
    
    print('--------------------------------------')
    # print(current_timestamp - code_timestamp < 60)
    print(type (user_code))
    print(type (session['verification_code']))
    # print(user_code == session['verification_code'])

    # 检查验证码是否有效（1分钟时效性）
    if current_timestamp - code_timestamp < 60 and user_code == session['verification_code']:
        print("验证通过")
        return {'message': '验证通过', 'status': 'success','code':200}
    else:
        return {'message': '验证码无效或已过期', 'status': 'failed','code':400}
    
# 初始化session变量
def initialize_session():
    session = {
    'verification_code': '',
    'code_timestamp': 0,
    'code_phone': ''
   } 
    return session

# 生成token
def generate_token(user_id):
    token = str(user_id) + str(int(time.time())) + str(random.randint(100000, 999999))
    return token

# 赋予初始用户名称
def initialize_username():
    username = 'user_' + str(int(time.time())) + str(random.randint(1000,9999))
    return username

# 密码解密
def decrypt_password(password,hash_password):
    return check_password_hash(password,hash_password)

# 获取当前文件所在目录
def get_current_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir

# 图片下载
def download_image(image_data,uid):
    current_dir = get_current_path()
    imgs_dir = os.path.join(current_dir, '../../vue3-forum/src/assets/imgs')

    os.makedirs(imgs_dir, exist_ok=True)

    with open(os.path.join(imgs_dir, "uid{}.jpg".format(uid)), 'wb') as f:
        f.write(image_data)

# 检查图片是否存在
def check_image_exist(uid):
    current_dir = get_current_path()
    imgs_dir = os.path.join(current_dir, '../../vue3-forum/src/assets/imgs')

    img_path = os.path.join(imgs_dir, "uid{}.jpg".format(uid))

    if os.path.exists(img_path):
        return True
    else:
        return False
    
# 获取头像路径
def get_avatar_path(uid):
    return 'src/assets/imgs/uid{}.jpg'.format(uid)

# 获取文章aid最大数
def get_max_aid():
    response_result,response_code = get_max_article_id()
    response_result = 0 if response_result == None else response_result
    print(response_result,response_code)
    if response_code == 200:
        return response_result,200
    else:
        return jsonify({'error': 'No articlesMax found'}), 400