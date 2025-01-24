import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from src.backend.database.company_db import CompanyDatabase

async def check_company():
    db = CompanyDatabase()
    company_id = '027a543c-79c7-4475-b932-6bc2a026d75c'
    result = db.client.table('companies').select('*').eq('id', company_id).execute()
    print(f"Company data: {result.data}")

if __name__ == "__main__":
    asyncio.run(check_company()) 