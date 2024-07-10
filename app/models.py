# 数据库模型
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

'''
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    description TEXT,
    user_name varchar(225),
    image varchar(225),
    like_article_ids json,
);
'''

'''
用户文章表
create table articles(
    aid int auto_increment primary key,
    title varchar(225) not null,
    content text not null,
    description text,
    uid int,
    like_count int,
    page_view int,
    create_time datetime default current_timestamp,
    update_time datetime,
    tagIds json,
    typeId int,
    constraint uid foreign key(uid) references users(id)
);
'''

'''
用户评论表
create table comments(
    com_id int auto_increment primary key,
    pnickname varchar(225),
    aid int,
    content text,
    parentComId int,
    uid int,
    sub_content text,
    time datetime not null default current_timestamp,
    constraint fk_uid foreign key(uid) references users(id),
    constraint fk_aid foreign key(aid) references articles(aid)
);

分类表
create table types(
    ttag_id int auto_increment primary key,
    tname varchar(225) not null
)

插入分类数据
insert into types(tname) values('Linux'),('入门'),('python'),('vue'),('axios'),('java'),('pinia'),('python');

----
如果报错1826，是因为你的外键名存在过了

用户标签表
create table user_tags(
    utag_id int auto_increment primary key,
    utag_uid int,
    utag_name varchar(225) not null,
    constraint fk_utag_uid foreign key(utag_uid) references users(id)
)
'''

# 表名为user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # index=True：创建索引，提高查询效率
    username = db.Column(db.String(20), unique=True, nullable=False,index=True)
    email = db.Column(db.String(120), unique=True, nullable=False,index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True,index=True)

    # 展示用户信息
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.phone}')"
    
    # 设置密码加密
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)