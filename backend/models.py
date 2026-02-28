# -*- coding: utf-8 -*-
"""数据库模型"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class History(db.Model):
    """生成历史记录"""

    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    software_name = db.Column(db.String(200), nullable=False, comment="软件名称")
    software_version = db.Column(db.String(50), default="V1.0", comment="版本号")
    dev_date = db.Column(db.String(50), comment="开发完成日期")
    agreement_date = db.Column(db.String(50), comment="协议签署日期")
    owners_count = db.Column(db.Integer, comment="著作权人数量")
    owners_info = db.Column(db.Text, comment="著作权人信息（JSON格式）")
    input_file = db.Column(db.String(500), comment="输入文件名")
    output_file = db.Column(db.String(500), comment="输出文件名")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

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
