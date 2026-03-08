"""
Analyzes developer inquiry patterns for AI training
"""
import pandas as pd
from collections import Counter

class InquiryAnalyzer:
    def __init__(self, database):
        self.db = database
        self.inquiries = database.get_all_inquiries()
        self.df = pd.DataFrame(self.inquiries)
    
    def get_summary_stats(self):
        """Generate summary statistics from inquiries"""
        
        # Calculate resolution rate
        resolved_count = len(self.df[self.df['status'] == 'resolved'])
        total_count = len(self.df)
        resolution_rate = (resolved_count / total_count * 100) if total_count > 0 else 0
        
        # Calculate escalation rate
        escalated_count = len(self.df[self.df['escalated_to_human'] == True])
        escalation_rate = (escalated_count / total_count * 100) if total_count > 0 else 0
        
        # Get top categories
        category_counts = self.df['category'].value_counts().head(5).to_dict()
        
        # Get top intents
        intent_counts = self.df['intent'].value_counts().head(5).to_dict()
        
        # Average response time
        resolved_df = self.df[self.df['status'] == 'resolved']
        avg_response = resolved_df['response_time_hours'].mean() if not resolved_df.empty else 0
        
        return {
            "total_inquiries": total_count,
            "unique_categories": self.df['category'].nunique(),
            "unique_intents": self.df['intent'].nunique(),
            "resolution_rate": round(resolution_rate, 1),
            "avg_response_time": round(avg_response, 1),
            "escalation_rate": round(escalation_rate, 1),
            "top_categories": category_counts,
            "top_intents": intent_counts
        }
    
    def get_trends_over_time(self):
        """Analyze inquiry trends by week"""
        if self.df.empty:
            return {"weekly_counts": {}, "category_trends": {}}
        
        # Convert date to datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Group by week
        self.df['week'] = self.df['date'].dt.isocalendar().week
        weekly_counts = self.df.groupby('week').size().to_dict()
        
        # Category by week
        category_week = self.df.groupby(['week', 'category']).size().unstack(fill_value=0)
        category_trends = category_week.to_dict()
        
        return {
            "weekly_counts": weekly_counts,
            "category_trends": category_trends
        }
    
    def extract_training_pairs(self):
        """Create labeled training data for AI agent"""
        training_data = []
        
        for inquiry in self.inquiries:
            # Determine quality based on resolution and satisfaction
            if inquiry["status"] == "resolved" and inquiry.get("satisfaction_score", 0) and inquiry["satisfaction_score"] >= 4:
                quality = "high"
            elif inquiry["status"] == "resolved":
                quality = "medium"
            else:
                quality = "low"  # Unresolved - not good for training
            
            # Extract keywords (simple version)
            keywords = []
            common_terms = ["register", "methodology", "mrv", "credit", "verify", 
                           "cost", "time", "document", "soil", "forest", "carbon"]
            for term in common_terms:
                if term in inquiry["inquiry_text"].lower():
                    keywords.append(term)
            
            training_data.append({
                "inquiry_id": inquiry["inquiry_id"],
                "prompt": inquiry["inquiry_text"],
                "category": inquiry["category"],
                "intent": inquiry["intent"],
                "user_type": inquiry["user_type"],
                "complexity": inquiry["complexity"],
                "quality_flag": quality,
                "keywords": ", ".join(keywords) if keywords else "general",
                "country_context": inquiry["country_mentioned"] or "unspecified",
                "project_type": inquiry["project_type_mentioned"] or "unspecified",
                "training_priority": "high" if quality == "high" else "medium"
            })
        
        return training_data
    
    def identify_knowledge_gaps(self):
        """Find patterns that indicate missing documentation"""
        gaps = []
        
        # Find inquiries that were escalated or are pending
        problematic = self.df[
            (self.df['escalated_to_human'] == True) | 
            (self.df['status'] == 'pending')
        ]
        
        if not problematic.empty:
            # Group by category to see where most issues happen
            escalation_hotspots = problematic.groupby('category').size().sort_values(ascending=False)
            
            for category, count in escalation_hotspots.head(3).items():
                # Get sample questions
                sample_rows = problematic[problematic['category'] == category].head(3)
                sample_questions = sample_rows['inquiry_text'].tolist() if not sample_rows.empty else []
                
                gaps.append({
                    "category": category,
                    "escalation_count": int(count),
                    "gap_severity": "high" if count > 5 else "medium",
                    "sample_questions": sample_questions,
                    "recommendation": f"Create or update documentation for {category} based on these common questions",
                    "priority": 1 if count > 5 else 2
                })
        
        return gaps
    
    def generate_intent_classifier_data(self):
        """Create dataset for training intent classification"""
        intents = []
        for inquiry in self.inquiries:
            intents.append({
                "text": inquiry["inquiry_text"],
                "category": inquiry["category"],
                "intent": inquiry["intent"]
            })
        return intents