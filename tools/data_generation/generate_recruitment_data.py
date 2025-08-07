#!/usr/bin/env python3
"""
Recruitment data generation script.

Generates fictional HR recruitment-related data to replace real business data.
"""

import os
import pandas as pd
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Set random seed for reproducibility
random.seed(42)

class RecruitmentDataGenerator:
    """Recruitment data generator"""

    def __init__(self, base_dir: str = None):
        """Initialize data generator"""
        if base_dir is None:
            # Get project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.join(current_dir, "..", "..", "data")
        else:
            self.base_dir = base_dir

        self.demo_dir = os.path.join(self.base_dir, "demo_data_csv")
        self.vector_dir = os.path.join(self.base_dir, "vector_db_csv")

        # Ensure directories exist
        os.makedirs(self.demo_dir, exist_ok=True)
        os.makedirs(self.vector_dir, exist_ok=True)

        # Base data
        self.positions = [
            "Java Developer", "Python Developer", "Frontend Developer", "Android Developer",
            "iOS Developer", "QA Engineer", "DevOps Engineer", "Data Analyst", "Product Manager",
            "UI Designer", "Project Manager", "Software Architect", "Algorithm Engineer", "Operations Specialist", "HR Specialist"
        ]

        self.departments = [
            "Engineering", "Product Design", "Quality Assurance", "DevOps", "Data Science",
            "Human Resources", "Marketing", "Operations", "Finance", "Administration"
        ]

        self.companies = [
            "TechCorp", "InnovateLab", "DataFlow Inc", "CloudTech", "MobileSoft",
            "SmartSystems", "NextGen Tech", "DigitalWorks", "FutureTech", "CodeCraft"
        ]

        self.cities = [
            "New York", "San Francisco", "Seattle", "Austin", "Boston", "Chicago", "Denver", "Atlanta", "Portland", "San Diego"
        ]
        
        self.job_levels = ["Junior", "Mid-Level", "Senior", "Staff", "Principal", "Manager", "Senior Manager", "Director"]

        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Christopher",
            "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua"
        ]

        self.last_names_male = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]

        self.last_names_female = [
            "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
            "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"
        ]

    def generate_name(self, gender: str = None) -> str:
        """Generate random name"""
        first_name = random.choice(self.first_names)
        if gender == "Male":
            last_name = random.choice(self.last_names_male)
        elif gender == "Female":
            last_name = random.choice(self.last_names_female)
        else:
            last_name = random.choice(self.last_names_male + self.last_names_female)
        return f"{first_name} {last_name}"

    def generate_employee_id(self, prefix: str = "EMP") -> str:
        """Generate employee ID"""
        return f"{prefix}{random.randint(100000, 999999)}"

    def generate_email(self, name: str, company: str = "company") -> str:
        """Generate email address"""
        return f"{name.lower()}.{random.randint(100, 999)}@{company.lower()}.com"

    def generate_date_range(self, start_date: str, days_range: int = 30) -> tuple:
        """Generate date range"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=random.randint(1, days_range))
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    def generate_recruitment_activities(self, count: int = 50) -> List[Dict]:
        """Generate recruitment activity data"""
        activities = []
        
        activity_names = [
            "Spring Campus Recruitment", "Summer Internship Program", "Fall General Recruitment", "Annual Core Talent Hunt",
            "Technical Specialist Hiring", "Product Team Recruitment", "Management Trainee Program", "Executive Search Campaign",
            "New Graduate Recruitment", "Senior Engineer Hiring", "Global Talent Acquisition", "Employee Referral Drive"
        ]
        
        for i in range(count):
            start_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))
            end_date = start_date + timedelta(days=random.randint(7, 60))
            
            activity = {
                "id": i + 1,
                "activity_number": f"REC{2024}{str(i+1).zfill(3)}",
                "activity_name": random.choice(activity_names),
                "position_type": random.choice(self.positions),
                "department": random.choice(self.departments),
                "recruitment_start_date": start_date.strftime("%Y-%m-%d"),
                "recruitment_end_date": end_date.strftime("%Y-%m-%d"),
                "recruitment_city": random.choice(self.cities),
                "target_headcount": random.randint(5, 50),
                "received_resumes": random.randint(20, 200),
                "screened_resumes": random.randint(10, 100),
                "interview_candidates": random.randint(5, 50),
                "offer_count": random.randint(1, 20),
                "onboard_count": random.randint(1, 15),
                "success_rate": round(random.uniform(0.1, 0.8), 2),
                "avg_interview_score": round(random.uniform(3.0, 4.5), 1),
                "hr_satisfaction": round(random.uniform(3.5, 5.0), 1),
                "hiring_manager_satisfaction": round(random.uniform(3.0, 5.0), 1),
                "job_level_requirement": random.choice(self.job_levels),
                "min_experience_years": random.randint(0, 8),
                "max_experience_years": random.randint(3, 15)
            }
            activities.append(activity)
        
        return activities

    def generate_interviewers(self, count: int = 100) -> List[Dict]:
        """Generate interviewer data"""
        interviewers = []

        interview_types = ["Technical Interview", "Behavioral Interview", "HR Interview", "Final Interview"]

        for i in range(count):
            gender = random.choice(["Male", "Female"])
            name = self.generate_name(gender)
            
            interviewer = {
                "id": i + 1,
                "role_type": "Interviewer",
                "emp_id": self.generate_employee_id("INT"),
                "interview_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d"),
                "is_fulltime_interviewer": random.choice(["Yes", "No"]),
                "interview_type": random.choice(interview_types),
                "activity_name": f"Recruitment Activity {random.randint(1, 50)}",
                "interview_score": round(random.uniform(3.0, 5.0), 1),
                "interview_duration": random.choice(["30 minutes", "45 minutes", "60 minutes", "90 minutes"]),
                "expertise_area": random.choice(self.positions),
                "hr_manager": self.generate_name(),
                "interview_round": random.randint(1, 4),
                "is_weekend": random.choice(["Yes", "No"]),
                "interviewer_level": random.choice(self.job_levels),
                "name": name,
                "sex": gender,
                "organization_name": random.choice(self.companies),
                "job_level_desc": random.choice(self.job_levels),
                "dept_descr0": random.choice(self.departments),
                "dept_descr1": random.choice(self.departments),
                "dept_descr2": random.choice(self.departments),
                "dept_descr3": random.choice(self.departments),
                "hr_status": random.choice(["Active", "Inactive"])
            }
            interviewers.append(interviewer)
        
        return interviewers

    def generate_candidates(self, count: int = 500) -> List[Dict]:
        """Generate candidate data"""
        candidates = []

        education_levels = ["Bachelor", "Master", "PhD", "Associate"]
        interview_results = ["Pass", "Fail", "Pending"]

        for i in range(count):
            gender = random.choice(["Male", "Female"])
            name = self.generate_name(gender)

            candidate = {
                "id": i + 1,
                "activity_name": f"Recruitment Activity {random.randint(1, 50)}",
                "position_applied": random.choice(self.positions),
                "recruitment_start_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d"),
                "candidate_name": name,
                "candidate_id": self.generate_employee_id("CAN"),
                "sex": gender,
                "remark": random.choice(["Excellent", "Good", "Average", "Needs Improvement", ""]),
                "work_email": self.generate_email(name),
                "applied_job_level": random.choice(self.job_levels),
                "current_company": random.choice(self.companies),
                "dept_descr0": random.choice(self.departments),
                "dept_descr1": random.choice(self.departments),
                "dept_descr2": random.choice(self.departments),
                "dept_descr3": random.choice(self.departments),
                "education_level": random.choice(education_levels),
                "major": random.choice(["Computer Science", "Software Engineering", "Information Systems", "Electrical Engineering", "Business Administration"]),
                "graduation_school": random.choice(["MIT", "Stanford University", "UC Berkeley", "Carnegie Mellon", "Harvard University"]),
                "work_city": random.choice(self.cities),
                "work_experience_years": random.randint(0, 15),
                "current_salary": random.randint(80000, 200000),
                "expected_salary": random.randint(90000, 250000),
                "target_organization_name": random.choice(self.companies),
                "current_job_level_desc": random.choice(self.job_levels),
                "current_dept_name": random.choice(self.departments),
                "current_dept_descr0": random.choice(self.departments),
                "current_dept_descr1": random.choice(self.departments),
                "current_dept_descr2": random.choice(self.departments),
                "current_dept_descr3": random.choice(self.departments),
                "current_position": random.choice(self.positions),
                "skill_keywords": random.choice(["Java,Spring,MySQL", "Python,Django,Redis", "React,Vue,JavaScript"]),
                "interview_result": random.choice(interview_results),
                "offer_status": random.choice(["Offer Extended", "No Offer", "Offer Declined", "Offer Accepted"]),
                "onboard_status": random.choice(["Onboarded", "Not Onboarded", "Declined Onboarding"]),
                "referrer_name": random.choice([self.generate_name(), ""]),
                "hr_status": random.choice(["Candidate", "Hired", "Rejected"])
            }
            candidates.append(candidate)
        
        return candidates

    def generate_table_descriptions(self) -> List[Dict]:
        """Generate table description data"""
        descriptions = [
            {
                "table_name": "recruitment_interviewer_info",
                "description": "Recruitment interviewer table",
                "additional_info": "Stores all interviewers and their interview-related data. The role_type field is used to distinguish interviewer types and can be ignored by default. Table structure characteristics: (1) One interviewer (emp_id) may correspond to multiple records, each representing an interview the interviewer participated in; (2) One recruitment activity (activity_name) may correspond to multiple records, representing multiple interviewers participating in that activity; (3) Can establish relationships with other tables through emp_id and activity_name fields; (4) Use activity_name to distinguish specific recruitment activities.",
                "schema": """| Field Name | Type | Description |
|------------|------|-------------|
| id | BIGINT |   |
| role_type | VARCHAR(50) |   |
| emp_id | VARCHAR(50) |   |
| interview_date | VARCHAR(50) |   |
| is_fulltime_interviewer | VARCHAR(50) |   |
| interview_type | VARCHAR(50) |   |
| activity_name | VARCHAR(50) |   |
| interview_score | VARCHAR(50) |   |
| interview_duration | VARCHAR(50) |   |
| expertise_area | VARCHAR(50) |   |
| hr_manager | VARCHAR(50) |   |
| interview_round | VARCHAR(50) |   |
| is_weekend | VARCHAR(50) |   |
| interviewer_level | VARCHAR(50) |   |
| name | VARCHAR(50) |   |
| sex | VARCHAR(50) |   |
| organization_name | VARCHAR(50) |   |
| job_level_desc | VARCHAR(50) |   |
| dept_descr0 | VARCHAR(50) |   |
| dept_descr1 | VARCHAR(50) |   |
| dept_descr2 | VARCHAR(50) |   |
| dept_descr3 | VARCHAR(50) |   |
| hr_status | VARCHAR(50) |   |"""
            },
            {
                "table_name": "recruitment_activity_info",
                "description": "Recruitment activity list",
                "additional_info": "Used for querying recruitment activity progress, applicant numbers, and success rate statistics. Table structure characteristics: (1) One row per activity, each row represents an independent recruitment activity instance; (2) Activities with the same name (activity_name) may be held at different times, distinguished by recruitment_start_date; (3) Contains activity statistics such as applicant numbers, onboarding numbers, suitable for recruitment effectiveness analysis.",
                "schema": """| Field Name | Type | Description |
|------------|------|-------------|
| id | BIGINT |   |
| activity_number | VARCHAR(50) | Activity number |
| activity_name | VARCHAR(50) | Activity name |
| position_type | VARCHAR(50) | Position type |
| department | VARCHAR(50) | Department |
| recruitment_start_date | VARCHAR(50) | Recruitment start date |
| recruitment_end_date | VARCHAR(50) | Recruitment end date |
| recruitment_city | VARCHAR(50) | Recruitment city |
| target_headcount | VARCHAR(50) | Target headcount |
| received_resumes | VARCHAR(50) | Received resumes |
| screened_resumes | VARCHAR(50) | Screened resumes |
| interview_candidates | VARCHAR(50) | Interview candidates |
| offer_count | VARCHAR(50) | Offer count |
| onboard_count | VARCHAR(50) | Actual onboard count |
| success_rate | VARCHAR(50) | Recruitment success rate |
| avg_interview_score | VARCHAR(50) | Average interview score |
| hr_satisfaction | VARCHAR(50) | HR satisfaction |
| hiring_manager_satisfaction | VARCHAR(50) | Hiring manager satisfaction |
| job_level_requirement | VARCHAR(50) | Job level requirement |
| min_experience_years | VARCHAR(50) | Minimum experience years |
| max_experience_years | VARCHAR(50) | Maximum experience years |"""
            },
            {
                "table_name": "recruitment_candidate_info",
                "description": "Candidate information table",
                "additional_info": "Records all candidate information participating in recruitment, including applied activities and related information. Table structure characteristics: (1) One candidate (candidate_id) may correspond to multiple records, each row represents a recruitment activity the candidate participated in; (2) One recruitment activity (activity_name) may correspond to multiple records, representing multiple candidates participating in that activity",
                "schema": """| Field Name | Type | Description |
|------------|------|-------------|
| id | BIGINT |   |
| activity_name | VARCHAR(50) |   |
| position_applied | VARCHAR(50) |   |
| recruitment_start_date | VARCHAR(50) |   |
| candidate_name | VARCHAR(50) |   |
| candidate_id | VARCHAR(50) |   |
| sex | VARCHAR(50) |   |
| remark | VARCHAR(50) |   |
| work_email | VARCHAR(50) |   |
| applied_job_level | VARCHAR(50) |   |
| current_company | VARCHAR(50) |   |
| dept_descr0 | VARCHAR(50) |   |
| dept_descr1 | VARCHAR(50) |   |
| dept_descr2 | VARCHAR(50) |   |
| dept_descr3 | VARCHAR(50) |   |
| education_level | VARCHAR(50) |   |
| major | VARCHAR(50) |   |
| graduation_school | VARCHAR(50) |   |
| work_city | VARCHAR(50) |   |
| work_experience_years | VARCHAR(50) |   |
| current_salary | VARCHAR(50) |   |
| expected_salary | VARCHAR(50) |   |
| target_organization_name | VARCHAR(50) |   |
| current_job_level_desc | VARCHAR(50) |   |
| current_dept_name | VARCHAR(50) |   |
| current_dept_descr0 | VARCHAR(50) |   |
| current_dept_descr1 | VARCHAR(50) |   |
| current_dept_descr2 | VARCHAR(50) |   |
| current_dept_descr3 | VARCHAR(50) |   |
| current_position | VARCHAR(50) |   |
| skill_keywords | VARCHAR(50) |   |
| interview_result | VARCHAR(50) |   |
| offer_status | VARCHAR(50) |   |
| onboard_status | VARCHAR(50) |   |
| referrer_name | VARCHAR(50) |   |
| hr_status | VARCHAR(50) |   |"""
            }
        ]
        return descriptions

    def generate_query_examples(self) -> List[Dict]:
        """Generate query example data"""
        examples = [
            {
                "query_text": "List of candidates from the most recent Spring Campus Recruitment",
                "query_sql": "SELECT rc.candidate_name, rc.candidate_id, rc.activity_name, rc.target_organization_name, rc.recruitment_start_date FROM recruitment_candidate_info rc WHERE rc.activity_name = 'Spring Campus Recruitment' AND rc.recruitment_start_date = ( SELECT MAX(recruitment_start_date) FROM recruitment_candidate_info WHERE activity_name = 'Spring Campus Recruitment' AND recruitment_start_date < '2024-11-22' );"
            },
            {
                "query_text": "Query all recruitment activities where James Smith served as interviewer",
                "query_sql": "SELECT DISTINCT activity_name, recruitment_start_date FROM recruitment_interviewer_info WHERE name = 'James Smith';"
            },
            {
                "query_text": "Query all recruitment activities that John Johnson participated in",
                "query_sql": "SELECT DISTINCT activity_name, position_applied, recruitment_start_date, target_organization_name FROM recruitment_candidate_info WHERE candidate_name = 'John Johnson' ORDER BY STR_TO_DATE(recruitment_start_date, '%Y-%m-%d') DESC;"
            },
            {
                "query_text": "Calculate recruitment success rate for Engineering department",
                "query_sql": "SELECT AVG(success_rate) as avg_success_rate, COUNT(*) as total_activities FROM recruitment_activity_info WHERE department = 'Engineering';"
            },
            {
                "query_text": "Query all candidates for Java Developer position",
                "query_sql": "SELECT candidate_name, education_level, work_experience_years, current_salary, interview_result FROM recruitment_candidate_info WHERE position_applied = 'Java Developer';"
            }
        ]
        return examples

    def generate_term_descriptions(self) -> List[Dict]:
        """Generate term description data"""
        terms = [
            {
                "original_term": "Jim",
                "standard_name": "James Smith",
                "additional_info": "Nickname for employee `James Smith`"
            },
            {
                "original_term": "Spring Hiring",
                "standard_name": "Spring Campus Recruitment",
                "additional_info": "Abbreviation for company's spring campus recruitment activity"
            },
            {
                "original_term": "Fall Hiring",
                "standard_name": "Fall General Recruitment",
                "additional_info": "Abbreviation for company's fall general recruitment activity"
            },
            {
                "original_term": "Big Tech",
                "standard_name": "TechCorp InnovateLab DataFlow",
                "additional_info": "Refers to the abbreviation for TechCorp, InnovateLab, and DataFlow companies"
            },
            {
                "original_term": "Johnny",
                "standard_name": "John Johnson",
                "additional_info": "Nickname for employee `John Johnson`"
            },
            {
                "original_term": "Senior+",
                "standard_name": "",
                "additional_info": "Refers to Senior level and above, including Senior, Staff, Principal, Manager, Senior Manager, Director; or job level rank >=3 for querying"
            },
            {
                "original_term": "Mid-Level",
                "standard_name": "",
                "additional_info": "Refers to Mid-Level position, can query by job level = 'Mid-Level' or job level rank = 2"
            },
            {
                "original_term": "Tech Dept",
                "standard_name": "Engineering",
                "additional_info": "Generally refers to department with name 'Engineering'"
            }
        ]
        return terms

    def save_to_csv(self, data: List[Dict], filename: str, directory: str):
        """Save data to CSV file"""
        filepath = os.path.join(directory, filename)
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"✅ Generated file: {filepath} ({len(data)} records)")

    def generate_all_data(self, 
                         activities_count: int = 50,
                         interviewers_count: int = 100, 
                         candidates_count: int = 500):
        """Generate all data files"""
        print("🔄 Starting to generate recruitment-related data...")

        # Generate main data tables
        activities = self.generate_recruitment_activities(activities_count)
        interviewers = self.generate_interviewers(interviewers_count)
        candidates = self.generate_candidates(candidates_count)

        # Save to demo_data_csv directory
        self.save_to_csv(activities, "recruitment_activity_info.csv", self.demo_dir)
        self.save_to_csv(interviewers, "recruitment_interviewer_info.csv", self.demo_dir)
        self.save_to_csv(candidates, "recruitment_candidate_info.csv", self.demo_dir)

        # Generate vector database related files
        table_descriptions = self.generate_table_descriptions()
        query_examples = self.generate_query_examples()
        term_descriptions = self.generate_term_descriptions()

        # Save to vector_db_csv directory
        self.save_to_csv(table_descriptions, "table_descriptions.csv", self.vector_dir)
        self.save_to_csv(query_examples, "query_examples.csv", self.vector_dir)
        self.save_to_csv(term_descriptions, "term_descriptions.csv", self.vector_dir)

        print("✅ All recruitment data generation completed!")
        return {
            "activities": len(activities),
            "interviewers": len(interviewers), 
            "candidates": len(candidates),
            "metadata_files": 3
        }


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate recruitment demo data")
    parser.add_argument("--activities", type=int, default=50, help="Number of recruitment activities")
    parser.add_argument("--interviewers", type=int, default=100, help="Number of interviewers")
    parser.add_argument("--candidates", type=int, default=500, help="Number of candidates")
    parser.add_argument("--output-dir", type=str, help="Output directory")

    args = parser.parse_args()

    generator = RecruitmentDataGenerator(args.output_dir)
    result = generator.generate_all_data(
        args.activities,
        args.interviewers,
        args.candidates
    )

    print(f"\n📊 Generation Statistics:")
    print(f"   - Recruitment activities: {result['activities']} records")
    print(f"   - Interviewers: {result['interviewers']} records")
    print(f"   - Candidates: {result['candidates']} records")
    print(f"   - Metadata files: {result['metadata_files']} files")


if __name__ == "__main__":
    main() 