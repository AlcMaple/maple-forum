# maple-forum

This is a forum project for Maplesoft.

# 当前版本

- MySQL 8.0.38（默认最新版本）
- python 3.11（向上兼容）

# 编译&安装

## 前端

```bash
# 克隆项目
git clone https://github.com/AlcMaple/maple-FFe.git

# 进入项目目录
cd maple-FFe

# 安装依赖
npm install

# 启动服务
npm run dev

# 测试账号：admin  密码：admin
```

## 后端

```bash
# 克隆项目
git clone https://github.com/AlcMaple/maple-forum.git

# 进入项目目录
cd maple-forum

# 安装依赖
pip install -r requirements.txt

# 修改配置文件
# 修改database.py中的数据库配置
# 创建MySQL数据库 

# 迁移MySQL数据库
mysql -u your_local_user -p your_local_database -P your_local_port --default-character-set=utf8 < forum.sql

# 启动服务
python run.py
```

# 预览

![2](.\images\2.png)

![3](.\images\3.png)

![4](.\images\4.png)

![5](.\images\5.png)

![6](.\images\6.png)

![7](.\images\7.png)

![8](.\images\8.png)

# 常见问题

---

- 后端启动服务，python run.py，显示权限不足

使用管理员模式打开命令行窗口

![1](.\images\1.png)

如果需要在本地搭建的话，需要修改http.js以及login.vue里的请求地址为本地：`http://127.0.0.1:8081`

# 感谢

- 所有开源软件组织&开发者