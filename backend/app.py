# -*- coding: utf-8 -*-
"""Flask 主程序 - 软件著作权合作协议生成器 Web 版"""

import os
import json
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, History
from utils import extract_info, calc_agreement_date, generate_agreement

# 配置
app = Flask(__name__)
CORS(app)  # 允许跨域

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "app.db")

# 创建必要目录
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# 数据库配置
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 最大 16MB

# 初始化数据库
db.init_app(app)
with app.app_context():
    db.create_all()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {"docx"}


def allowed_file(filename):
    """检查文件扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "message": "服务运行正常"})


@app.route("/api/preview", methods=["POST"])
def preview():
    """
    预览提取的信息

    接收 .docx 文件，返回提取的软件信息
    """
    # 检查文件
    if "file" not in request.files:
        return jsonify({"ok": False, "err": "没有上传文件"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"ok": False, "err": "没有选择文件"}), 400

    if not allowed_file(file.filename):
        return jsonify({"ok": False, "err": "只支持 .docx 文件"}), 400

    try:
        # 保存上传文件
        filename = secure_filename(file.filename)
        timestamp = str(int(os.times().elapsed * 1000))
        upload_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{filename}")
        file.save(upload_path)

        # 提取信息（返回列表）
        software_list = extract_info(upload_path)

        if not software_list:
            return jsonify({"ok": False, "err": "无法提取软件信息，请检查文件格式"}), 400

        # 返回提取的信息（支持多个软件）
        result = {
            "ok": True,
            "data": {
                "software_count": len(software_list),
                "software_list": [
                    {
                        "software_name": sw["name"],
                        "software_version": sw["version"],
                        "dev_date": sw["date"],
                        "agreement_date": calc_agreement_date(sw["date"]),
                    }
                    for sw in software_list
                ],
                "owners_count": len(software_list[0]["owners"]) if software_list[0].get("owners") else 0,
                "owners": software_list[0].get("owners", []),
                "input_file": filename,
                "upload_path": upload_path,
            },
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"ok": False, "err": f"处理失败: {str(e)}"}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    生成合作协议

    接收预览数据，生成协议文件
    """
    try:
        data = request.json

        # 获取上传文件路径
        upload_path = data.get("upload_path")
        if not upload_path or not os.path.exists(upload_path):
            return jsonify({"ok": False, "err": "上传文件不存在，请重新上传"}), 400

        # 生成协议
        result = generate_agreement(upload_path, TEMPLATE_DIR, OUTPUT_DIR)

        if not result["ok"]:
            return jsonify(result), 400

        # 保存到数据库
        software_list = data.get("software_list", [])
        first_software = software_list[0] if software_list else {}
        owners_info = data.get("owners", [])
        
        history = History(
            software_name=first_software.get("software_name", ""),
            software_version=first_software.get("software_version", "V1.0"),
            dev_date=first_software.get("dev_date", ""),
            agreement_date=first_software.get("agreement_date", ""),
            owners_count=data.get("owners_count", 0),
            owners_info=json.dumps(owners_info, ensure_ascii=False),
            input_file=data.get("input_file"),
            output_file=os.path.basename(result["output"]),
        )
        db.session.add(history)
        db.session.commit()

        # 返回下载链接
        response = {
            "ok": True,
            "output_file": os.path.basename(result["output"]),
            "download_url": f"/api/download/{os.path.basename(result['output'])}",
            "history_id": history.id,
            "software_count": result.get("software_count", 1),
            "software_list": result.get("software_list", []),
        }
        
        # 如果生成了多个文件，打包成ZIP
        if result.get("output_files") and len(result["output_files"]) > 1:
            import zipfile
            import tempfile
            
            # 创建ZIP文件
            zip_filename = f"合作协议-批量下载-{len(result['output_files'])}份.zip"
            zip_path = os.path.join(OUTPUT_DIR, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in result["output_files"]:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            # 更新返回的下载链接为ZIP文件
            response["download_url"] = f"/api/download/{zip_filename}"
            response["output_file"] = zip_filename
            response["is_zip"] = True
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"ok": False, "err": f"生成失败: {str(e)}"}), 500


@app.route("/api/download/<filename>", methods=["GET"])
def download(filename):
    """下载生成的协议文件"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"ok": False, "err": "文件不存在"}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"ok": False, "err": f"下载失败: {str(e)}"}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    """获取历史记录列表"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        pagination = (
            History.query.order_by(History.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return jsonify(
            {
                "ok": True,
                "data": {
                    "items": [item.to_dict() for item in pagination.items],
                    "total": pagination.total,
                    "page": page,
                    "per_page": per_page,
                    "pages": pagination.pages,
                },
            }
        )

    except Exception as e:
        return jsonify({"ok": False, "err": f"查询失败: {str(e)}"}), 500


@app.route("/api/history/<int:history_id>", methods=["GET"])
def get_history_detail(history_id):
    """获取单条历史记录详情"""
    try:
        history = History.query.get(history_id)
        if not history:
            return jsonify({"ok": False, "err": "记录不存在"}), 404

        return jsonify({"ok": True, "data": history.to_dict()})

    except Exception as e:
        return jsonify({"ok": False, "err": f"查询失败: {str(e)}"}), 500


@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    """删除历史记录"""
    try:
        history = History.query.get(history_id)
        if not history:
            return jsonify({"ok": False, "err": "记录不存在"}), 404

        # 删除文件
        if history.output_file:
            output_path = os.path.join(OUTPUT_DIR, history.output_file)
            if os.path.exists(output_path):
                os.remove(output_path)

        # 删除数据库记录
        db.session.delete(history)
        db.session.commit()

        return jsonify({"ok": True, "message": "删除成功"})

    except Exception as e:
        return jsonify({"ok": False, "err": f"删除失败: {str(e)}"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("软件著作权合作协议生成器 - Web 版")
    print("=" * 50)
    print(f"模板目录: {TEMPLATE_DIR}")
    print(f"上传目录: {UPLOAD_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"数据库: {DATABASE_PATH}")
    print("=" * 50)
    print("服务启动: http://localhost:5000")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)
