from typing import Dict, Optional, List
import pandas as pd
from .company_db import CompanyDatabase
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import ast
import json

load_dotenv()

class SurveyDatabase:
    """Interface for survey data storage in Supabase with Google Sheets integration"""
    
    def __init__(self):
        """Initialize database connections"""
        self.company_db = CompanyDatabase()
        self.client = self.company_db.client
        self._setup_gsheets()
        
    def _setup_gsheets(self):
        """Setup Google Sheets API connection"""
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Google Sheets credentials file not found at: {creds_path}")
            
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        self.gsheets_client = gspread.authorize(creds)
        
    def _extract_sheet_id(self, sheet_url: str) -> str:
        """Extract sheet ID from Google Sheets URL"""
        try:
            if 'spreadsheets/d/' in sheet_url:
                sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
                return sheet_id
            raise ValueError("Invalid Google Sheets URL format")
        except Exception as e:
            raise ValueError(f"Error extracting sheet ID: {str(e)}")
            
    def _safe_eval_list(self, value: str) -> List:
        """Safely evaluate string representations of lists"""
        try:
            if not value or value.lower() == 'none':
                return []
            # Try ast.literal_eval first
            try:
                result = ast.literal_eval(value)
                if isinstance(result, list):
                    return result
            except:
                pass
            
            # Try JSON parse
            try:
                result = json.loads(value)
                if isinstance(result, list):
                    return result
            except:
                pass
                
            # If it's a comma-separated string
            if ',' in value:
                return [item.strip() for item in value.split(',')]
                
            # If it's a single value
            return [value]
            
        except Exception as e:
            print(f"Warning: Could not parse list value '{value}': {str(e)}")
            return []
            
    async def get_survey_data(self, company_id: str) -> Optional[pd.DataFrame]:
        """Retrieve survey data for a company from Google Sheets"""
        try:
            # Get company record with survey_data URL
            response = self.client.table('companies').select("*").eq('id', company_id).execute()
            
            if not response.data:
                print(f"No company found with ID: {company_id}")
                return None
                
            sheet_url = response.data[0].get('survey_data')
            if not sheet_url:
                print(f"No survey_data URL found for company: {company_id}")
                return None
                
            # Get data from Google Sheets
            try:
                sheet_id = self._extract_sheet_id(sheet_url)
                print(f"Accessing sheet with ID: {sheet_id}")
                
                sheet = self.gsheets_client.open_by_key(sheet_id).sheet1
                data = sheet.get_all_records()
                
                if not data:
                    print(f"No data found in Google Sheet for company: {company_id}")
                    return None
                    
                print(f"Raw data from sheet: {data[:1]}")  # Print first row for debugging
                
                # Convert to DataFrame
                df = pd.DataFrame(data)
                
                # Convert string columns that should be lists
                list_columns = ['main_challenges', 'current_systems_used']
                for col in list_columns:
                    if col in df.columns:
                        df[col] = df[col].apply(self._safe_eval_list)
                        
                # Ensure required columns exist
                required_columns = [
                    'process_name', 'process_description', 'total_time_minutes',
                    'people_involved', 'daily_frequency', 'error_rate_percentage',
                    'error_impact_rating', 'business_importance', 'automation_potential'
                ]
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"Warning: Missing required columns: {missing_columns}")
                    
                return df
                
            except Exception as e:
                print(f"Error accessing Google Sheet: {str(e)}")
                print(f"Sheet URL: {sheet_url}")
                return None
            
        except Exception as e:
            print(f"Error retrieving survey data: {str(e)}")
            return None
            
    async def store_survey_data(self, company_id: str, survey_data: List[Dict]) -> bool:
        """
        Store survey data for a company
        
        Args:
            company_id: Company ID
            survey_data: List of survey response dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            # Add company_id to each survey record
            for record in survey_data:
                record['company_id'] = company_id
                
            # Insert survey data
            response = self.client.table('survey_data').insert(survey_data).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"Error storing survey data: {str(e)}")
            return False 