import pymysql.cursors
from flask import jsonify
from werkzeug.security import generate_password_hash,check_password_hash
import json

def create_connection():
    try:
        connect=pymysql.Connect(
            host='localhost',
            port=7777,
            user='root',
            passwd='loveat2024a+.',
            db='forum',
            charset='utf8'
        )
        cursor=connect.cursor()
        cursor.execute("Select version()")
        version=cursor.fetchone()
        print("MySQL数据库版本是：%s"%version)
        cursor.close()
    except Exception as e:
        print('数据库连接失败：', e)  

    return connect

def register_user(username,email, password, phone,user_name):
    connection = create_connection()
    cursor = connection.cursor()

    # 检查用户名是否已经存在
    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    result = cursor.fetchone()
    if result:
        cursor.close()
        return jsonify({'error': 'Username already exists'}), 400
    
    print('检查用户名完成，继续创建用户')

    # 检查邮箱是否已经存在
    cursor.execute("SELECT * FROM users WHERE email = %s", (email))
    result = cursor.fetchone()
    if result:
        cursor.close()
        return jsonify({'error': 'Email already exists'}), 400
    
    # 检查手机号是否已经存在
    cursor.execute("SELECT * FROM users WHERE phone = %s", (phone))
    result = cursor.fetchone()
    if result:
        cursor.close()
        return jsonify({'error': 'Phone already exists'}), 400
    
    # 对密码进行hash加密
    password_hash = generate_password_hash(password)

    print('加密完成，继续创建用户')
    
    # 插入用户数据到数据库
    cursor.execute("INSERT INTO users(username, email,password_hash,phone,description,user_name) VALUES (%s,%s, %s,%s,%s,%s)", (username, email, password_hash,phone,"你还没有介绍自己呢！！！",user_name))

    print('插入数据库完成，开始事务')

    # 提交事务
    connection.commit()

    # 关闭游标
    cursor.close()

    # 返回成功信息
    return jsonify({'message': 'User registered successfully'}), 200

def login_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    print('username:', username)

    # 检查用户名是否存在
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if not result:
        print('用户名不存在')
        cursor.close()
        return jsonify({'error': 'Username does not exist'}), 400

    # 检查密码是否正确
    password_hash = result[3]
    if not check_password_hash(password_hash, password):
        # print('generate_password_hash(password):',generate_password_hash(password))
        print('密码错误')
        cursor.close()
        return jsonify({'error': 'Incorrect password'}), 400

    # 返回用户信息
    user = {
        'id': result[0],
        'username': result[1],
        'email': result[2],
        'phone': result[4],
        'description': result[5],
        'user_name':result[6]
    }
    cursor.close()
    return user, 200

# 更改用户信息
def update_user(user_id, user_name, email, description,avator_path):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("update users set user_name=%s, email=%s, description=%s, image=%s where id=%s", (user_name, email, description,avator_path, user_id))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'User updated successfully'}), 200

# 获取用户信息
def get_user_info(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        return jsonify({'error': 'User does not exist'}), 400
    
    # print('avator：',result[7])

    user = {
        'id': result[0],
        'username': result[1],
        'email': result[2],
        'phone': result[4],
        'description': result[5],
        'user_name':result[6],
        'avator':result[7]
    }

    print('user:',user)
    cursor.close()
    return user, 200

# 更改用户密码
def update_password(user_id, new_password):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("update users set password_hash=%s where id=%s", (generate_password_hash(new_password), user_id))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Password updated successfully'}), 200

# 获取用户密码
def get_user_password(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        return jsonify({'error': 'User does not exist'}), 400
    cursor.close()
    return result[0], 200

# 保存图片
def save_image(image_data,uid):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("update users set image_data=%s where id=%s", (image_data,uid))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Image saved successfully'}), 200

# 获取文章最大数
def get_max_article_id():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(aid) FROM articles")
    result = cursor.fetchone()
    if not result:
        cursor.close()
        return jsonify({'error': 'No articlesMax found'}), 400
    cursor.close()
    return result[0], 200

# 新增文章
def add_article_db(title, content, description, uid,tagIds,typeId):
    # 函数内部导入模块，避免两个模块相互导入的问题
    from .utils import array_to_json
    connection = create_connection()
    cursor = connection.cursor()
    tagIds = array_to_json(tagIds)
    # print('tagIds:',tagIds)
    cursor.execute("INSERT INTO articles(title, content, description, uid,tagIds,typeId) VALUES (%s,%s,%s,%s,%s,%s)", (title, content, description, uid,tagIds,typeId))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Article added successfully'}), 200

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
def get_article_list_db(uid):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM articles WHERE uid = %s", (uid,))
    result = cursor.fetchall()
    if not result:
        cursor.close()
        return jsonify({'error': 'No articles found'}), 400
    article_list = []
    for article in result:
        article_list.append({
            'title': article[1],
            'aid':article[0],
            'uid':article[4],
        })
    cursor.close()
    return article_list, 200

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
def get_article_details_db(aid):

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM articles WHERE aid = %s", (aid,))
    result = cursor.fetchone()
    print("result:",result)
    if not result:
        cursor.close()
        return jsonify({'error': 'Article does not exist'}), 400
    article = {
        'title': result[1],
        'content': result[2],
        'aid': result[0],
        'description': result[3],
        'commentabled': 'true',
        'tags':[],
        'typeId':result[10],
    }

    # 获取文章分类
    # cursor.execute("SELECT tname FROM types WHERE ttag_id = %s", (result[10],))
    # result = cursor.fetchone()
    # if result:
    #     article['typeId'] = result[0]

    tags_data = json.loads(result[9])

    for i in tags_data:
        cursor.execute("SELECT tname FROM types WHERE ttag_id = %s", (i,))
        result = cursor.fetchone()
        if result:
            article['tags'].append({'name': result[0]})
    cursor.close()
    return article, 200

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
def modify_article_db(title, content, aid, description,tagIds,typeId):
    from .utils import array_to_json
    connection = create_connection()
    cursor = connection.cursor()
    tagIds = array_to_json(tagIds)
    cursor.execute("UPDATE articles SET title=%s, content=%s, description=%s, tagIds=%s, typeId=%s WHERE aid=%s", (title, content, description, aid,tagIds,typeId))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Article modified successfully'}), 200

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
def delete_article_db(aid):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM articles WHERE aid = %s", (aid,))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Article deleted successfully'}), 200

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
def add_comment_db(aid, parentComId, uid,parentCount,content='', sub_content='',pnickname=''):
    connection = create_connection()
    cursor = connection.cursor()
    print('将要添加的数据库中的content的值：',content)
    print(bool(content))
    if sub_content == '':
        print('添加一级评论')
        cursor.execute("INSERT INTO comments(aid, parentComId, uid, content) VALUES (%s,%s,%s,%s)", (aid, parentCount, uid, content))
        connection.commit()
        cursor.close()
        return jsonify({'message': 'Parent-Comment added successfully'}), 200
        # return 0
    print('添加二级评论')
    cursor.execute("INSERT INTO comments(aid, parentComId, uid, sub_content, pnickname) VALUES (%s,%s,%s,%s,%s)", (aid, parentComId, uid, sub_content, pnickname))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Sub-Comment added successfully'}), 200

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
def get_public_comment_db(aid):
    connection = create_connection()
    cursor = connection.cursor()
    # 获取comments评论表nickname为空且aid等于aid的信息，并根据信息中的uid获取users用户表里的信息
    cursor.execute("SELECT c.com_id, c.uid, c.content, c.time, u.user_name, u.image FROM comments c INNER JOIN users u ON c.uid = u.id WHERE c.aid = %s AND c.pnickname is NULL", (aid,))
    # cursor.execute("SELECT c.com_id, c.uid, c.content, c.time, u.user_name, u.image FROM comments c INNER JOIN users u ON c.uid = u.id WHERE c.aid = %s", (aid,))
    result = cursor.fetchall()
    if not result:
        print("没有查到结果")
        cursor.close()
        return jsonify({'error': 'No comments found'}), 400
    comment_list = []
    for comment in result:
        sub_reply_list = []
        # 获取子评论信息
        cursor.execute("SELECT c.uid, c.sub_content, u.user_name, u.image, c.pnickname, c.time FROM comments c INNER JOIN users u ON c.uid = u.id WHERE c.parentComId = %s and c.pnickname is not NULL", (comment[0],))
        sub_reply_result = cursor.fetchall()
        for sub_reply in sub_reply_result:
            sub_reply_list.append({
                'uid': sub_reply[0],
                'content': sub_reply[1],
                'createTime': sub_reply[5],
                'nickname': sub_reply[2],
                'uavator': "../" + sub_reply[3],
                'pnickname': sub_reply[4],
            })
        comment_list.append({
            'comId': comment[0],
            'uid': comment[1],
            'content': comment[2],
            'createTime': comment[3],
            'nickname': comment[4],
            'uavator': "../" + comment[5],
           'subReply': sub_reply_list,
        })
    cursor.close()
    print("评论列表：",comment_list)
    return comment_list, 200

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
def get_all_types_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM types")
    result = cursor.fetchall()
    if not result:
        cursor.close()
        return jsonify({'error': 'No types found'}), 400
    type_list = []
    for type in result:
        type_list.append({
            'name': type[1],
            'tagId': type[0]
        })

    cursor.close()
    return type_list, 200