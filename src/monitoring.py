import re
import time
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_monitor.log'),
        logging.StreamHandler()
    ]
)

class ChatbotMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def detect_pii(self, text: str) -> bool:
        """Detect Personally Identifiable Information in text"""
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        credit_card_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
        
        patterns = [email_pattern, phone_pattern, credit_card_pattern]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def measure_latency(self, start_time: float) -> float:
        """Calculate response latency in milliseconds"""
        return (time.time() - start_time) * 1000  # Convert to ms
    
    def log_response(self, user_id: str, query: str, response: str, 
                    start_time: float, error: Optional[str] = None) -> Dict[str, Any]:
        """Log chatbot response with monitoring metrics"""
        
        latency = self.measure_latency(start_time)
        has_pii = self.detect_pii(response)
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "user_id": user_id,
            "query": query,
            "response": response,
            "latency_ms": round(latency, 2),
            "has_pii": has_pii,
            "error": error,
            "response_length": len(response)
        }
        
        # Log based on conditions
        if error:
            self.logger.error(f"Error response: {log_entry}")
        elif has_pii:
            self.logger.warning(f"PII detected: {log_entry}")
        elif latency > 1000:  # 1 second threshold
            self.logger.warning(f"High latency: {log_entry}")
        else:
            self.logger.info(f"Response logged: {log_entry}")
        
        return log_entry
    
    def process_chatbot_logs(self, log_file: str):
        """Process sample chatbot logs for testing"""
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            for log in logs:
                start_time = time.time()
                # Simulate processing delay
                time.sleep(0.1)
                self.log_response(
                    log['user_id'],
                    log['query'],
                    log['response'],
                    start_time,
                    log.get('error')
                )
                
        except FileNotFoundError:
            self.logger.error(f"Log file {log_file} not found")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in log file")

# Example usage
if __name__ == "__main__":
    monitor = ChatbotMonitor()
    
    # Test with sample data
    test_cases = [
        {
            "user_id": "user123",
            "query": "What's my email?",
            "response": "Your email is john.doe@example.com",
            "error": None
        },
        {
            "user_id": "user456",
            "query": "How do I reset password?",
            "response": "Visit settings and click reset",
            "error": None
        },
        {
            "user_id": "user789",
            "query": "What's my phone?",
            "response": "Your number is 555-123-4567",
            "error": None
        }
    ]
    
    # Save test cases to file
    with open('sample_chatbot_logs.json', 'w') as f:
        json.dump(test_cases, f, indent=2)
    
    # Process the logs
    monitor.process_chatbot_logs('sample_chatbot_logs.json')