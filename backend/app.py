# -*- coding: utf-8 -*-
"""Flask 主程序 - 软件著作权合作协议生成器 Web 版"""

import os
import json
import subprocess
import time
import secrets
from functools import wraps
from flask import Flask, request, jsonify, send_file, send_from_directory, session, g
from flask_session import Session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, User, History
from utils import extract_info, calc_agreement_date, generate_agreement, check_minor_owners


# 认证装饰器
def login_required(f):
    """需要登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"ok": False, "err": "请先登录", "need_login": True}), 401
        user = User.query.get(user_id)
        if not user:
            session.pop("user_id", None)
            return jsonify({"ok": False, "err": "用户不存在", "need_login": True}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """需要管理员权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"ok": False, "err": "请先登录", "need_login": True}), 401
        user = User.query.get(user_id)
        if not user:
            session.pop("user_id", None)
            return jsonify({"ok": False, "err": "用户不存在", "need_login": True}), 401
        if user.role != "admin":
            return jsonify({"ok": False, "err": "需要管理员权限"}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def convert_doc_to_docx(doc_path):
    """将 .doc 转换为 .docx（使用 Windows Word）"""
    import shutil
    import uuid
    
    # 创建 Windows 临时目录
    win_temp_dir = "D:\\temp"
    temp_id = str(uuid.uuid4())[:8]
    
    # 复制文件到 Windows 文件系统
    temp_doc = os.path.join(win_temp_dir, f"{temp_id}_convert.doc")
    temp_docx = os.path.join(win_temp_dir, f"{temp_id}_convert.docx")
    
    # WSL 路径
    wsl_temp_doc = f"/mnt/d/temp/{temp_id}_convert.doc"
    wsl_temp_docx = f"/mnt/d/temp/{temp_id}_convert.docx"
    
    try:
        # 确保临时目录存在
        os.makedirs("/mnt/d/temp", exist_ok=True)
        
        # 复制到 Windows 文件系统
        shutil.copy2(doc_path, wsl_temp_doc)
        print(f"[DEBUG] 复制文件到: {wsl_temp_doc}")
        
        # PowerShell 转换脚本
        ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open("{temp_doc}")
    $doc.SaveAs("{temp_docx}", 16)
    $doc.Close()
    Write-Host "Success"
}} catch {{
    Write-Host "Error: $_"
}} finally {{
    $word.Quit()
}}
'''
        
        print(f"[DEBUG] 执行 PowerShell 转换...")
        result = subprocess.run(
            ['powershell.exe', '-Command', ps_script],
            capture_output=True,
            timeout=60
        )
        
        output = result.stdout.decode('utf-8', errors='ignore')
        print(f"[DEBUG] PowerShell 输出: {output}")
        
        time.sleep(2)  # 等待文件写入完成
        
        # 检查转换后的文件
        if os.path.exists(wsl_temp_docx):
            # 复制到上传目录
            final_docx = doc_path.rsplit('.', 1)[0] + '.docx'
            shutil.copy2(wsl_temp_docx, final_docx)
            print(f"✅ .doc 转换成功: {final_docx}")
            
            # 清理临时文件
            try:
                os.remove(wsl_temp_doc)
                os.remove(wsl_temp_docx)
            except:
                pass
            
            return final_docx
        else:
            print(f"❌ .doc 转换失败: 文件不存在")
            
    except Exception as e:
        print(f"❌ .doc 转换异常: {e}")
    finally:
        # 清理临时文件
        try:
            if os.path.exists(wsl_temp_doc):
                os.remove(wsl_temp_doc)
        except:
            pass
    
    return None

# 配置
app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-in-production"

# Session 配置（使用文件系统存储，支持多 worker）
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "/app/backend/flask_session/"
Session(app)

# CORS 配置（支持 credentials）
CORS(app, supports_credentials=True)

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
    try:
        db.create_all()
    except Exception as e:
        pass  # 表已存在，忽略
    User.create_admin()  # 创建默认管理员

ALLOWED_EXTENSIONS = {"docx", "doc"}


def allowed_file(filename):
    """检查文件扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "message": "服务运行正常"})


# ==================== 用户认证 API ====================

@app.route("/api/login", methods=["POST"])
def login():
    """用户登录"""
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"ok": False, "err": "用户名和密码不能为空"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"ok": False, "err": "用户名或密码错误"}), 401

    session["user_id"] = user.id
    return jsonify({
        "ok": True,
        "data": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    """用户登出"""
    session.pop("user_id", None)
    return jsonify({"ok": True, "message": "已登出"})


@app.route("/api/me", methods=["GET"])
@login_required
def get_current_user():
    """获取当前登录用户"""
    return jsonify({
        "ok": True,
        "data": {
            "id": g.current_user.id,
            "username": g.current_user.username,
            "role": g.current_user.role,
        }
    })


# ==================== 用户管理 API（管理员专用）====================

@app.route("/api/users", methods=["GET"])
@admin_required
def list_users():
    """获取用户列表"""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        "ok": True,
        "data": [u.to_dict() for u in users]
    })


@app.route("/api/users", methods=["POST"])
@admin_required
def create_user():
    """创建用户"""
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"ok": False, "err": "用户名和密码不能为空"}), 400

    if role not in ["admin", "user"]:
        return jsonify({"ok": False, "err": "角色只能是 admin 或 user"}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"ok": False, "err": "用户名已存在"}), 400

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"ok": True, "data": user.to_dict()})


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """删除用户"""
    if user_id == g.current_user.id:
        return jsonify({"ok": False, "err": "不能删除自己"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"ok": False, "err": "用户不存在"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"ok": True, "message": "删除成功"})


@app.route("/api/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_user_password(user_id):
    """重置用户密码"""
    data = request.json
    new_password = data.get("password", "")

    if not new_password:
        return jsonify({"ok": False, "err": "密码不能为空"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"ok": False, "err": "用户不存在"}), 404

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"ok": True, "message": "密码已重置"})


# ==================== 协议生成 API ====================

@app.route("/api/preview-batch", methods=["POST"])
@login_required
def preview_batch():
    """
    批量预览提取的信息

    接收多个 .docx 文件，返回所有提取的软件信息
    """
    # 检查文件
    if "files" not in request.files:
        return jsonify({"ok": False, "err": "没有上传文件"}), 400

    files = request.files.getlist("files")

    if not files or all(f.filename == "" for f in files):
        return jsonify({"ok": False, "err": "没有选择文件"}), 400

    # 过滤有效文件
    valid_files = [f for f in files if f.filename and allowed_file(f.filename)]
    
    if not valid_files:
        return jsonify({"ok": False, "err": "没有有效的 .doc/.docx 文件"}), 400

    try:
        all_software = []
        all_owners = []
        upload_paths = []
        
        for file in valid_files:
            # 保存上传文件（使用原始文件名判断类型）
            original_filename = file.filename
            filename = secure_filename(original_filename)
            timestamp = str(int(time.time() * 1000))
            upload_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{filename}")
            file.save(upload_path)
            
            # 如果是 .doc 文件，转换为 .docx（使用原始文件名判断）
            actual_path = upload_path
            if original_filename.lower().endswith('.doc') and not original_filename.lower().endswith('.docx'):
                print(f"[INFO] 检测到 .doc 文件: {original_filename}", flush=True)
                converted_path = convert_doc_to_docx(upload_path)
                if converted_path:
                    actual_path = converted_path
                    print(f"[INFO] 使用转换后的文件: {actual_path}", flush=True)
                else:
                    print(f"[ERROR] .doc 转换失败，跳过该文件", flush=True)
                    continue
            
            upload_paths.append(actual_path)
            
            # 提取信息
            software_list = extract_info(actual_path)
            
            if software_list:
                # 添加文件来源信息
                for sw in software_list:
                    sw["source_file"] = filename
                all_software.extend(software_list)
                
                # 合并著作权人（去重）
                if software_list[0].get("owners"):
                    for owner in software_list[0]["owners"]:
                        if owner not in all_owners:
                            all_owners.append(owner)

        if not all_software:
            return jsonify({"ok": False, "err": "无法提取软件信息"}), 400

        # 检查未成年人著作权人
        minors = []
        if all_software:
            # 使用第一个软件的协议日期检查
            first_agreement_date = calc_agreement_date(all_software[0]["date"])
            minors = check_minor_owners(all_owners, first_agreement_date)

        # 返回提取的信息
        result = {
            "ok": True,
            "data": {
                "file_count": len(valid_files),
                "software_count": len(all_software),
                "software_list": [
                    {
                        "software_name": sw["name"],
                        "software_version": sw["version"],
                        "dev_date": sw["date"],
                        "agreement_date": calc_agreement_date(sw["date"]),
                        "source_file": sw.get("source_file", ""),
                    }
                    for sw in all_software
                ],
                "owners_count": len(all_owners),
                "owners": all_owners,
                "upload_paths": upload_paths,
                "minors": minors,  # 添加未成年人信息
            },
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        print(f"[ERROR] preview_batch 处理失败: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({"ok": False, "err": f"处理失败: {str(e)}"}), 500


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
@login_required
def generate():
    """
    生成合作协议

    接收预览数据，生成协议文件
    """
    try:
        data = request.json

        # 支持批量处理
        upload_paths = data.get("upload_paths", [])
        if isinstance(upload_paths, str):
            upload_paths = [upload_paths]
        
        if not upload_paths:
            return jsonify({"ok": False, "err": "没有上传文件"}), 400
        
        # 验证文件存在
        valid_paths = [p for p in upload_paths if os.path.exists(p)]
        if not valid_paths:
            return jsonify({"ok": False, "err": "上传文件不存在，请重新上传"}), 400

        # 接收自定义协议签署日期
        custom_agreement_date = data.get("custom_agreement_date")
        
        # 批量生成协议
        all_output_files = []
        all_software_list = []
        
        for upload_path in valid_paths:
            result = generate_agreement(upload_path, TEMPLATE_DIR, OUTPUT_DIR, custom_agreement_date)
            
            if result["ok"]:
                if result.get("output_files"):
                    all_output_files.extend(result["output_files"])
                else:
                    all_output_files.append(result["output"])
                
                all_software_list.extend(result.get("software_list", []))

        if not all_output_files:
            return jsonify({"ok": False, "err": "生成失败，没有生成任何协议"}), 400

        # 保存到数据库
        software_list = data.get("software_list", [])
        first_software = software_list[0] if software_list else {}
        owners_info = data.get("owners", [])
        
        history = History(
            user_id=g.current_user.id,  # 关联当前用户
            software_name=first_software.get("software_name", ""),
            software_version=first_software.get("software_version", "V1.0"),
            dev_date=first_software.get("dev_date", ""),
            agreement_date=first_software.get("agreement_date", ""),
            owners_count=data.get("owners_count", 0),
            owners_info=json.dumps(owners_info, ensure_ascii=False),
            input_file=data.get("input_file"),
            output_file=f"批量生成{len(all_output_files)}份协议",
        )
        db.session.add(history)
        db.session.commit()

        # 如果只有1份协议，直接返回docx文件
        if len(all_output_files) == 1:
            output_file = all_output_files[0]
            filename = os.path.basename(output_file)
            response = {
                "ok": True,
                "output_file": filename,
                "download_url": f"/api/download/{filename}",
                "software_count": len(all_software_list),
                "software_list": all_software_list,
                "file_count": 1,
                "is_zip": False,
            }
            return jsonify(response)

        # 多份协议：打包zip
        import zipfile
        
        zip_filename = f"合作协议-批量下载-{len(all_output_files)}份.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in all_output_files:
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
        
        # 返回下载链接
        response = {
            "ok": True,
            "output_file": zip_filename,
            "download_url": f"/api/download/{zip_filename}",
            "software_count": len(all_software_list),
            "software_list": all_software_list,
            "file_count": len(all_output_files),
            "is_zip": True,
        }
        
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
@admin_required
def get_history():
    """获取历史记录列表（仅管理员）"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        pagination = (
            History.query.order_by(History.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        # 添加用户名信息
        items = []
        for item in pagination.items:
            data = item.to_dict()
            data["username"] = item.user.username if item.user else "未知"
            items.append(data)

        return jsonify(
            {
                "ok": True,
                "data": {
                    "items": items,
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
@admin_required
def get_history_detail(history_id):
    """获取单条历史记录详情（仅管理员）"""
    try:
        history = History.query.get(history_id)
        if not history:
            return jsonify({"ok": False, "err": "记录不存在"}), 404

        data = history.to_dict()
        data["username"] = history.user.username if history.user else "未知"
        return jsonify({"ok": True, "data": data})

    except Exception as e:
        return jsonify({"ok": False, "err": f"查询失败: {str(e)}"}), 500


@app.route("/api/history/<int:history_id>", methods=["DELETE"])
@admin_required
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
