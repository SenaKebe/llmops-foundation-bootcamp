import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

class FeedbackCollector:
    def __init__(self, storage_file: str = 'feedback_data.json'):
        self.storage_file = storage_file
        self.feedback_types = ['bug_report', 'feature_request', 'general_feedback', 'incorrect_response']
    
    def validate_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate feedback data structure"""
        required_fields = ['user_id', 'feedback_type', 'description']
        
        if not all(field in feedback_data for field in required_fields):
            return False
        
        if feedback_data['feedback_type'] not in self.feedback_types:
            return False
        
        if len(feedback_data['description'].strip()) < 10:
            return False
            
        return True
    
    def collect_feedback(self, user_id: str, feedback_type: str, 
                        description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect and store user feedback"""
        
        feedback_data = {
            "feedback_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "user_id": user_id,
            "feedback_type": feedback_type,
            "description": description,
            "metadata": metadata or {}
        }
        
        if not self.validate_feedback(feedback_data):
            raise ValueError("Invalid feedback data")
        
        # Load existing feedback
        try:
            with open(self.storage_file, 'r') as f:
                existing_feedback = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_feedback = []
        
        # Add new feedback
        existing_feedback.append(feedback_data)
        
        # Save updated feedback
        with open(self.storage_file, 'w') as f:
            json.dump(existing_feedback, f, indent=2)
        
        return feedback_data
    
    def get_feedback(self, feedback_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve feedback, optionally filtered by type"""
        try:
            with open(self.storage_file, 'r') as f:
                feedback = json.load(f)
            
            if feedback_type:
                return [item for item in feedback if item['feedback_type'] == feedback_type]
            return feedback
            
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def cli_collect_feedback(self):
        """Command-line interface for collecting feedback"""
        print("=== Chatbot Feedback Collection ===")
        
        user_id = input("User ID: ").strip()
        if not user_id:
            print("User ID is required!")
            return
        
        print("\nFeedback types:")
        for i, ftype in enumerate(self.feedback_types, 1):
            print(f"{i}. {ftype}")
        
        try:
            choice = int(input("\nSelect feedback type (number): "))
            if choice < 1 or choice > len(self.feedback_types):
                print("Invalid selection")
                return
            feedback_type = self.feedback_types[choice - 1]
        except ValueError:
            print("Please enter a valid number")
            return
        
        description = input("\nDescription: ").strip()
        if len(description) < 10:
            print("Description must be at least 10 characters")
            return
        
        # Optional metadata
        print("\nOptional metadata (press enter to skip):")
        conversation_id = input("Conversation ID: ").strip()
        rating_input = input("Rating (1-5): ").strip()
        
        metadata = {}
        if conversation_id:
            metadata['conversation_id'] = conversation_id
        if rating_input:
            try:
                rating = int(rating_input)
                if 1 <= rating <= 5:
                    metadata['rating'] = rating
                else:
                    print("Rating must be between 1 and 5")
            except ValueError:
                print("Rating must be a number")
        
        try:
            feedback = self.collect_feedback(user_id, feedback_type, description, metadata)
            print(f"\n✅ Feedback submitted successfully! ID: {feedback['feedback_id']}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")

# Example usage
if __name__ == "__main__":
    collector = FeedbackCollector()
    
    # Test data
    test_feedback = [
        {
            "user_id": "12345",
            "feedback_type": "bug_report",
            "description": "Bot gave wrong answer to refund request.",
            "metadata": {"conversation_id": "conv_abc123", "rating": 2}
        },
        {
            "user_id": "67890",
            "feedback_type": "feature_request",
            "description": "Please add support for multiple languages.",
            "metadata": {"rating": 5}
        }
    ]
    
    # Add test feedback
    for feedback in test_feedback:
        try:
            collector.collect_feedback(
                feedback['user_id'],
                feedback['feedback_type'],
                feedback['description'],
                feedback.get('metadata', {})
            )
        except ValueError as e:
            print(f"Error with test data: {e}")
    
    # Start CLI interface
    collector.cli_collect_feedback()
    
    # Display collected feedback
    print("\n=== All Collected Feedback ===")
    all_feedback = collector.get_feedback()
    for fb in all_feedback:
        print(f"\nID: {fb['feedback_id']}")
        print(f"Type: {fb['feedback_type']}")
        print(f"User: {fb['user_id']}")
        print(f"Description: {fb['description'][:100]}...")