#!/usr/bin/env python3
import subprocess
import sys

# Check Python version
result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
print(f"Python: {result.stdout.strip()}")

# Check if fastapi is importable
try:
    import fastapi
    print(f"FastAPI: {fastapi.__version__}")
except ImportError:
    print("FastAPI: NOT INSTALLED")

try:
    import pydantic
    print(f"Pydantic: {pydantic.__version__}")
except ImportError:
    print("Pydantic: NOT INSTALLED")

try:
    import sqlalchemy
    print(f"SQLAlchemy: {sqlalchemy.__version__}")
except ImportError:
    print("SQLAlchemy: NOT INSTALLED")

# Now test backend imports
sys.path.insert(0, '/home/ubuntu/erp')

try:
    from backend.routers import (
        foundries_router, castings_router, casting_ins_router,
        workpiece_outs_router, customers_router
    )
    print('\nRouters import OK')
except Exception as e:
    print(f'\nRouters import error: {e}')

try:
    from backend.schemas import (
        FoundryCreate, CastingCreate, CastingInCreate, WorkpieceOutCreate
    )
    print('Schemas import OK')
except Exception as e:
    print(f'Schemas import error: {e}')

try:
    from backend.repositories import (
        FoundryRepository, CastingRepository, CastingInRepository, WorkpieceOutRepository
    )
    print('Repositories import OK')
except Exception as e:
    print(f'Repositories import error: {e}')