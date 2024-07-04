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
npm run serve
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
# 修改da.py中的数据库配置
# 创建MySQL数据库

# 迁移MySQL数据库
mysql -u your_local_user -p your_local_database -P your_local_port < forum.sql

# 启动服务
python run.py
```

# 感谢

- 所有开源软件组织&开发者