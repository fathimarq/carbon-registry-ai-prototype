"""
Testing framework for AI agent responses
"""
import random
from difflib import SequenceMatcher
import pandas as pd

class AgentTester:
    def __init__(self, database, knowledge_base):
        self.db = database
        self.knowledge_base = knowledge_base
    
    def simulate_agent_response(self, inquiry):
        """Simulate what an AI agent might respond"""
        category = inquiry["category"]
        
        # Simple response templates based on category
        if category == "project_registration":
            steps = self.knowledge_base['registration_steps'][:3]
            return f"To register a project, you'll need to: {', '.join(steps)}. For complete details, check our Program Guide."
        
        elif category == "methodology":
            return f"The right methodology depends on your project type. For {inquiry.get('project_type_mentioned', 'your project')}, we recommend reviewing our methodology library at docs.regen.network/methodologies"
        
        elif category == "mrv":
            proj_type = inquiry.get('project_type_mentioned', 'your project')
            if proj_type in self.knowledge_base['mrv_requirements']:
                reqs = self.knowledge_base['mrv_requirements'][proj_type]
            else:
                reqs = "regular monitoring with appropriate sampling and reporting"
            return f"MRV requirements for {proj_type} include: {reqs}. Contact our MRV team for detailed guidance."
        
        elif category == "credit_issuance":
            return f"Credits are typically issued annually after verification. Current prices range from $5-20 per credit. See our credit issuance guide for detailed calculations."
        
        else:  # technical_support
            return "Please check our technical documentation at docs.regen.network. If the issue persists, contact support@regen.network with screenshots."
    
    def calculate_response_quality(self, simulated_response, inquiry):
        """Score how good the response is based on keyword coverage"""
        
        # Keywords that should be in response based on category
        category_keywords = {
            "project_registration": ["register", "step", "process", "document", "submit"],
            "methodology": ["methodology", "project type", "library", "applicable"],
            "mrv": ["monitor", "report", "verify", "sample", "requirement"],
            "credit_issuance": ["credit", "issue", "price", "sell", "calculation"],
            "technical_support": ["documentation", "support", "error", "help", "contact"]
        }
        
        # Get keywords for this category
        keywords = category_keywords.get(inquiry["category"], ["help", "guidance"])
        
        # Count how many keywords appear in response
        response_lower = simulated_response.lower()
        matched = sum(1 for k in keywords if k in response_lower)
        
        # Calculate score (0-1)
        score = matched / len(keywords) if keywords else 0.5
        
        # Bonus if response is helpful length
        if 50 < len(simulated_response) < 300:
            score += 0.1
        
        return min(round(score, 2), 1.0)  # Cap at 1.0
    
    def run_test_suite(self, test_inquiries):
        """Run tests on a set of inquiries"""
        results = []
        
        for inquiry in test_inquiries:
            # Simulate agent response
            simulated = self.simulate_agent_response(inquiry)
            
            # Calculate quality score
            quality_score = self.calculate_response_quality(simulated, inquiry)
            
            # Determine if passed
            passed = quality_score >= 0.4
            
            # Identify issues
            issues = []
            if quality_score < 0.3:
                issues.append("Response too generic - missing specific guidance")
            if quality_score < 0.2:
                issues.append("No actionable information provided")
            if len(simulated) < 40:
                issues.append("Response too short")
            if "contact" in simulated.lower() and quality_score < 0.5:
                issues.append("Over-reliance on directing to human support")
            
            results.append({
                "inquiry_id": inquiry["inquiry_id"],
                "category": inquiry["category"],
                "inquiry_preview": inquiry["inquiry_text"][:50] + "...",
                "simulated_response": simulated[:100] + "..." if len(simulated) > 100 else simulated,
                "quality_score": quality_score,
                "passed": passed,
                "issues_found": issues if issues else ["None"]
            })
        
        return results
    
    def identify_failure_patterns(self, test_results):
        """Find patterns in test failures"""
        failures = [r for r in test_results if not r["passed"]]
        
        if not failures:
            return [{"message": "No failures detected - agent performing well"}]
        
        # Group by category
        failure_by_category = {}
        for f in failures:
            cat = f["category"]
            if cat not in failure_by_category:
                failure_by_category[cat] = []
            failure_by_category[cat].append(f)
        
        patterns = []
        for category, fails in failure_by_category.items():
            # Collect all issues
            all_issues = []
            for fail in fails:
                all_issues.extend(fail["issues_found"])
            
            # Find most common issues
            from collections import Counter
            common = Counter(all_issues).most_common(2)
            
            patterns.append({
                "category": category,
                "failure_count": len(fails),
                "common_issues": [issue for issue, count in common],
                "recommendation": f"Improve {category} training data. Add more specific responses about {', '.join([issue[:20] for issue, _ in common])}"
            })
        
        return patterns
    
    def generate_test_report(self, test_results):
        """Create summary report of agent performance"""
        total = len(test_results)
        passed = len([r for r in test_results if r["passed"]])
        
        # Average quality score
        avg_quality = sum(r["quality_score"] for r in test_results) / total if total > 0 else 0
        
        # Results by category
        by_category = {}
        df = pd.DataFrame(test_results)
        if not df.empty and 'category' in df.columns:
            for category in df['category'].unique():
                cat_df = df[df['category'] == category]
                cat_passed = len(cat_df[cat_df['passed']])
                cat_total = len(cat_df)
                by_category[category] = {
                    "count": cat_total,
                    "pass_rate": round((cat_passed / cat_total * 100), 1) if cat_total > 0 else 0,
                    "avg_quality": round(cat_df['quality_score'].mean(), 2)
                }
        
        return {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": round((passed/total)*100, 1) if total > 0 else 0,
                "avg_quality_score": round(avg_quality, 2)
            },
            "by_category": by_category,
            "failure_patterns": self.identify_failure_patterns(test_results)
        }