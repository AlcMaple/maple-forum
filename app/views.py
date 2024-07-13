# 路由和视图函数
from flask import request,jsonify,Blueprint
from .utils import *
from .models import User,db
from config.settings import Config
from .database import *
import requests,base64
from pprint import pprint

# 创建名为auth的蓝图对象
bp = Blueprint('auth',__name__,url_prefix='/')

# 定义全局变量session
session = {
    'verification_code': '',
    'code_timestamp': 0,
    'code_phone': ''
}

# 注册
@bp.route('/register',methods=['POST'])
def register():
    data = json_response(request)
    # print("data：",data)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    code = int(data.get('verification_code'))

    verification_response = verify_code(phone,code,session)
    # print("verification_response:",verification_response)
    # 获取返回的状态码和信息
    status_code = verification_response['code']
    # print(status_code)
    message = verification_response['message']

    if status_code == 200:
        print('开始注册，添加数据库……')
        # 生成初始用户名称
        user_name = initialize_username()
        result = 200 if register_user(username,email,password,phone,user_name) else 400
        print('添加数据后返回的状态码：',result)
        
        return jsonify({'code':200,'msg':'User registered successfully'}) if result == 200 else jsonify({'code':400,'msg':'Username or email or phone already exists'})
    else:
        return jsonify({'code':400,'msg':message})

# 发送验证码
@bp.route('/send_verification_code',methods=['POST'])
def send_verification_code():
    data = json_response(request)
    verification_phone = data.get('phone')

    global session

    verification_code,session = send_sms(verification_phone,session)
    # verification_code = result[0]
    # session = result[1]

    sendOK, info, apiStatus = Config.sms.send(verification_phone, 0, {'code': verification_code})
    # apiStatus = '200'
    print(sendOK) # 是否成功(布尔值)
    # print('apiStatus:', apiStatus, 'type:', type(apiStatus)) # api状态码
    # print(info) # 描述信息 
    if apiStatus == '200':
        print('短信发送成功')
        return jsonify({'msg': 'Verification code sent successfully'}), 200
    else:
        print('短信发送失败')
        return jsonify({'error': 'Verification code sent failed'}), 400
    
# 登录
@bp.route('/login',methods=['POST'])
def login():
    data = json_response(request)
    # print("data：",data)

    account = data.get('account')
    password = data.get('password')

    result_sponse,result_code = login_user(account,password)
    # print("result_spnonse：",result_sponse)
    # print("result_code",result_code)

    if result_code == 200:
        # 生成token值
        token = generate_token(result_sponse['id'])
        userInfo={
            'uid':result_sponse['id'],
            'account':result_sponse['username'],
            'email':result_sponse['email'],
            'phone':result_sponse['phone'],
            'token':token,
            'username':result_sponse['user_name'],
            'description':result_sponse['description']
        }
        return jsonify({'code':0,'msg':'User logged in successfully','userInfo':userInfo})
    
    return jsonify({'code':400,'msg':'账号或密码不正确'})

# 修改用户信息
@bp.route('/user',methods=['put'])
def user():
    # data = json_response(request)
    data = json_response(request)
    # print("update_data：",data)

    uid = data.get('uid')
    email=data.get('email')
    image_data = data.get('image_data')
    nickname = data.get('nickname')
    description = data.get('description')

    # print('avator：',image_data)
    # 解码base64字符串为二进制数据
    decoded_data = base64.b64decode(image_data)
    # print('decoded_data：',decoded_data)

    # download_image(decoded_data,uid)

    # is_success = check_image_exist(uid)
    # if is_success == False:
    #     return jsonify({'code':400,'msg':'Avatar upload failed'})

    # # 获取头像路径
    # avator_path = get_avatar_path(uid)
    # print('avator_path:',avator_path)

    # result_sponse,result_code = update_user(uid,nickname,email,description,avator_path)
    # if result_code == 200:
    #     return jsonify({'code':0,'msg':'User updated successfully'})
    # else:
    #     return jsonify({'code':400,'msg':'User update failed'})
    
    return jsonify({'code':0,'msg':'User updated successfully'})

# 获取用户信息
@bp.route('/user',methods=['post'])
def get_user():
    data = json_response(request)
    # print("DATA:",data)
    # print("data['_rawValue'][0]['uid']：",data['_rawValue'][0]['uid'])

    result_sponse,result_code = get_user_info(data['_rawValue'][0]['uid'])
    if result_code == 200:
        data = {
            'uid':result_sponse['id'],
            'account':result_sponse['username'],
            'email':result_sponse['email'],
            'mobile':result_sponse['phone'],
            'nickname':result_sponse['user_name'],
            'description':result_sponse['description'],
            'avator': result_sponse['avator'],
            'image_data': "",
        }
        return jsonify({'userInfo':data,'code':0,'msg':'User found successfully'})
    else:
        return jsonify({'code':400,'msg':'User not found'})
    
# 修改用户密码
@bp.route('/user/password',methods=['post'])
def change_password():
    data = json_response(request)
    # print(data)

    oldPassword=data.get('oldPassword')
    newPassword=data.get('newPassword')
    # print('oldPassword=',oldPassword)
    # print('newPassword=',newPassword)
    uid = str_to_dict(data.get('uid'))['userInfo']['uid']
    # print('uid=',uid)

    # 获取用户原密码
    result_sponse,result_code = get_user_password(uid)
    # print(result_sponse)

    result = decrypt_password(result_sponse,oldPassword)
    # print('result=',result)

    if oldPassword == newPassword or decrypt_password(result_sponse,oldPassword) == False:
        return jsonify({'code':400,'msg':'New password cannot be the same as the old password'})
    
    print('检查通过，开始更改密码……')

    result_sponse,result_code = update_password(uid,newPassword)
    return jsonify({'code':200,'msg':'Password changed successfully'})

# 处理上传的头像
@bp.route('/upload',methods=['post'])
def upload_avator():
    # result = request
    # print(result)
    file = request.files['file']
    # print("request.files：",request.files)
    # print("request.form：",request.form)
    # print(file)

    # 读取文件二进制数据
    file_data = file.read()
    # print("file_data：",file_data)

    # 将二进制数据编码为base64字符串
    encoded_data = base64.b64encode(file_data).decode('utf-8')

    return encoded_data

# 新增文章
@bp.route('/article/',methods=['post'])
def add_article():
    data = json_response(request)

    # print("add_article_data：",data)

    title = data.get('title')
    content = data.get('content')
    description = data.get('description')
    uid = data.get('uid')
    tagIds = data.get('tagIds')
    typeId = data.get('typeId')
    # print("uid：",uid)
    add_article_result,add_article_code = add_article_db(title,content,description,uid,tagIds,typeId)
    if add_article_code == 200:
        return jsonify({'code':200,'msg':'Article added successfully'})
    else:
        return jsonify({'code':400,'msg':'Article added error'})
    
    # return jsonify({'code':200,'msg':'Article added successfully'})

'''
获取用户文章标题列表
export function getUserArticleList() {
    return httpInstance({
        url: `/article`,
        method: 'get',
    })
}

const articleList = ref([])
onMounted: {
    code.value = account.code
    // 获取后端数据
    // getUserArticleList().then(res => {
    //     articleList.value = res.data.pageInfo.list;
    // });
}
'''
@bp.route('/article',methods=['post'])
def get_article_list():
    data = json_response(request)
    # print("get_article_list：",data)
    uid = data.get('uid')
    result_sponse,result_code = get_article_list_db(uid)
    # print(result_sponse,result_code)

    return jsonify({'code':200,'msg':'Article list found successfully','articleList':result_sponse})

    # return jsonify({'code':400,'msg':'Article list found error'})

'''
// 根据aid 获取文章信息
export function getArticleDetails(aid) {
    return httpInstance({
        url: `/article/${aid}`,
        method: 'get'
    });
}

onMounted: {
    //接收参数
    getArticleDetails(route.query.aid).then(res => {
        console.log('作者文章页', res);
        article.value = res.data
    });
}
'''
@bp.route('/article/<int:aid>',methods=['get'])
def get_article_details(aid):
    result_sponse,result_code = get_article_details_db(aid)
    # print(result_sponse,result_code)
    # print("aid:",aid)
    return jsonify({'code':200,'msg':'Article details found successfully','data':result_sponse})

'''
// 提交修改的数据
const put = () => {
  // articleSubmit.value.aid = article.value.aid
  articleSubmit.value.content = article.value.content;
  articleSubmit.value.description = article.value.description;
  articleSubmit.value.title = article.value.title;
  modifyArticle(articleSubmit.value).then(res => {
      console.log('修改文章', res);
      msg.value = ''
      msg.value = res.msg
  });
  alert("模拟保存修改");
};

// 修改文章
export function modifyArticle(article) {
    return httpInstance({
        url: `/article/`,
        method: 'put',
        data:article
    });
}
'''
@bp.route('/article/',methods=['put'])
def modify_article():
    data = json_response(request)
    # aid = result_sponse + 1
    title = data.get('title')
    content = data.get('content')
    description = data.get('description')
    tagIds = data.get('tagIds')
    typeId = data.get('typeId')
    aid = data.get('aid')
    # print('aid：',aid)

    response_result,response_code = modify_article_db(title, content, aid, description, tagIds, typeId)

    if response_code == 200:
        return jsonify({'code':200,'msg':'Article modified successfully'})
    else:
        return jsonify({'code':400,'msg':'Article modified error'})

    # return jsonify({'code':200,'msg':'Article modified successfully'})

'''
// 删除文章
const deleteArticle = () => {
  confirm("确定删除？");
  deleteArt(article.value.aid).then(res => {
      router.push({
          path: '/userHome/article'
      })
  });
};

// 用户删除这篇文章
export function deleteArt(aid) {
    return httpInstance({
        url: `/article/${aid}`,
        method: 'delete',
    });
'''
@bp.route('/article/<int:aid>',methods=['delete'])
def delete_article(aid):
    response_result,response_code = delete_article_db(aid)
    if response_code == 200:
        return jsonify({'code':200,'msg':'Article deleted successfully'})
    else:
        return jsonify({'code':400,'msg':'Article deleted error'})
    
'''
// 添加回复信息
const sendMsg = (parentComId) => {
  if (code.value != 0) {
    router.push({
      path: "/login",
    });
  }
  console.log("props.aid：", props.aid);
  console.log("parentComId：", parentComId);
  send.value.aid = props.aid;
  send.value.parentComId = parentComId;
  console.log("uid：", send.value.uid);
  console.log(send.value);
  postSendMag(send.value).then(res => {
      location.reload();
      console.log('添加评论', res)
  });
  alert("模拟添加");
};

// 回复评论信息
export function postSendMag(send) {
    return httpInstance({
        url: `/comment`,
        method: 'post',
        data:send
    });
}
'''
@bp.route('/comment',methods=['post'])
def add_comment():
    data = json_response(request)
    print("将要添加的评论：",data)
    aid = data.get('aid')
    content = data.get('content')
    parentComId = data.get('parentComId')
    uid = data.get('uid')
    parentCount = data.get('parentCount')
    sub_content = data.get("sub_content")
    pnickname = data.get('pnickname')

    # print('目前aid:',aid)

    if pnickname == "":
        result_sponse,result_code = add_comment_db(aid,parentCount,uid,parentCount,content=content)
        # 说明是一级评论
        return jsonify({'code':200,'msg':'Parent-Comment added successfully'})
    else:
        result_sponse,result_code = add_comment_db(aid,parentComId,uid,parentCount,sub_content=sub_content,pnickname=pnickname)
        # 说明是二级评论
        return jsonify({'code':200,'msg':'Sub-Comment added successfully'})
    
    # return jsonify({'code':200,'msg':'Sub-Comment added successfully'})

'''
// 获取已过审文章评论信息
export function getPublicContentment(aid) {
    return httpInstance({
        url: `/comment/anno/${aid}`,
        method: 'get',
    });
}

onMounted: {
  //接收参数
  getPublicContentment(route.query.aid).then((res) => {
    console.log("文章评论", res);
    contentment.value = res.data;
  });

  // 模拟评论
  contentment.value = [
    {
      comId: 0,
      uid: 1,
      nickname: "我会用vue3",
      createTime: "2023-6-3 19:22",
      content:
        "我的 uid 是 '1' 😎与模拟 ( 这条评论我发的 ) 的一样,因此我会有 -删除- 按钮🐔",
      uavator:
        "https://img0.baidu.com/it/u=1091210682,206783907&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1684602000&t=1813754cb45a25a646263c4b3a711514",
      // 子评论
      subReply: [
        {
          uid: 2,
          nickname: "我在学pinia",
          createTime: "2023-6-4 12:32",
          content: "我的 uid 是 '2' 我来玩了🥳",
          uavator: "../src/assets/imgs/uid2.png",
          pnickname: "我会用vue3",
        },
        {
          uid: 1,
          nickname: "我会用vue3",
          createTime: "2023-6-4 12:39",
          content: "我的 uid 是 '1' 欢迎欢迎 泰库辣🥳",
          uavator:
            "https://img0.baidu.com/it/u=1091210682,206783907&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1684602000&t=1813754cb45a25a646263c4b3a711514",
          pnickname: "我会用vue3",
        },
      ],
    },
    {
      comId: 1,
      uid: 2,
      nickname: "我在学pinia",
      createTime: "2023-6-3 22:32",
      content: "我的 uid 是 '2' 我没有 -删除- 按钮🐔 因为上面的评论不是我发的",
      uavator: "../src/assets/imgs/uid2.png",
    },
    {
      comId: 2,
      uid: 2,
      nickname: "我在学pinia",
      createTime: "2023-6-3 22:32",
      content: "忘记告诉你们了！因为是模拟数据所以这些按钮也就成为摆设了😘",
      uavator: "../src/assets/imgs/uid2.png",
    },
  ];
}
'''
@bp.route('/comment/anno/<int:aid>',methods=['get'])
def get_public_comment(aid):
    # print('当前文章的aid：',aid)
    # get_public_comment_db(aid)
    result_sponse,result_code = get_public_comment_db(aid)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Comment not found'})
    # print("查询评论信息result_sponse：",result_sponse)
    return jsonify({'code':200,'msg':'Comment found successfully','data':result_sponse})

'''
  // 获取全部分类信息
  getTypes().then(res => {
      console.log('全部分类', res);
      types.value = res.data
  })

  // 获取所有的分类信息
export function getTypes() {
    return httpInstance({
        url: `/type/anno/typelist`,
        method: 'get',
    });
}

// 文章分类
const types = ref([
  {
    name: "vue",
    tagId: 1,
  },
  {
    name: "axios",
    tagId: 2,
  },
  {
    name: "java",
    tagId: 3,
  },
  {
    name: "pinia",
    tagId: 4,
  },
  {
    name: "python",
    tagId: 5,
  },
]);
'''
@bp.route('/type/anno/typelist',methods=['get'])
def get_all_types():
    respnse_result,response_code = get_all_types_db()
    if response_code != 200:
        return jsonify({'code':400,'msg':'Types not found'})
    
    return jsonify({'code':200,'msg':'Types found successfully','data':respnse_result})

'''
// 热评
export function getIndexTime(){
    return httpInstance({
        url:'/api/index/time',
        method:'get',
    })
}

getIndexTime().then(res => {
    articleList.value = res.data.page.list;
    console.log('首页返回数据',articleList.value);
  });
'''
@bp.route('/api/index/time',methods=['get'])
def get_index_time():
    result_sponse,result_code = get_index_time_db()
    if result_code != 200:
        return jsonify({'code':400,'msg':'Article not found'})
    
    # print((str(result_sponse)))
    return jsonify({'code':200,'msg':'Article found successfully','data':result_sponse})

'''
export function handleThumb(aid, likeCount) {
    return httpInstance({
        url: `/article/${aid}/like`,
        method: 'post',
        data: {
            likeCount: likeCount
        }
    });
}

const handleLikeClick = async (event, article) => {
  event.stopPropagation();
  article.likeCount++;

  handleThumb(article.aid, article.likeCount).then((res) => {
    console.log(res);
  });
};
'''
@bp.route('/article/<int:aid>/like',methods=['post'])
def handle_like_click(aid):
    data = json_response(request)
    likeCount = data.get('likeCount')
    uid = data.get('uid')
    # print("当前文章的aid：",aid)
    # print("当前文章的likeCount：",likeCount)
    # print("当前用户的uid：",uid)
    response_result,response_code = handle_like_click_db(aid,likeCount,uid)
    # print("点赞响应结果：",response_result)
    if response_code != 200:
        return jsonify({'code':400,'msg':'Article not found'})
    
    return jsonify({'code':200,'msg':'Article found successfully','data':response_result})

# 首页热评
'''
// 获取数据
getIndexHot().then(res => {
    articleList.value = res.data.page.list;
});

// 热评
export function getIndexHot(){
    return httpInstance({
        url:'/api/index/hot',
        method:'get',
    })
}
'''
@bp.route('/api/index/hot',methods=['get'])
def get_index_hot():
    result_sponse,result_code = get_index_hot_db()
    if result_code != 200:
        return jsonify({'code':400,'msg':'Article not found'})
    
    return jsonify({'code':200,'msg':'Article found successfully','data':result_sponse})

# 搜索功能
'''
getSearch(queryData.value).then(res => {
    console.log('搜索结果', res.data.pageInfo.list);
    articleList.value = res.data.pageInfo.list;
});

// 与搜索有关的API
export function getSearch(query){
    return httpInstance({
        url:`/api/query`,
        method:'post',
        data:query
    })
}
'''
@bp.route('/api/query',methods=['post'])
def get_search():
    data = json_response(request)
    query = data.get('query')
    # print("搜索关键字：",query)
    result_sponse,result_code = get_search_db(query)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Search not found'})

    return jsonify({'code':200,'msg':'Search found successfully','data':result_sponse})

# 获取用户标签
'''
getUserTagList(userData.value[0].uid).then(res => {
    console.log('用户主页',res);
    tags.value=res.data.pageInfo.list
});

export function getUserTagList() {
    return httpInstance({
        url: `/tag/tagList`,
        method: 'get',
    })
}
'''

# 新增用户标签
'''
postNewTag(tag.value).then((res) => {
    console.log(res);
    msg.value = ''
    msg.value = res.msg
    loadTagsData();
})

export function postNewTag(tag) {
    return httpInstance({
        url: `/tag`,
        method: 'post',
        data: tag
    })
}
'''
@bp.route('/tag',methods=['post'])
def add_user_tag():
    data = json_response(request)
    tag = data.get('name')
    uid = data.get('uid')
    # print("新增标签：",tag)
    result_sponse,result_code = add_user_tag_db(tag,uid)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Tag not added'})

    return jsonify({'code':200,'msg':'Tag added successfully','msg':result_sponse})

# 修改用户标签
'''
updateTagName(editedTag.value).then((res) => {

    msg.value = ''
    msg.value = res.msg
    loadTagsData();
})

// 更新标签值
export function updateTagName(tag) {
    return httpInstance({
        url: `/tag`,
        method: 'put',
        data: tag
    })
}
'''
@bp.route('/tag',methods=['put'])
def update_user_tag():
    data = json_response(request)
    tag = data.get('name')
    tagId = data.get('tagId')
    old_tag = data.get('oldName')
    # print("修改标签：",tag)
    # print("tagId：" ,tagId)
    # print("old_tag：" ,old_tag)
    result_sponse,result_code = update_user_tag_db(tag,tagId,old_tag)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Tag not updated'})

    return jsonify({'code':200,'msg':'Tag updated successfully','msg':result_sponse})

    # return jsonify({'code':200,'msg':'Tag updated successfully'})

# 获取用户标签
'''
//获取用户标签信息
export function getUserTagList(uid) {
    return httpInstance({
        url: `/tag/tagList`,
        method: 'post',
        data: {
            uid: uid
        }
    })
}

// 加载参数
loadTagsData = async () => {
  const res = await getUserTagList(props.userId);
  tagsData.value = res.data.pageInfo.list;
};
loadTagsData();
'''
@bp.route('/tag/tagList',methods=['post'])
def get_user_tag_list():
    data = json_response(request)
    uid = data.get('uid')
    # print("获取用户标签：",uid)
    result_sponse,result_code = get_user_tag_list_db(uid)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Tag not found'})

    return jsonify({'code':200,'msg':'Tag found successfully','data':result_sponse})

# 删除用户标签
'''
// 删除标签
const handleDelete = (tagId) => {
  deleteTag(tagId).then((res) => {
    msg.value = ''
    msg.value = res.msg
    loadTagsData();
  })
  alert("模拟删除");
};

// 删除一个标签
export function deleteTag(tagId) {
    return httpInstance({
        url: `/tag/${tagId}`,
        method: 'delete',
    })
}
'''
@bp.route('/tag/<int:tagId>',methods=['delete'])
def delete_user_tag(tagId):
    # print("删除标签：",tagId)
    result_sponse,result_code = delete_user_tag_db(tagId)
    if result_code != 200:
        return jsonify({'code':400,'msg':'Tag not deleted'})

    return jsonify({'code':200,'msg':'Tag deleted successfully','msg':result_sponse})