from typing import Dict
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage
import time

class DataAnonymizer:
    """Handles data anonymization using local LLM"""
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize with a local LLM for anonymization
        
        Args:
            max_retries (int): Maximum number of connection attempts
        """
        self.max_retries = max_retries
        self.anonymizer_llm = self._initialize_anonymizer()

    def _initialize_anonymizer(self) -> OllamaLLM:
        """
        Initialize the Ollama LLM with retry logic
        
        Returns:
            OllamaLLM: Configured LLM instance
        
        Raises:
            ConnectionError: If all connection attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                llm = OllamaLLM(
                    model="phi4:latest",
                    timeout=30  # Increase timeout
                )
                # Test the connection
                llm.invoke("test")
                return llm
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(
                        f"Failed to initialize Ollama after {self.max_retries} attempts. "
                        "Please ensure Ollama is running locally. Error: " + str(e)
                    )
                print(f"Attempt {attempt + 1} failed, retrying in 2 seconds...")
                time.sleep(2)

    async def anonymize_with_llm(self, metrics: Dict) -> Dict:
        """
        Uses a local LLM to intelligently anonymize sensitive data while
        preserving statistical relationships and business context
        """
        if not self.anonymizer_llm:
            print("Warning: Anonymizer LLM not available, using basic anonymization")
            return self.basic_anonymize_metrics(metrics)

        prompt = f"""
        Given these process metrics:
        {metrics}
        
        Create an anonymized version that:
        1. Removes specific step names, role names, and department names
        2. Preserves all numerical data and statistical relationships
        3. Maintains the structure of the data
        4. Uses generic descriptors instead of specific names
        
        Format the response as a JSON with the same structure as the input, but with anonymized values.
        Keep all numerical values unchanged.
        Replace specific names with generic descriptors like "step_1", "role_A", "department_X".
        """
        
        try:
            response = await self.anonymizer_llm.agenerate([prompt])
            print(response.generations[0][0].text)
            print(50*"-")
            return response.generations[0][0].text
        except Exception as e:
            print(f"Anonymization failed: {str(e)}")
            return self.basic_anonymize_metrics(metrics)

    def basic_anonymize_metrics(self, metrics: Dict) -> Dict:
        """
        Fallback method for basic anonymization if LLM anonymization fails
        """
        try:
            anonymized = metrics.copy()
            
            if "process_actions" in anonymized:
                anonymized["process_actions"]["steps"] = [
                    f"step_{i+1}" for i in range(len(metrics["process_actions"]["steps"]))
                ]
                
            if "human_resources" in anonymized:
                anonymized["human_resources"]["roles"] = [
                    f"role_{i+1}" for i in range(len(metrics["human_resources"]["roles"]))
                ]
                
            if "impact_assessment" in anonymized:
                anonymized["impact_assessment"]["affected_departments"] = [
                    f"department_{i+1}" for i in range(len(metrics["impact_assessment"]["affected_departments"]))
                ]
                
            return anonymized
        except Exception as e:
            print(f"Basic anonymization failed: {str(e)}")
            # Return original metrics if everything fails
            return metrics 