from typing import Dict, Optional, List
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class CompanyDatabase:
    """Interface for company data storage in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
    async def store_company_data(self, data: Dict) -> str:
        """
        Store company data in Supabase
        
        Args:
            data: Company data dictionary
            
        Returns:
            str: Company ID
        """
        try:
            response = await self.client.table('companies').insert(data).execute()
            return response.data[0]['id']
        except Exception as e:
            print(f"Error storing company data: {str(e)}")
            raise
            
    async def get_company_data(self, company_id: str) -> Optional[Dict]:
        """
        Retrieve company data
        
        Args:
            company_id: Company UUID
            
        Returns:
            Optional[Dict]: Company data or None if not found
        """
        try:
            response = self.client.table('companies').select("*").eq('id', company_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error retrieving company data: {str(e)}")
            return None

    async def get_all_companies(self) -> List[Dict]:
        """
        Retrieve all companies from the database
        
        Returns:
            List[Dict]: List of company data dictionaries containing id and name
        """
        try:
            response = self.client.table('companies').select("id,company_name").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving companies: {str(e)}")
            return [] 