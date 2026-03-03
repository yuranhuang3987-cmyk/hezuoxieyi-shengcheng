# -*- coding: utf-8 -*-
"""数据库模型"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """用户表"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment="用户名")
    password_hash = db.Column(db.String(256), nullable=False, comment="密码哈希")
    role = db.Column(db.String(20), default="user", comment="角色: admin/user")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }

    @staticmethod
    def create_admin():
        """创建默认管理员"""
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员已创建: admin / admin123")
        return admin


class History(db.Model):
    """生成历史记录"""

    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, comment="用户ID")
    software_name = db.Column(db.String(200), nullable=False, comment="软件名称")
    software_version = db.Column(db.String(50), default="V1.0", comment="版本号")
    dev_date = db.Column(db.String(50), comment="开发完成日期")
    agreement_date = db.Column(db.String(50), comment="协议签署日期")
    owners_count = db.Column(db.Integer, comment="著作权人数量")
    owners_info = db.Column(db.Text, comment="著作权人信息（JSON格式）")
    input_file = db.Column(db.String(500), comment="输入文件名")
    output_file = db.Column(db.String(500), comment="输出文件名")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    # 关联用户
    user = db.relationship("User", backref=db.backref("histories", lazy="dynamic"))

    def to_dict(self):
        """转换为字典"""
        import json

        return {
            "id": self.id,
            "software_name": self.software_name,
            "software_version": self.software_version,
            "dev_date": self.dev_date,
            "agreement_date": self.agreement_date,
            "owners_count": self.owners_count,
            "owners_info": json.loads(self.owners_info) if self.owners_info else [],
            "input_file": self.input_file,
            "output_file": self.output_file,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None,
        }
