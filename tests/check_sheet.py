import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from src.backend.database.survey_db import SurveyDatabase

async def check_sheet():
    db = SurveyDatabase()
    company_id = '027a543c-79c7-4475-b932-6bc2a026d75c'
    data = await db.get_survey_data(company_id)
    print(f"Survey data: {data}")

if __name__ == "__main__":
    asyncio.run(check_sheet()) 