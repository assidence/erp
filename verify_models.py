"""
Database Model Verification Script
Tests that all database models can be created successfully.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import setup_logging, settings
from backend.database import engine, Base, init_db
from backend.models import (
    Customer, Supplier, Part, PartDrawing,
    MaterialIn, ProductOut, ProductionPlan,
    PaymentPlan, QualityIssue, Attachment
)
from sqlalchemy import inspect


def verify_tables():
    """Verify all expected tables exist in the database."""
    setup_logging()
    print("=" * 60)
    print("Database Model Verification")
    print("=" * 60)

    # Initialize database
    print("\n1. Creating database tables...")
    init_db()
    print("   ✓ Tables created successfully")

    # Inspect tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n2. Tables in database ({len(tables)} total):")
    expected_tables = [
        "customers", "suppliers", "parts", "part_drawings",
        "material_ins", "product_outs", "production_plans",
        "payment_plans", "quality_issues", "attachments"
    ]

    all_found = True
    for table in expected_tables:
        if table in tables:
            print(f"   ✓ {table}")
        else:
            print(f"   ✗ {table} (MISSING)")
            all_found = False

    # Show table columns for each table
    print("\n3. Table columns:")
    for table in sorted(tables):
        columns = inspector.get_columns(table)
        print(f"\n   {table}:")
        for col in columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            print(f"      - {col['name']}: {col['type']} ({nullable})")

    # Verify unique constraints
    print("\n4. Unique constraints:")
    constraints = inspector.get_unique_constraints("material_ins")
    if any(c["name"] == "uq_material_in_delivery_note" for c in constraints):
        print("   ✓ material_ins.delivery_note_no is unique")
    else:
        print("   ✗ material_ins.delivery_note_no unique constraint missing")

    constraints = inspector.get_unique_constraints("product_outs")
    if any(c["name"] == "uq_product_out_delivery_note" for c in constraints):
        print("   ✓ product_outs.delivery_note_no is unique")
    else:
        print("   ✗ product_outs.delivery_note_no unique constraint missing")

    print("\n" + "=" * 60)
    if all_found:
        print("✓ VERIFICATION PASSED - All tables created correctly")
    else:
        print("✗ VERIFICATION FAILED - Some tables are missing")
    print("=" * 60)

    return all_found


if __name__ == "__main__":
    success = verify_tables()
    sys.exit(0 if success else 1)