"""
Mock database simulating developer inquiries to a carbon registry
All data is simulated
"""
import random
from datetime import datetime, timedelta

class CarbonRegistryDB:
    def __init__(self):
        self.inquiries = self._generate_sample_inquiries()
        self.knowledge_base = self._create_knowledge_base()
    
    def _generate_sample_inquiries(self):
        """Generate 50 realistic developer inquiries"""
        
        # Templates for different types of questions
        templates = [
            # Registration questions
            "How do I register a {project_type} project in {country}?",
            "What are the steps for {project_type} registration?",
            "Can I register a {project_type} project as an individual?",
            "What documents are needed for {project_type} registration?",
            "How long does {project_type} registration take?",
            
            # Methodology questions
            "Which methodology should I use for {project_type}?",
            "How do I apply the {methodology} methodology?",
            "What's the difference between {methodology} and {methodology_alt}?",
            "Is {methodology} approved for {project_type}?",
            "Can you explain the {methodology} methodology?",
            
            # MRV questions
            "What are the MRV requirements for {project_type}?",
            "How often do I need to monitor {project_type}?",
            "What remote sensing tools work for {project_type}?",
            "How much does MRV cost for {project_type}?",
            "Who can verify my {project_type} project?",
            
            # Credit questions
            "When do credits get issued for {project_type}?",
            "How are credits calculated for {project_type}?",
            "What's the minimum credit issuance?",
            "How do I sell my carbon credits?",
            "What is the current credit price?",
            
            # Technical questions
            "I can't log in to the platform",
            "How do I upload my {document_type}?",
            "The system says error when submitting",
            "Is there an API for data upload?",
            "Can I integrate with {software}?"
        ]
        
        # Possible values to fill templates
        project_types = ["soil carbon", "forestry", "agroforestry", "grasslands", "wetlands", "blue carbon", "improved forest management"]
        countries = ["Kenya", "Ethiopia", "Rwanda", "Uganda", "Tanzania", "Zambia", "Malawi", "Mozambique", "Ghana", "Senegal"]
        methodologies = ["VM0017", "VM0021", "VM0032", "VM0042", "VM0047", "AR-ACM0003", "VM0012"]
        document_types = ["PDD", "monitoring report", "validation report", "verification report", "baseline study", "map"]
        software = ["Excel", "GIS software", "Google Sheets", "custom API", "Salesforce"]
        
        user_types = ["new_developer", "experienced_developer", "project_developer", "validator", "buyer", "consultant"]
        categories = ["project_registration", "methodology", "mrv", "credit_issuance", "technical_support"]
        intents = ["process_guidance", "documentation", "eligibility", "methodology_selection", 
                   "technical_requirements", "cost_estimation", "verification", "timeline", 
                   "calculation", "market_access", "troubleshooting", "api_help"]
        
        inquiries = []
        start_date = datetime(2024, 1, 1)
        
        for i in range(1, 51):
            template = random.choice(templates)
            
            # Fill in the template
            text = template.format(
                project_type=random.choice(project_types),
                country=random.choice(countries),
                methodology=random.choice(methodologies),
                methodology_alt=random.choice(methodologies),
                document_type=random.choice(document_types),
                software=random.choice(software)
            )
            
            # Random date within last 3 months
            days_ago = random.randint(0, 90)
            inquiry_date = start_date + timedelta(days=days_ago)
            
            # Random status with realistic probabilities
            if days_ago < 7:  # Recent inquiries more likely to be pending
                status = random.choices(["resolved", "pending", "escalated"], weights=[0.5, 0.4, 0.1])[0]
            else:
                status = random.choices(["resolved", "pending", "escalated"], weights=[0.85, 0.1, 0.05])[0]
            
            # Response time based on complexity
            complexity = random.choice(["low", "medium", "high"])
            if complexity == "low":
                response_time = round(random.uniform(1, 24), 1)
            elif complexity == "medium":
                response_time = round(random.uniform(12, 48), 1)
            else:
                response_time = round(random.uniform(24, 120), 1)
            
            inquiries.append({
                "inquiry_id": f"INQ{i:03d}",
                "date": inquiry_date.strftime("%Y-%m-%d"),
                "timestamp": inquiry_date.isoformat(),
                "user_type": random.choice(user_types),
                "inquiry_text": text,
                "category": random.choice(categories),
                "intent": random.choice(intents),
                "status": status,
                "response_time_hours": response_time,
                "complexity": complexity,
                "satisfaction_score": random.choice([3, 4, 5]) if status == "resolved" else None,
                "escalated_to_human": status == "escalated",
                "country_mentioned": random.choice(countries) if random.random() > 0.4 else None,
                "project_type_mentioned": random.choice(project_types) if random.random() > 0.3 else None,
            })
        
        # Sort by date
        return sorted(inquiries, key=lambda x: x["date"])
    
    def _create_knowledge_base(self):
        """Create structured knowledge base for responses"""
        return {
            "methodologies": {
                "VM0017": "Soil carbon quantification methodology for agricultural lands",
                "VM0021": "Afforestation/reforestation methodology for degraded lands",
                "VM0032": "Improved forest management methodology for carbon enhancement",
                "VM0042": "Agroforestry methodology for smallholder farmers",
                "VM0047": "Blue carbon methodology for coastal ecosystems"
            },
            "registration_steps": [
                "1. Join Builder Lab (orientation program for new developers)",
                "2. Submit concept note for methodology fit check",
                "3. Develop Project Design Document (PDD) with all required sections",
                "4. Third-party validation by approved validator",
                "5. Submit registration fee payment",
                "6. Official listing on the registry"
            ],
            "mrv_requirements": {
                "soil_carbon": "Soil sampling every 3-5 years, annual biomass assessment, remote sensing verification",
                "forestry": "Remote sensing annually, ground plots every 3-5 years, biodiversity monitoring",
                "agroforestry": "Tree counts, biomass equations, survival rates, annual sampling",
                "wetlands": "Hydrological monitoring, vegetation surveys, water quality sampling"
            },
            "faqs": {
                "What does it cost?": "Registration fee: $5,000 one-time. Annual verification: $3,000-8,000 depending on project size. Issuance fee: $0.10-0.30 per credit.",
                "How long does it take?": "Typically 6-18 months from concept to first credit issuance, depending on project complexity and developer experience.",
                "Minimum project size?": "There is no official minimum size, but smaller projects may have higher relative costs. We recommend at least 100 hectares for economic viability.",
                "Credit prices?": "Current market prices range from $5-20 per credit depending on methodology, co-benefits, and vintage."
            }
        }
    
    def get_all_inquiries(self):
        return self.inquiries
    
    def get_inquiries_by_category(self, category):
        return [i for i in self.inquiries if i["category"] == category]
    
    def get_unresolved_inquiries(self):
        return [i for i in self.inquiries if i["status"] != "resolved"]

# Create a single instance to use throughout the app
db = CarbonRegistryDB()