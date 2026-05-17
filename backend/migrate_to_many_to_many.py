"""
迁移脚本：将 1:N 关系迁移到 M2M 多对多关系

创建关联表并迁移现有数据：
1. customer_foundries (customer_id, foundry_id) - 从 Foundry.customer_id 迁移
2. customer_castings (customer_id, casting_id) - 从 Casting.customer_id 迁移
3. part_castings (part_id, casting_id) - 预留，未来用于零件与铸件的关联

Usage:
    cd /home/ubuntu/erp/backend
    python3 migrate_to_many_to_many.py

依赖:
    - SQLAlchemy (通过 from backend.models import ... 导入)
    - database.py 中的 Base, engine, SessionLocal
"""

import sys
import os
from datetime import datetime

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# 导入数据库配置
try:
    from database import Base, engine, SessionLocal, get_db
    from models import Customer, Foundry, Casting, Part
    from models import CustomerFoundry, PartCasting
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在 /home/ubuntu/erp/backend 目录下运行此脚本")
    sys.exit(1)


def get_db_session():
    """获取数据库会话"""
    return SessionLocal()


def create_tables():
    """创建关联表（如果不存在）"""
    print("\n[Step 1] 创建关联表...")
    
    with engine.connect() as conn:
        # customer_foundries 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_foundries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                foundry_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (foundry_id) REFERENCES foundries(id) ON DELETE CASCADE,
                UNIQUE(customer_id, foundry_id)
            )
        """))
        print("  - customer_foundries OK")
        
        # customer_castings 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (casting_id) REFERENCES castings(id) ON DELETE CASCADE,
                UNIQUE(customer_id, casting_id)
            )
        """))
        print("  - customer_castings OK")
        
        # part_castings 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS part_castings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                casting_id INTEGER NOT NULL,
                quantity NUMERIC(10, 3) DEFAULT 1,
                notes VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE,
                FOREIGN KEY (casting_id) REFERENCES castings(id) ON DELETE CASCADE,
                UNIQUE(part_id, casting_id)
            )
        """))
        print("  - part_castings OK")
        
        conn.commit()


def migrate_foundry_data():
    """迁移 Foundry.customer_id 到 customer_foundries 表"""
    print("\n[Step 2] 迁移 Foundry 数据...")
    
    db = get_db_session()
    try:
        foundries = db.query(Foundry).filter(
            Foundry.customer_id.isnot(None)
        ).all()
        
        migrated_count = 0
        for foundry in foundries:
            try:
                existing = db.query(CustomerFoundry).filter(
                    CustomerFoundry.customer_id == foundry.customer_id,
                    CustomerFoundry.foundry_id == foundry.id
                ).first()
                
                if existing:
                    continue
                
                cf = CustomerFoundry(
                    customer_id=foundry.customer_id,
                    foundry_id=foundry.id
                )
                db.add(cf)
                migrated_count += 1
                
            except IntegrityError:
                db.rollback()
                continue
        
        db.commit()
        print(f"  - 迁移 {migrated_count} 条 Foundry -> Customer 关联")
        return migrated_count
        
    except Exception as e:
        db.rollback()
        print(f"  - 迁移 Foundry 数据失败: {e}")
        raise
    finally:
        db.close()


def migrate_casting_data():
    """迁移 Casting.customer_id 到 customer_castings 表"""
    print("\n[Step 3] 迁移 Casting 数据...")
    
    db = get_db_session()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(castings)"))
            columns = [row[1] for row in result.fetchall()]
        
        if 'customer_id' not in columns:
            print("  - Casting 表没有 customer_id 列，跳过迁移")
            return 0
        
        castings = db.query(Casting).filter(
            Casting.customer_id.isnot(None)
        ).all()
        
        migrated_count = 0
        for casting in castings:
            try:
                existing = db.execute(
                    text("SELECT id FROM customer_castings WHERE customer_id = :cid AND casting_id = :cgid"),
                    {"cid": casting.customer_id, "cgid": casting.id}
                ).fetchone()
                
                if existing:
                    continue
                
                db.execute(
                    text("""
                        INSERT INTO customer_castings (customer_id, casting_id, created_at, updated_at)
                        VALUES (:cid, :cgid, datetime('now'), datetime('now'))
                    """),
                    {"cid": casting.customer_id, "cgid": casting.id}
                )
                migrated_count += 1
                
            except IntegrityError:
                continue
        
        db.commit()
        print(f"  - 迁移 {migrated_count} 条 Casting -> Customer 关联")
        return migrated_count
        
    except Exception as e:
        print(f"  - 迁移 Casting 数据失败: {e}")
        return 0
    finally:
        db.close()


def verify_migration():
    """验证迁移结果"""
    print("\n[Step 4] 验证迁移结果...")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM customer_foundries"))
        cf_count = result.fetchone()[0]
        print(f"  - customer_foundries: {cf_count} 条记录")
        
        result = conn.execute(text("SELECT COUNT(*) FROM customer_castings"))
        cc_count = result.fetchone()[0]
        print(f"  - customer_castings: {cc_count} 条记录")
        
        result = conn.execute(text("SELECT COUNT(*) FROM part_castings"))
        pc_count = result.fetchone()[0]
        print(f"  - part_castings: {pc_count} 条记录")
        
        print("\n  示例数据 - customer_foundries:")
        result = conn.execute(text("""
            SELECT cf.id, c.name as customer_name, f.name as foundry_name
            FROM customer_foundries cf
            JOIN customers c ON cf.customer_id = c.id
            JOIN foundries f ON cf.foundry_id = f.id
            LIMIT 5
        """))
        for row in result.fetchall():
            print(f"    [{row[0]}] {row[1]} <-> {row[2]}")
        
        print("\n  示例数据 - customer_castings:")
        result = conn.execute(text("""
            SELECT cc.id, c.name as customer_name, cg.name as casting_name
            FROM customer_castings cc
            JOIN customers c ON cc.customer_id = c.id
            JOIN castings cg ON cc.casting_id = cg.id
            LIMIT 5
        """))
        for row in result.fetchall():
            print(f"    [{row[0]}] {row[1]} <-> {row[2]}")


def verify_foreign_key_access():
    """验证通过关联表可以访问原有数据"""
    print("\n[Step 5] 验证关联表查询...")
    
    db = get_db_session()
    try:
        print("  关联表查询示例:")
        result = db.execute(
            text("""
                SELECT c.name as customer, f.name as foundry
                FROM customer_foundries cf
                JOIN customers c ON cf.customer_id = c.id
                JOIN foundries f ON cf.foundry_id = f.id
                LIMIT 3
            """)
        )
        for row in result.fetchall():
            print(f"    Customer '{row[0]}' -> Foundry '{row[1]}'")
        
        print("  - 关联表查询验证通过")
        return True
        
    except Exception as e:
        print(f"  - 关联表查询验证失败: {e}")
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("Migration: 1:N to M2M Relationships")
    print("=" * 60)
    print(f"Database: {engine.url.database}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        create_tables()
        foundry_migrated = migrate_foundry_data()
        casting_migrated = migrate_casting_data()
        verify_migration()
        verify_foreign_key_access()
        
        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print(f"  - customer_foundries: {foundry_migrated} new records")
        print(f"  - customer_castings: {casting_migrated} new records")
        print(f"  - part_castings: 0 records (reserved)")
        
    except Exception as e:
        print(f"\nMigration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()