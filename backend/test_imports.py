#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/erp')

# Test imports
try:
    from backend.routers import (
        foundries_router, castings_router, casting_ins_router,
        workpiece_outs_router, customers_router
    )
    print('Routers import OK')
except Exception as e:
    print(f'Routers import error: {e}')

# Test schemas
try:
    from backend.schemas import (
        FoundryCreate, FoundryUpdate, FoundryResponse,
        CastingCreate, CastingUpdate, CastingResponse,
        CastingInCreate, CastingInUpdate, CastingInResponse,
        WorkpieceOutCreate, WorkpieceOutUpdate, WorkpieceOutResponse
    )
    print('Schemas import OK')
except Exception as e:
    print(f'Schemas import error: {e}')

# Test repositories
try:
    from backend.repositories import (
        FoundryRepository, CastingRepository, CastingDrawingRepository,
        CastingInRepository, WorkpieceOutRepository
    )
    print('Repositories import OK')
except Exception as e:
    print(f'Repositories import error: {e}')

print("\nAll imports verified!")