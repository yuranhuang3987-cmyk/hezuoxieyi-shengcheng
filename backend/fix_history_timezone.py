# -*- coding: utf-8 -*-
"""
一次性修复脚本：把数据库里已有记录的创建时间从 UTC 修正为北京时间（+8 小时）。

背景：基础镜像 python:3.11-slim 默认时区为 UTC，时区修复部署之前生成的
历史记录，其 created_at 比真实北京时间慢 8 小时。本脚本对这些旧记录统一 +8 小时。

安全设计：
- 默认只「预览」，不改任何数据；加 --apply 才真正写入。
- --apply 前自动把整个数据库复制一份备份（出问题可直接还原）。
- 只应在「时区修复部署后、尚未生成任何新协议之前」运行一次；
  此时库里所有记录都还是 UTC，整体 +8 小时即全部修正。

用法（在服务器上）：
    # 容器内运行（推荐，重新构建部署后脚本已在镜像里）
    docker exec agreement-generator python /app/backend/fix_history_timezone.py            # 预览
    docker exec agreement-generator python /app/backend/fix_history_timezone.py --apply    # 执行

    # 或直接对宿主上的数据库文件运行
    python fix_history_timezone.py --db ./data/app.db            # 预览
    python fix_history_timezone.py --db ./data/app.db --apply    # 执行

    # 同时修正用户表的创建时间
    docker exec agreement-generator python /app/backend/fix_history_timezone.py --apply --include-users
"""

import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta


def shift_time(value, hours):
    """把存储的时间字符串解析后加上指定小时数，返回同格式字符串。

    兼容带/不带微秒、空格或 T 分隔的 ISO 格式；无法解析则原样返回（跳过）。
    """
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    new_dt = dt + timedelta(hours=hours)
    # 用空格分隔，与 SQLAlchemy 在 SQLite 中的默认存储格式一致（微秒为0时自动省略）
    return new_dt.isoformat(sep=" ")


def process_table(conn, table, hours, apply):
    """预览或修正一张表的 created_at。返回 (受影响行数, 预览明细列表)。"""
    cur = conn.cursor()
    # 取一个有代表性的名称列用于预览展示
    name_col = "software_name" if table == "history" else "username"
    rows = cur.execute(
        f"SELECT id, {name_col}, created_at FROM {table} ORDER BY id"
    ).fetchall()

    detail = []
    updates = []
    for rid, name, created in rows:
        new_val = shift_time(created, hours)
        if new_val is None:
            detail.append((rid, name, created, "（无法解析，跳过）"))
            continue
        detail.append((rid, name, created, new_val))
        updates.append((new_val, rid))

    if apply and updates:
        cur.executemany(
            f"UPDATE {table} SET created_at = ? WHERE id = ?", updates
        )

    return len(updates), detail


def print_detail(table, detail):
    print(f"\n===== 表 {table}（共 {len(detail)} 条）=====")
    print(f"{'ID':>4}  {'名称':<24}  {'原创建时间(UTC)':<26} -> 修正后(北京时间)")
    for rid, name, old, new in detail:
        name_disp = (name or "")[:24]
        print(f"{rid:>4}  {name_disp:<24}  {str(old):<26} -> {new}")


def main():
    parser = argparse.ArgumentParser(description="把历史记录创建时间从 UTC 修正为北京时间(+8小时)")
    parser.add_argument("--db", default="/app/database/app.db", help="SQLite 数据库路径（默认容器内 /app/database/app.db）")
    parser.add_argument("--hours", type=int, default=8, help="加的小时数（默认 8，即 UTC->北京时间）")
    parser.add_argument("--apply", action="store_true", help="真正写入；不加则只预览")
    parser.add_argument("--include-users", action="store_true", help="同时修正 users 表的创建时间")
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"❌ 找不到数据库文件：{args.db}")
        sys.exit(1)

    tables = ["history"]
    if args.include_users:
        tables.append("users")

    # --apply 前先整库备份
    if args.apply:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{args.db}.bak_{stamp}"
        shutil.copy2(args.db, backup)
        print(f"📦 已备份数据库到：{backup}")

    conn = sqlite3.connect(args.db)
    try:
        total = 0
        for table in tables:
            count, detail = process_table(conn, table, args.hours, args.apply)
            print_detail(table, detail)
            total += count
        if args.apply:
            conn.commit()
            print(f"\n✅ 已修正 {total} 条记录，每条创建时间 +{args.hours} 小时。")
        else:
            print(f"\n👀 以上为预览（共 {total} 条将被修改），未改动任何数据。")
            print("   确认无误后，加 --apply 参数重新运行即可真正写入。")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
