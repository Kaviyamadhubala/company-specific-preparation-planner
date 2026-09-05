"""
Comprehensive database seeder for Company-Specific Preparation Planner.
Populates realistic placement prep data for immediate demonstration.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.models import (
    User, Student, Skill, StudentSkill, Company, Role, CompanyRole,
    CompanySkill, RecruitmentRound, RoundSkill, Question, QuestionOption,
    Project, Resource, ReadinessWeight, Roadmap, RoadmapWeek, RoadmapTask,
    UserRole, Difficulty, QuestionCategory, TestType, ResourceType,
    RoadmapStatus, TaskStatus
)
from app.auth.jwt import get_password_hash

def seed():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Readiness Weights
        print("Seeding Readiness Weights...")
        weights_data = [
            ("technical", 35.0, "Technical Programming Skills"),
            ("dsa", 20.0, "Data Structures & Algorithms"),
            ("aptitude", 15.0, "Aptitude & Reasoning"),
            ("cs_fundamentals", 10.0, "CS Core Subjects (DBMS, OS, Networks)"),
            ("communication", 10.0, "Communication & Soft Skills"),
            ("interview", 10.0, "Interview Preparation"),
        ]
        for cat, pct, desc in weights_data:
            existing = db.query(ReadinessWeight).filter(ReadinessWeight.category == cat).first()
            if not existing:
                db.add(ReadinessWeight(category=cat, weight_pct=pct, description=desc))
        db.commit()

        # 2. Users
        print("Seeding Users...")
        admin_user = db.query(User).filter(User.email == "admin@prepplanner.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@prepplanner.com",
                password_hash=get_password_hash("Admin@123"),
                role=UserRole.admin,
                is_active=True
            )
            db.add(admin_user)

        student_user = db.query(User).filter(User.email == "student@example.com").first()
        if not student_user:
            student_user = User(
                email="student@example.com",
                password_hash=get_password_hash("Student@123"),
                role=UserRole.student,
                is_active=True
            )
            db.add(student_user)
        db.commit()

        # 3. Student Profile
        print("Seeding Student Profile...")
        student = db.query(Student).filter(Student.user_id == student_user.id).first()
        if not student:
            student = Student(
                user_id=student_user.id,
                full_name="Alex Johnson",
                college="MIT College of Engineering",
                degree="B.Tech",
                branch="Computer Science & Engineering",
                graduation_year=2025,
                cgpa=8.4,
                phone="9876543210",
                location="Bangalore, India",
                daily_hours=2.5,
                preferred_role="Software Developer",
                preferred_location="Bangalore",
                bio="Passionate computer science student aiming for premier IT and product company placements. Focused on Java, DSA, and Web Development.",
                profile_completed=True
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        # 4. Skills
        print("Seeding Skills...")
        skills_def = [
            (1, "Java", "technical", "Core & Advanced Java, OOP, Collections, Multithreading"),
            (2, "Python", "technical", "Python 3, OOP, standard libraries, scripting"),
            (3, "JavaScript", "technical", "Modern ES6+, DOM manipulation, async programming"),
            (4, "SQL", "technical", "Relational queries, joins, aggregation, indexing"),
            (5, "React", "technical", "Frontend component architecture, hooks, state management"),
            (6, "Spring Boot", "technical", "Enterprise Java framework, REST APIs, Microservices"),
            (7, "DSA", "dsa", "Arrays, Linked Lists, Trees, Graphs, Sorting, Searching"),
            (8, "OOP", "technical", "Encapsulation, Inheritance, Polymorphism, Abstraction, SOLID"),
            (9, "DBMS", "cs_fundamentals", "Normalization, Transactions, ACID properties, Indexing"),
            (10, "Operating Systems", "cs_fundamentals", "Process scheduling, memory management, deadlocks, threads"),
            (11, "Computer Networks", "cs_fundamentals", "OSI model, TCP/IP, HTTP/HTTPS, DNS, routing"),
            (12, "Aptitude", "aptitude", "Quantitative ability, percentages, ratios, time and work"),
            (13, "Logical Reasoning", "aptitude", "Puzzles, series, syllogisms, blood relations"),
            (14, "Communication", "communication", "Verbal, written, self-introduction, HR discussion"),
            (15, "Interview Skills", "interview", "Technical presentation, STAR method, project defense"),
        ]
        skill_id_map = {}
        for s_id, s_name, s_cat, s_desc in skills_def:
            s = db.query(Skill).filter(Skill.name == s_name).first()
            if not s:
                s = Skill(name=s_name, category=s_cat, description=s_desc)
                db.add(s)
                db.flush()
            skill_id_map[s_name] = s.id
        db.commit()

        # 5. Student Skills for Alex Johnson
        print("Seeding Student Skills...")
        student_skills_def = {
            "Java": 3,           # Intermediate
            "Python": 3,         # Intermediate
            "JavaScript": 3,     # Intermediate
            "SQL": 3,            # Intermediate
            "React": 3,          # Intermediate
            "DSA": 1,            # Beginner (creates Major Gap for top roles!)
            "OOP": 3,            # Intermediate
            "DBMS": 2,           # Basic
            "Operating Systems": 2, # Basic
            "Computer Networks": 2, # Basic
            "Aptitude": 3,       # Intermediate
            "Logical Reasoning": 3,# Intermediate
            "Communication": 3,  # Intermediate
            "Interview Skills": 2 # Basic
        }
        for s_name, lvl in student_skills_def.items():
            s_id = skill_id_map.get(s_name)
            if s_id:
                ss = db.query(StudentSkill).filter(
                    StudentSkill.student_id == student.id,
                    StudentSkill.skill_id == s_id
                ).first()
                if not ss:
                    db.add(StudentSkill(student_id=student.id, skill_id=s_id, level=lvl))
                else:
                    ss.level = lvl
        db.commit()

        # 6. Roles
        print("Seeding Roles...")
        roles_def = [
            ("Software Developer", "Builds, tests, and maintains applications and software components."),
            ("Software Engineer", "Designs scalable software architectures and engineering solutions."),
            ("Java Developer", "Specializes in enterprise Java, Spring framework, and microservices."),
            ("Backend Developer", "Develops server-side logic, databases, APIs, and business systems."),
            ("Frontend Developer", "Constructs responsive, interactive user interfaces and web applications."),
            ("Data Analyst", "Processes data pipelines, analytics dashboards, and statistical models."),
            ("QA Engineer", "Automates testing, validates quality assurance, and ensures system reliability.")
        ]
        role_id_map = {}
        for r_name, r_desc in roles_def:
            r = db.query(Role).filter(Role.name == r_name).first()
            if not r:
                r = Role(name=r_name, description=r_desc)
                db.add(r)
                db.flush()
            role_id_map[r_name] = r.id
        db.commit()

        # 7. Companies (10 companies)
        print("Seeding Companies...")
        companies_data = [
            {
                "name": "TCS",
                "logo_color": "#0033A0",
                "logo_initials": "TCS",
                "industry": "IT Services & Consulting",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "Tata Consultancy Services is a global leader in IT services, consulting, and business solutions, operating in 55 countries.",
                "eligibility_notes": "Minimum 60% or 6.0 CGPA across 10th, 12th, and Graduation. Max 1 active backlog allowed at time of test.",
                "website": "https://www.tcs.com",
                "roles": ["Software Developer", "Software Engineer"],
                "req_skills": {
                    "Java": 3, "SQL": 3, "DSA": 3, "OOP": 3, "DBMS": 2, "Aptitude": 3, "Communication": 3
                }
            },
            {
                "name": "Infosys",
                "logo_color": "#007CC3",
                "logo_initials": "INFY",
                "industry": "IT Services",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.5,
                "description": "Infosys is a global leader in next-generation digital services and consulting, enabling clients across 56 countries to navigate digital transformation.",
                "eligibility_notes": "65% throughout academics (10th, 12th, and College). No active backlogs allowed during recruitment.",
                "website": "https://www.infosys.com",
                "roles": ["Software Developer", "Java Developer"],
                "req_skills": {
                    "Java": 3, "Python": 2, "SQL": 3, "DSA": 3, "OOP": 3, "Aptitude": 3, "Communication": 3
                }
            },
            {
                "name": "Accenture",
                "logo_color": "#A100FF",
                "logo_initials": "ACN",
                "industry": "Management Consulting & IT",
                "difficulty": Difficulty.medium,
                "min_cgpa": 6.5,
                "description": "Accenture is a Fortune Global 500 company providing strategy, consulting, digital, technology, and operations services worldwide.",
                "eligibility_notes": "Minimum 6.5 CGPA. Excellent verbal communication and logical reasoning are strictly assessed in Round 1.",
                "website": "https://www.accenture.com",
                "roles": ["Software Developer", "Software Engineer"],
                "req_skills": {
                    "Java": 3, "JavaScript": 3, "SQL": 3, "DSA": 3, "OOP": 3, "Communication": 4, "Aptitude": 3
                }
            },
            {
                "name": "Wipro",
                "logo_color": "#341C6C",
                "logo_initials": "WIP",
                "industry": "IT Services & BPO",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "Wipro Limited is a leading technology services and consulting company focused on building innovative solutions addressing digital transformation needs.",
                "eligibility_notes": "60% or 6.0 CGPA minimum. Maximum 3-year gap in education allowed.",
                "website": "https://www.wipro.com",
                "roles": ["Software Developer", "Backend Developer"],
                "req_skills": {
                    "Java": 3, "SQL": 3, "DSA": 2, "OOP": 3, "Aptitude": 3, "Communication": 3
                }
            },
            {
                "name": "Zoho",
                "logo_color": "#E42527",
                "logo_initials": "ZHO",
                "industry": "SaaS & Cloud Software",
                "difficulty": Difficulty.hard,
                "min_cgpa": 6.5,
                "description": "Zoho Corporation is an Indian multinational tech company creating cloud business applications, productivity suites, and custom CRM systems.",
                "eligibility_notes": "No strict CGPA cutoff; selection is 100% merit-based through extensive live coding rounds and in-depth problem solving.",
                "website": "https://www.zoho.com",
                "roles": ["Software Developer", "Java Developer", "Backend Developer"],
                "req_skills": {
                    "Java": 4, "DSA": 4, "OOP": 4, "SQL": 3, "DBMS": 3, "Communication": 3
                }
            },
            {
                "name": "Cognizant",
                "logo_color": "#003087",
                "logo_initials": "COG",
                "industry": "IT Services",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "Cognizant engineers modern businesses to improve everyday life, serving global leaders across healthcare, finance, and manufacturing.",
                "eligibility_notes": "Minimum 60% or 6.0 CGPA. GenC and GenC Next tracks depend on coding round scores.",
                "website": "https://www.cognizant.com",
                "roles": ["Software Engineer", "Software Developer"],
                "req_skills": {
                    "Java": 3, "SQL": 2, "DSA": 2, "OOP": 3, "Communication": 3, "Aptitude": 3
                }
            },
            {
                "name": "Capgemini",
                "logo_color": "#0070AD",
                "logo_initials": "CAP",
                "industry": "IT Services & Consulting",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "Capgemini is a French multinational IT services and consulting giant with world-class engineering, digital, and cloud practices.",
                "eligibility_notes": "60% throughout 10th, 12th, and Diploma/Graduation. Game-based aptitude test in Round 1.",
                "website": "https://www.capgemini.com",
                "roles": ["Software Developer", "Software Engineer"],
                "req_skills": {
                    "Java": 3, "SQL": 3, "DSA": 2, "OOP": 2, "Communication": 3, "Aptitude": 3
                }
            },
            {
                "name": "HCLTech",
                "logo_color": "#003087",
                "logo_initials": "HCL",
                "industry": "IT Services & Infrastructure",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "HCLTech is a global technology company home to 220,000+ people across 60 countries, delivering industry-leading capabilities in digital, engineering, and cloud.",
                "eligibility_notes": "60% or 6.0 CGPA. All branches of engineering eligible.",
                "website": "https://www.hcltech.com",
                "roles": ["Software Developer", "Backend Developer"],
                "req_skills": {
                    "Java": 3, "SQL": 3, "DSA": 2, "OOP": 3, "Communication": 3
                }
            },
            {
                "name": "Tech Mahindra",
                "logo_color": "#C8102E",
                "logo_initials": "TM",
                "industry": "IT Services & Telecom",
                "difficulty": Difficulty.easy,
                "min_cgpa": 6.0,
                "description": "Tech Mahindra represents the connected world, offering innovative and customer-centric digital experiences to global telecom and enterprise clients.",
                "eligibility_notes": "Minimum 60% across 10th, 12th, and Degree. Essay writing and psychometric evaluations included.",
                "website": "https://www.techmahindra.com",
                "roles": ["Software Developer", "QA Engineer"],
                "req_skills": {
                    "Java": 3, "SQL": 2, "DSA": 2, "OOP": 3, "Communication": 3
                }
            },
            {
                "name": "IBM",
                "logo_color": "#006699",
                "logo_initials": "IBM",
                "industry": "Enterprise Software & Cloud",
                "difficulty": Difficulty.medium,
                "min_cgpa": 7.0,
                "description": "IBM is an American multinational technology corporation specializing in hybrid cloud architectures, artificial intelligence, and quantum computing.",
                "eligibility_notes": "70% or 7.0 CGPA throughout academics. Cognitive ability games assessment in preliminary screening.",
                "website": "https://www.ibm.com",
                "roles": ["Software Engineer", "Backend Developer", "Data Analyst"],
                "req_skills": {
                    "Java": 4, "Python": 3, "SQL": 4, "DSA": 4, "OOP": 4, "Communication": 3
                }
            }
        ]

        # Standard 5 recruitment rounds per company
        standard_rounds = [
            (1, "Aptitude & Cognitive Assessment", "Online evaluation covering quantitative ability, logical reasoning, and verbal comprehension.", Difficulty.easy, 3, "Focus on speed and accuracy. Practice RS Aggarwal and solve previous year papers."),
            (2, "Coding & Technical Assessment", "Hands-on coding challenges featuring 2-3 algorithmic problems (arrays, strings, recursion).", Difficulty.medium, 5, "Familiarize yourself with clean edge-case handling and standard time limits."),
            (3, "Technical Interview (Round 1)", "Deep-dive into Data Structures, OOP principles, DBMS queries, and your academic projects.", Difficulty.medium, 7, "Be ready to write live code and explain your project database schema."),
            (4, "Managerial / System Fit Interview", "Situational questions, scenario problem-solving, and adaptability assessment with senior leadership.", Difficulty.medium, 3, "Use the STAR method to structure your responses effectively."),
            (5, "HR Interview & Offer Discussion", "Evaluation of cultural alignment, communication clarity, location preferences, and career goals.", Difficulty.easy, 2, "Research the company's core values, recent milestones, and prepare thoughtful questions.")
        ]

        for c_data in companies_data:
            c = db.query(Company).filter(Company.name == c_data["name"]).first()
            if not c:
                c = Company(
                    name=c_data["name"],
                    logo_color=c_data["logo_color"],
                    logo_initials=c_data["logo_initials"],
                    industry=c_data["industry"],
                    difficulty=c_data["difficulty"],
                    min_cgpa=c_data["min_cgpa"],
                    description=c_data["description"],
                    eligibility_notes=c_data["eligibility_notes"],
                    website=c_data["website"],
                    is_active=True
                )
                db.add(c)
                db.flush()
            else:
                c.logo_color = c_data["logo_color"]
                c.logo_initials = c_data["logo_initials"]
                c.industry = c_data["industry"]
                c.description = c_data["description"]
                c.eligibility_notes = c_data["eligibility_notes"]

            # Add recruitment rounds
            for r_num, r_name, r_desc, r_diff, r_days, r_tips in standard_rounds:
                round_rec = db.query(RecruitmentRound).filter(
                    RecruitmentRound.company_id == c.id,
                    RecruitmentRound.round_number == r_num
                ).first()
                if not round_rec:
                    round_rec = RecruitmentRound(
                        company_id=c.id,
                        round_number=r_num,
                        name=r_name,
                        description=r_desc,
                        difficulty=r_diff,
                        estimated_days=r_days,
                        tips=r_tips
                    )
                    db.add(round_rec)

            # Add roles and company skills
            for r_name in c_data["roles"]:
                r_id = role_id_map.get(r_name)
                if r_id:
                    cr = db.query(CompanyRole).filter(
                        CompanyRole.company_id == c.id,
                        CompanyRole.role_id == r_id
                    ).first()
                    if not cr:
                        cr = CompanyRole(
                            company_id=c.id,
                            role_id=r_id,
                            is_active=True,
                            notes=f"Key technical recruitment profile for {c_data['name']}."
                        )
                        db.add(cr)
                        db.flush()

                    # Add required skills
                    for s_name, req_lvl in c_data["req_skills"].items():
                        s_id = skill_id_map.get(s_name)
                        if s_id:
                            cs = db.query(CompanySkill).filter(
                                CompanySkill.company_role_id == cr.id,
                                CompanySkill.skill_id == s_id
                            ).first()
                            if not cs:
                                db.add(CompanySkill(
                                    company_role_id=cr.id,
                                    skill_id=s_id,
                                    required_level=req_lvl,
                                    weight=1.0
                                ))
        db.commit()

        # 8. Questions (100+ realistic questions)
        print("Seeding Questions...")
        existing_q_count = db.query(Question).count()
        if existing_q_count < 50:
            raw_questions = [
                # APTITUDE (12)
                {
                    "q": "A train 150 meters long passes a pole in 15 seconds. What is the speed of the train in km/h?",
                    "cat": QuestionCategory.aptitude, "topic": "Speed & Distance", "diff": Difficulty.easy,
                    "exp": "Speed = Distance/Time = 150/15 = 10 m/s. In km/h: 10 * (18/5) = 36 km/h.",
                    "opts": [("36 km/h", True), ("45 km/h", False), ("30 km/h", False), ("40 km/h", False)]
                },
                {
                    "q": "If 6 workers can build a wall in 10 days, how many days will 10 workers take to build the same wall?",
                    "cat": QuestionCategory.aptitude, "topic": "Time & Work", "diff": Difficulty.easy,
                    "exp": "Total work = 6 * 10 = 60 man-days. With 10 workers: 60 / 10 = 6 days.",
                    "opts": [("6 days", True), ("8 days", False), ("5 days", False), ("4 days", False)]
                },
                {
                    "q": "A shopkeeper sells an article at Rs. 540 gaining a 20% profit. What was the original cost price?",
                    "cat": QuestionCategory.aptitude, "topic": "Profit & Loss", "diff": Difficulty.medium,
                    "exp": "SP = CP * 1.20. Therefore CP = 540 / 1.20 = Rs. 450.",
                    "opts": [("Rs. 450", True), ("Rs. 480", False), ("Rs. 420", False), ("Rs. 500", False)]
                },
                {
                    "q": "What is the probability of obtaining a prime number when a fair 6-sided die is rolled once?",
                    "cat": QuestionCategory.aptitude, "topic": "Probability", "diff": Difficulty.easy,
                    "exp": "The prime outcomes are {2, 3, 5} out of 6 possible numbers. Probability = 3/6 = 1/2.",
                    "opts": [("1/2", True), ("1/3", False), ("2/3", False), ("1/6", False)]
                },
                {
                    "q": "Two numbers are in the ratio 3:5. If their LCM is 120, what is the sum of the two numbers?",
                    "cat": QuestionCategory.aptitude, "topic": "Ratios", "diff": Difficulty.medium,
                    "exp": "Let numbers be 3x and 5x. LCM(3x, 5x) = 15x = 120 => x = 8. Numbers are 24 and 40. Sum = 64.",
                    "opts": [("64", True), ("60", False), ("72", False), ("56", False)]
                },
                {
                    "q": "Find the missing number in the sequence: 2, 6, 12, 20, 30, ?",
                    "cat": QuestionCategory.aptitude, "topic": "Number Series", "diff": Difficulty.easy,
                    "exp": "Differences are +4, +6, +8, +10, +12. 30 + 12 = 42.",
                    "opts": [("42", True), ("40", False), ("44", False), ("36", False)]
                },
                {
                    "q": "A can complete a project in 12 days, and B can complete it in 15 days. Working together, how many days will they take?",
                    "cat": QuestionCategory.aptitude, "topic": "Time & Work", "diff": Difficulty.easy,
                    "exp": "Combined rate = 1/12 + 1/15 = 9/60 = 3/20 per day. Time = 20/3 = 6.67 days.",
                    "opts": [("6.67 days", True), ("7.5 days", False), ("6 days", False), ("8 days", False)]
                },
                {
                    "q": "What is 35% of 280?",
                    "cat": QuestionCategory.aptitude, "topic": "Percentages", "diff": Difficulty.easy,
                    "exp": "0.35 * 280 = 98.",
                    "opts": [("98", True), ("96", False), ("102", False), ("94", False)]
                },
                {
                    "q": "A sum of money doubles itself in 5 years at simple interest. In how many years will it become four times itself?",
                    "cat": QuestionCategory.aptitude, "topic": "Simple Interest", "diff": Difficulty.medium,
                    "exp": "Interest for doubling (P) takes 5 years. For becoming 4P (interest 3P), it takes 3 * 5 = 15 years.",
                    "opts": [("15 years", True), ("10 years", False), ("20 years", False), ("25 years", False)]
                },
                {
                    "q": "In an examination, 70% candidates passed in English and 65% passed in Math. If 15% failed in both, what % passed in both?",
                    "cat": QuestionCategory.aptitude, "topic": "Set Theory", "diff": Difficulty.medium,
                    "exp": "Failed in at least one = 100 - 15 = 85%. P(E or M) = 85%. P(E and M) = 70 + 65 - 85 = 50%.",
                    "opts": [("50%", True), ("45%", False), ("55%", False), ("60%", False)]
                },
                {
                    "q": "A pipe can fill a cistern in 6 hours and another can empty it in 8 hours. If both open, how long to fill the cistern?",
                    "cat": QuestionCategory.aptitude, "topic": "Pipes & Cisterns", "diff": Difficulty.medium,
                    "exp": "Net rate = 1/6 - 1/8 = 1/24 per hour. Time = 24 hours.",
                    "opts": [("24 hours", True), ("20 hours", False), ("18 hours", False), ("14 hours", False)]
                },
                {
                    "q": "The average age of 24 students and their teacher is 15 years. If the teacher's age is excluded, the average drops by 1. What is the teacher's age?",
                    "cat": QuestionCategory.aptitude, "topic": "Averages", "diff": Difficulty.medium,
                    "exp": "Total with teacher = 25 * 15 = 375. Students total = 24 * 14 = 336. Teacher's age = 375 - 336 = 39.",
                    "opts": [("39 years", True), ("35 years", False), ("40 years", False), ("42 years", False)]
                },

                # DSA (15)
                {
                    "q": "What is the worst-case time complexity of QuickSort when a naive pivot selection is used?",
                    "cat": QuestionCategory.dsa, "topic": "Sorting", "diff": Difficulty.medium,
                    "exp": "When the array is already sorted and the first/last element is picked as pivot, partitions become unbalanced: O(n^2).",
                    "opts": [("O(n^2)", True), ("O(n log n)", False), ("O(n)", False), ("O(log n)", False)]
                },
                {
                    "q": "Which data structure is fundamentally used to implement Breadth-First Search (BFS) in graphs?",
                    "cat": QuestionCategory.dsa, "topic": "Graphs", "diff": Difficulty.easy,
                    "exp": "BFS processes nodes level by level using a FIFO Queue.",
                    "opts": [("Queue", True), ("Stack", False), ("Priority Queue", False), ("Array", False)]
                },
                {
                    "q": "What is the auxiliary space complexity required to reverse a singly linked list in-place?",
                    "cat": QuestionCategory.dsa, "topic": "Linked Lists", "diff": Difficulty.easy,
                    "exp": "In-place iterative reversal requires only three pointers (prev, curr, next), which takes O(1) extra space.",
                    "opts": [("O(1)", True), ("O(n)", False), ("O(log n)", False), ("O(n^2)", False)]
                },
                {
                    "q": "Which algorithm finds the single-source shortest path on a directed graph with non-negative edge weights?",
                    "cat": QuestionCategory.dsa, "topic": "Graphs", "diff": Difficulty.medium,
                    "exp": "Dijkstra's algorithm greedily extracts the minimum-distance vertex using a min-heap in O((V + E) log V).",
                    "opts": [("Dijkstra's Algorithm", True), ("Bellman-Ford Algorithm", False), ("Floyd-Warshall", False), ("Prim's Algorithm", False)]
                },
                {
                    "q": "What is the time complexity of searching for an element in a balanced Binary Search Tree (AVL / Red-Black)?",
                    "cat": QuestionCategory.dsa, "topic": "Trees", "diff": Difficulty.easy,
                    "exp": "Since the height of a balanced BST is strictly bounded by O(log n), search operates in O(log n).",
                    "opts": [("O(log n)", True), ("O(n)", False), ("O(1)", False), ("O(n log n)", False)]
                },
                {
                    "q": "Kadane's algorithm is celebrated for solving which classic problem in O(n) time?",
                    "cat": QuestionCategory.dsa, "topic": "Arrays", "diff": Difficulty.medium,
                    "exp": "Kadane's algorithm finds the contiguous subarray with the largest sum in linear time.",
                    "opts": [("Maximum Subarray Sum", True), ("Two Sum Problem", False), ("Longest Common Subsequence", False), ("Matrix Multiplication", False)]
                },
                {
                    "q": "Inorder traversal of a Binary Search Tree produces nodes in what sequence?",
                    "cat": QuestionCategory.dsa, "topic": "Trees", "diff": Difficulty.easy,
                    "exp": "Inorder (Left-Root-Right) visits smaller elements before the parent and larger after, resulting in ascending sorted order.",
                    "opts": [("Sorted ascending order", True), ("Sorted descending order", False), ("Level by level order", False), ("Postorder sequence", False)]
                },
                {
                    "q": "Which of the following sorting algorithms is NOT stable in its standard formulation?",
                    "cat": QuestionCategory.dsa, "topic": "Sorting", "diff": Difficulty.medium,
                    "exp": "QuickSort can swap non-adjacent identical elements across the pivot, violating original relative order.",
                    "opts": [("QuickSort", True), ("MergeSort", False), ("InsertionSort", False), ("BubbleSort", False)]
                },
                {
                    "q": "What is the minimum number of queues needed to implement a FIFO Stack?",
                    "cat": QuestionCategory.dsa, "topic": "Stacks & Queues", "diff": Difficulty.medium,
                    "exp": "Two queues (or one queue with cyclic rotation) are needed to reverse FIFO behavior to simulate LIFO.",
                    "opts": [("2", True), ("1", False), ("3", False), ("4", False)]
                },
                {
                    "q": "What is the best average-case time complexity of searching an element in a Hash Map?",
                    "cat": QuestionCategory.dsa, "topic": "Hashing", "diff": Difficulty.easy,
                    "exp": "Assuming uniform hashing and low collision factor, hash table lookups execute in O(1) expected time.",
                    "opts": [("O(1)", True), ("O(log n)", False), ("O(n)", False), ("O(n log n)", False)]
                },
                {
                    "q": "Which data structure is optimally suited to verify balanced parentheses in an expression?",
                    "cat": QuestionCategory.dsa, "topic": "Stacks & Queues", "diff": Difficulty.easy,
                    "exp": "A Stack stores opening brackets and pops to match closing brackets in strict LIFO order.",
                    "opts": [("Stack", True), ("Queue", False), ("Linked List", False), ("Binary Tree", False)]
                },
                {
                    "q": "What is the time complexity to build a binary heap from an unsorted array of n elements?",
                    "cat": QuestionCategory.dsa, "topic": "Heaps", "diff": Difficulty.hard,
                    "exp": "Bottom-up heap construction (heapify from n/2 down to 1) converges mathematically to O(n).",
                    "opts": [("O(n)", True), ("O(n log n)", False), ("O(log n)", False), ("O(n^2)", False)]
                },
                {
                    "q": "Which algorithm is used to detect strongly connected components in a directed graph?",
                    "cat": QuestionCategory.dsa, "topic": "Graphs", "diff": Difficulty.hard,
                    "exp": "Tarjan's or Kosaraju's algorithm finds SCCs using DFS traversals in linear O(V + E) time.",
                    "opts": [("Kosaraju's Algorithm", True), ("Kruskal's Algorithm", False), ("Floyd-Warshall", False), ("Dijkstra's Algorithm", False)]
                },
                {
                    "q": "In a max-heap with n elements, where can the minimum element be located?",
                    "cat": QuestionCategory.dsa, "topic": "Heaps", "diff": Difficulty.medium,
                    "exp": "In a max-heap, every parent is greater than its children; hence the minimum must reside in one of the leaf nodes.",
                    "opts": [("Only at one of the leaf nodes", True), ("At the root node", False), ("At index 1", False), ("At the second level", False)]
                },
                {
                    "q": "What is the amortized time complexity of an push operation in a dynamic array (like ArrayList/vector)?",
                    "cat": QuestionCategory.dsa, "topic": "Arrays", "diff": Difficulty.medium,
                    "exp": "Doubling array capacity occurs infrequently; the total cost of n insertions divided by n is O(1) amortized.",
                    "opts": [("O(1) amortized", True), ("O(n) amortized", False), ("O(log n) amortized", False), ("O(n^2)", False)]
                },

                # OOP (12)
                {
                    "q": "Which OOP pillar focuses on wrapping data and methods into a single unit and restricting direct outside access?",
                    "cat": QuestionCategory.oop, "topic": "Encapsulation", "diff": Difficulty.easy,
                    "exp": "Encapsulation keeps fields private and exposes controlled access via public getters and setters.",
                    "opts": [("Encapsulation", True), ("Inheritance", False), ("Polymorphism", False), ("Abstraction", False)]
                },
                {
                    "q": "Method overriding in Java is an example of which type of polymorphism?",
                    "cat": QuestionCategory.oop, "topic": "Polymorphism", "diff": Difficulty.easy,
                    "exp": "Overridden methods are dynamically bound at runtime based on the actual object instance (Dynamic Dispatch).",
                    "opts": [("Runtime Polymorphism", True), ("Compile-time Polymorphism", False), ("Ad-hoc Polymorphism", False), ("Parametric Polymorphism", False)]
                },
                {
                    "q": "Which Java keyword prevents a class from being inherited by any other class?",
                    "cat": QuestionCategory.oop, "topic": "Inheritance", "diff": Difficulty.easy,
                    "exp": "Declaring 'final class MyClass' prevents inheritance and protects immutable structures.",
                    "opts": [("final", True), ("static", False), ("abstract", False), ("const", False)]
                },
                {
                    "q": "What does the 'L' stand for in the SOLID design principles?",
                    "cat": QuestionCategory.oop, "topic": "SOLID Principles", "diff": Difficulty.medium,
                    "exp": "Liskov Substitution Principle: Objects of a superclass should be replaceable with objects of a subclass without breaking behavior.",
                    "opts": [("Liskov Substitution Principle", True), ("Lazy Initialization Principle", False), ("Linear Structure Principle", False), ("Loosely Coupled Principle", False)]
                },
                {
                    "q": "Which design pattern restricts class instantiation to a single shared object across the entire application?",
                    "cat": QuestionCategory.oop, "topic": "Design Patterns", "diff": Difficulty.easy,
                    "exp": "The Singleton pattern privateizes the constructor and provides a global static getInstance() accessor.",
                    "opts": [("Singleton Pattern", True), ("Factory Pattern", False), ("Observer Pattern", False), ("Prototype Pattern", False)]
                },
                {
                    "q": "Can an abstract class in Java have a constructor?",
                    "cat": QuestionCategory.oop, "topic": "Abstraction", "diff": Difficulty.medium,
                    "exp": "Yes, abstract classes have constructors invoked via super() when derived concrete subclasses are instantiated.",
                    "opts": [("Yes, invoked by subclasses using super()", True), ("No, because it cannot be instantiated", False), ("Only if it has no abstract methods", False), ("Only private constructors allowed", False)]
                },
                {
                    "q": "Which principle states that software entities should be open for extension but closed for modification?",
                    "cat": QuestionCategory.oop, "topic": "SOLID Principles", "diff": Difficulty.medium,
                    "exp": "The Open/Closed Principle (OCP) encourages polymorphic extension without altering tested source code.",
                    "opts": [("Open/Closed Principle", True), ("Single Responsibility Principle", False), ("Interface Segregation Principle", False), ("Dependency Inversion Principle", False)]
                },
                {
                    "q": "What is the primary difference between an Interface and an Abstract Class in modern Java (Java 8+)?",
                    "cat": QuestionCategory.oop, "topic": "Interfaces", "diff": Difficulty.medium,
                    "exp": "A class can implement multiple interfaces, but can extend only one abstract class (single class inheritance).",
                    "opts": [("A class can implement multiple interfaces but extend only one class", True), ("Interfaces cannot have any method bodies", False), ("Abstract classes cannot have instance variables", False), ("Interfaces support private constructors", False)]
                },
                {
                    "q": "Which design pattern defines a one-to-many dependency between objects so that when one changes state, all dependents are notified?",
                    "cat": QuestionCategory.oop, "topic": "Design Patterns", "diff": Difficulty.medium,
                    "exp": "The Observer pattern is the backbone of event-driven architectures and pub-sub systems.",
                    "opts": [("Observer Pattern", True), ("Strategy Pattern", False), ("Decorator Pattern", False), ("Adapter Pattern", False)]
                },
                {
                    "q": "In Java, what happens if you invoke a method on a null reference?",
                    "cat": QuestionCategory.oop, "topic": "Exception Handling", "diff": Difficulty.easy,
                    "exp": "Dereferencing null causes the JVM to throw a NullPointerException at runtime.",
                    "opts": [("NullPointerException is thrown", True), ("Compile-time error occurs", False), ("Method returns null", False), ("Program silently halts", False)]
                },
                {
                    "q": "Composition is often favored over Inheritance because:",
                    "cat": QuestionCategory.oop, "topic": "Design Principles", "diff": Difficulty.medium,
                    "exp": "Composition promotes loose coupling, dynamic runtime behavior swapping, and shields classes from fragile base-class changes.",
                    "opts": [("It provides looser coupling and greater flexibility at runtime", True), ("It uses less memory", False), ("It automatically creates database relations", False), ("It enforces single inheritance", False)]
                },
                {
                    "q": "Which design pattern is used to attach new responsibilities to an object dynamically without modifying its structure?",
                    "cat": QuestionCategory.oop, "topic": "Design Patterns", "diff": Difficulty.hard,
                    "exp": "The Decorator pattern wraps the original object within another class conforming to the same interface.",
                    "opts": [("Decorator Pattern", True), ("Facade Pattern", False), ("Composite Pattern", False), ("Proxy Pattern", False)]
                },

                # SQL (12)
                {
                    "q": "Which SQL clause is used to filter records AFTER an aggregation has been performed with GROUP BY?",
                    "cat": QuestionCategory.sql, "topic": "GROUP BY", "diff": Difficulty.easy,
                    "exp": "WHERE filters individual rows before grouping; HAVING filters aggregated groups.",
                    "opts": [("HAVING", True), ("WHERE", False), ("ORDER BY", False), ("QUALIFY", False)]
                },
                {
                    "q": "What type of JOIN returns all records from Table A, and matched records from Table B, filling missing matches with NULL?",
                    "cat": QuestionCategory.sql, "topic": "JOINs", "diff": Difficulty.easy,
                    "exp": "A LEFT OUTER JOIN preserves all rows from the left-hand table irrespective of matching keys.",
                    "opts": [("LEFT JOIN", True), ("INNER JOIN", False), ("CROSS JOIN", False), ("FULL JOIN", False)]
                },
                {
                    "q": "What is the primary operational difference between TRUNCATE and DELETE in SQL?",
                    "cat": QuestionCategory.sql, "topic": "DML vs DDL", "diff": Difficulty.medium,
                    "exp": "TRUNCATE is a DDL command that deallocates data pages quickly without row-by-row logging and cannot be filtered with WHERE.",
                    "opts": [("TRUNCATE is DDL and faster without row-by-row logging; DELETE is DML", True), ("TRUNCATE can use WHERE clause; DELETE cannot", False), ("DELETE resets identity columns; TRUNCATE does not", False), ("There is no difference", False)]
                },
                {
                    "q": "Which constraint ensures that all values in a column are strictly unique and never NULL?",
                    "cat": QuestionCategory.sql, "topic": "Constraints", "diff": Difficulty.easy,
                    "exp": "PRIMARY KEY uniquely identifies each record and rejects NULL values by definition.",
                    "opts": [("PRIMARY KEY", True), ("UNIQUE", False), ("CHECK", False), ("FOREIGN KEY", False)]
                },
                {
                    "q": "What does a database Clustered Index do to table rows?",
                    "cat": QuestionCategory.sql, "topic": "Indexes", "diff": Difficulty.medium,
                    "exp": "A clustered index physically sorts and stores the data rows in the table based on the indexed key columns.",
                    "opts": [("It dictates the physical ordering of data rows on disk", True), ("It creates a separate pointer list without rearranging rows", False), ("It prevents insertion of duplicate records", False), ("It accelerates only text search queries", False)]
                },
                {
                    "q": "Which window function assigns a unique sequential integer to rows within a partition without gaps?",
                    "cat": QuestionCategory.sql, "topic": "Window Functions", "diff": Difficulty.medium,
                    "exp": "ROW_NUMBER() assigns a unique ascending integer starting from 1 to each row in the partition.",
                    "opts": [("ROW_NUMBER()", True), ("RANK()", False), ("DENSE_RANK()", False), ("NTILE()", False)]
                },
                {
                    "q": "What is the result of multiplying the row counts of two tables in a CROSS JOIN?",
                    "cat": QuestionCategory.sql, "topic": "JOINs", "diff": Difficulty.easy,
                    "exp": "CROSS JOIN produces a Cartesian product: Table 1 count * Table 2 count.",
                    "opts": [("Cartesian Product (Count A * Count B)", True), ("Sum of counts (Count A + Count B)", False), ("Maximum count between the two", False), ("Zero unless keys match", False)]
                },
                {
                    "q": "What does the ACID property 'Atomicity' guarantee in database transactions?",
                    "cat": QuestionCategory.sql, "topic": "Transactions", "diff": Difficulty.easy,
                    "exp": "Atomicity ensures 'all or nothing' execution: either all operations in a transaction succeed, or the entire transaction is rolled back.",
                    "opts": [("Either all transaction statements succeed, or all are rolled back", True), ("Data is instantly replicated to slave nodes", False), ("Transactions execute isolated from each other", False), ("Committed data persists permanently", False)]
                },
                {
                    "q": "Which SQL statement is used to remove a table's schema definition and all its data permanently?",
                    "cat": QuestionCategory.sql, "topic": "DDL", "diff": Difficulty.easy,
                    "exp": "DROP TABLE deletes both the table metadata and data completely from the database catalog.",
                    "opts": [("DROP TABLE", True), ("DELETE TABLE", False), ("CLEAR TABLE", False), ("REMOVE TABLE", False)]
                },
                {
                    "q": "What is a correlated subquery in SQL?",
                    "cat": QuestionCategory.sql, "topic": "Subqueries", "diff": Difficulty.medium,
                    "exp": "A correlated subquery references columns from the outer query and evaluates once for every candidate row processed by the outer query.",
                    "opts": [("A subquery that relies on values from the outer query for each row", True), ("A query that executes independently before the main query", False), ("A query stored in a database view", False), ("A temporary table created via CTE", False)]
                },
                {
                    "q": "What is the primary risk of using 'SELECT *' in production queries?",
                    "cat": QuestionCategory.sql, "topic": "Performance", "diff": Difficulty.easy,
                    "exp": "It transfers unnecessary columns over the network, prevents covering index usage, and increases I/O overhead.",
                    "opts": [("Increases unnecessary I/O, network bandwidth, and breaks covering indexes", True), ("Causes database deadlocks", False), ("Syntax is deprecated in ANSI SQL", False), ("Forces table creation locks", False)]
                },
                {
                    "q": "Which transaction isolation level completely prevents Dirty Reads, Non-Repeatable Reads, and Phantom Reads?",
                    "cat": QuestionCategory.sql, "topic": "Transactions", "diff": Difficulty.hard,
                    "exp": "SERIALIZABLE is the strictest ANSI isolation level, executing transactions as though they occurred sequentially.",
                    "opts": [("SERIALIZABLE", True), ("REPEATABLE READ", False), ("READ COMMITTED", False), ("READ UNCOMMITTED", False)]
                },

                # DBMS (10)
                {
                    "q": "A relational database table is in Second Normal Form (2NF) if it is in 1NF and:",
                    "cat": QuestionCategory.dbms, "topic": "Normalization", "diff": Difficulty.medium,
                    "exp": "2NF requires eliminating partial functional dependencies: all non-prime attributes must be fully functionally dependent on the entire primary key.",
                    "opts": [("Has no partial dependency on candidate keys", True), ("Has no transitive dependencies", False), ("Has multivalued dependencies removed", False), ("All attributes are atomic", False)]
                },
                {
                    "q": "Third Normal Form (3NF) strictly eliminates which type of dependency?",
                    "cat": QuestionCategory.dbms, "topic": "Normalization", "diff": Difficulty.medium,
                    "exp": "3NF eliminates transitive dependencies: non-prime attributes cannot depend on other non-prime attributes.",
                    "opts": [("Transitive Dependency", True), ("Partial Dependency", False), ("Multivalued Dependency", False), ("Join Dependency", False)]
                },
                {
                    "q": "What anomaly occurs when a transaction reads data that has been modified by an uncommitted transaction?",
                    "cat": QuestionCategory.dbms, "topic": "Concurrency", "diff": Difficulty.medium,
                    "exp": "Dirty Read occurs when reading uncommitted changes that might later be rolled back.",
                    "opts": [("Dirty Read", True), ("Non-Repeatable Read", False), ("Phantom Read", False), ("Lost Update", False)]
                },
                {
                    "q": "What is the purpose of Write-Ahead Logging (WAL) in database recovery?",
                    "cat": QuestionCategory.dbms, "topic": "Recovery", "diff": Difficulty.medium,
                    "exp": "WAL ensures log records of changes are written to persistent storage before data pages are flushed to disk, ensuring Durability and crash recovery.",
                    "opts": [("Ensures transaction log entries are persisted before data pages are written", True), ("Encrypts all write queries", False), ("Compacts table space asynchronously", False), ("Validates foreign key integrity", False)]
                },
                {
                    "q": "What data structure is predominantly used for database B-Tree index nodes on disk?",
                    "cat": QuestionCategory.dbms, "topic": "Storage & Indexing", "diff": Difficulty.medium,
                    "exp": "B+ Trees keep all data records in leaf nodes connected as a doubly linked list, enabling fast range scans and predictable shallow tree depths.",
                    "opts": [("B+ Tree", True), ("Binary Search Tree", False), ("Red-Black Tree", False), ("Trie", False)]
                },
                {
                    "q": "In Entity-Relationship modeling, what does a diamond shape represent?",
                    "cat": QuestionCategory.dbms, "topic": "ER Modeling", "diff": Difficulty.easy,
                    "exp": "In standard Chen ER notation, rectangles denote Entities, ellipses denote Attributes, and diamonds denote Relationships.",
                    "opts": [("Relationship set", True), ("Entity set", False), ("Attribute", False), ("Primary key", False)]
                },
                {
                    "q": "What is a Candidate Key in a relational schema?",
                    "cat": QuestionCategory.dbms, "topic": "Keys", "diff": Difficulty.easy,
                    "exp": "A candidate key is a minimal superkey capable of uniquely identifying any tuple in a relation without redundant attributes.",
                    "opts": [("A minimal set of attributes that uniquely identifies a row", True), ("A foreign key pointing to external tables", False), ("Any column containing unique numbers", False), ("A key created by composite indexes", False)]
                },
                {
                    "q": "Which concurrency control protocol prevents cascading rollbacks and guarantees serializability using shared and exclusive locks?",
                    "cat": QuestionCategory.dbms, "topic": "Concurrency", "diff": Difficulty.hard,
                    "exp": "Strict Two-Phase Locking (Strict 2PL) holds all exclusive locks until transaction commit/abort, guaranteeing serializability and no cascading aborts.",
                    "opts": [("Strict Two-Phase Locking (Strict 2PL)", True), ("Time-stamp Ordering", False), ("Validation-based Protocol", False), ("Snapshot Isolation", False)]
                },
                {
                    "q": "What is the primary benefit of Database Normalization?",
                    "cat": QuestionCategory.dbms, "topic": "Normalization", "diff": Difficulty.easy,
                    "exp": "Normalization minimizes data redundancy, prevents update/insertion/deletion anomalies, and ensures logical data integrity.",
                    "opts": [("Minimizes data redundancy and prevents update anomalies", True), ("Increases query speed across all JOINs", False), ("Automates backup generation", False), ("Eliminates the need for foreign keys", False)]
                },
                {
                    "q": "What does database Sharding accomplish?",
                    "cat": QuestionCategory.dbms, "topic": "Architecture", "diff": Difficulty.medium,
                    "exp": "Sharding horizontally partitions database rows across multiple independent physical database instances for scale.",
                    "opts": [("Horizontally partitions data across multiple machines", True), ("Replicates identical tables to backup nodes", False), ("Caches queries in Redis memory", False), ("Converts SQL tables to NoSQL collections", False)]
                },

                # TECHNICAL / CS FUNDAMENTALS (12)
                {
                    "q": "In Operating Systems, what condition is NOT one of Coffman's four necessary conditions for Deadlock?",
                    "cat": QuestionCategory.technical, "topic": "Operating Systems", "diff": Difficulty.medium,
                    "exp": "The four conditions are Mutual Exclusion, Hold & Wait, No Preemption, and Circular Wait. Preemption prevents deadlocks.",
                    "opts": [("Preemption Allowed", True), ("Mutual Exclusion", False), ("Hold and Wait", False), ("Circular Wait", False)]
                },
                {
                    "q": "Which layer of the OSI model is responsible for end-to-end reliable transmission, flow control, and segmentation?",
                    "cat": QuestionCategory.technical, "topic": "Computer Networks", "diff": Difficulty.easy,
                    "exp": "The Transport Layer (Layer 4, e.g. TCP) provides end-to-end process-level communication, sequencing, and flow control.",
                    "opts": [("Transport Layer", True), ("Network Layer", False), ("Data Link Layer", False), ("Session Layer", False)]
                },
                {
                    "q": "What is the primary difference between a Process and a Thread?",
                    "cat": QuestionCategory.technical, "topic": "Operating Systems", "diff": Difficulty.easy,
                    "exp": "A process has its own isolated address space; threads within the same process share code, heap, and open files, having only their own stack.",
                    "opts": [("Threads share memory and address space of the parent process; processes are isolated", True), ("Processes run on CPUs; threads run on GPUs", False), ("Threads cannot run concurrently", False), ("Processes cannot have child threads", False)]
                },
                {
                    "q": "What HTTP status code represents '401 Unauthorized' versus '403 Forbidden'?",
                    "cat": QuestionCategory.technical, "topic": "Web Protocols", "diff": Difficulty.easy,
                    "exp": "401 means unauthenticated (credentials missing or invalid); 403 means authenticated but lacking necessary permissions.",
                    "opts": [("401 = Not authenticated; 403 = Authenticated but forbidden from resource", True), ("401 = Resource not found; 403 = Server crash", False), ("401 = Method not allowed; 403 = Timeout", False), ("They are interchangeable", False)]
                },
                {
                    "q": "In Computer Networks, what protocol translates human-readable domain names into IP addresses?",
                    "cat": QuestionCategory.technical, "topic": "Computer Networks", "diff": Difficulty.easy,
                    "exp": "DNS (Domain Name System) resolves hostnames like google.com into numerical IP addresses.",
                    "opts": [("DNS", True), ("DHCP", False), ("ARP", False), ("NAT", False)]
                },
                {
                    "q": "What is Virtual Memory in modern computer architectures?",
                    "cat": QuestionCategory.technical, "topic": "Operating Systems", "diff": Difficulty.medium,
                    "exp": "Virtual memory maps process logical addresses to physical RAM and secondary disk storage via paging, giving each process the illusion of continuous memory.",
                    "opts": [("A memory management capability giving processes the illusion of large contiguous RAM using paging", True), ("Extra RAM installed in cloud servers", False), ("CPU L1 cache storage", False), ("ROM BIOS storage", False)]
                },
                {
                    "q": "What happens during a TCP 3-Way Handshake before establishing a connection?",
                    "cat": QuestionCategory.technical, "topic": "Computer Networks", "diff": Difficulty.medium,
                    "exp": "Client sends SYN, server responds with SYN-ACK, client acknowledges with ACK to establish synchronized sequence numbers.",
                    "opts": [("SYN -> SYN-ACK -> ACK", True), ("ACK -> SYN -> SYN-ACK", False), ("PING -> PONG -> CONNECT", False), ("REQUEST -> RESPONSE -> READY", False)]
                },
                {
                    "q": "What is the primary role of Git command 'git rebase' compared to 'git merge'?",
                    "cat": QuestionCategory.technical, "topic": "Version Control", "diff": Difficulty.medium,
                    "exp": "Rebase replays branch commits on top of the target base commit, preserving a linear project history without merge commits.",
                    "opts": [("Replays commits on top of another base for a clean linear commit history", True), ("Deletes remote branch copies", False), ("Reverts working tree files to last commit", False), ("Creates an automatic release tag", False)]
                },
                {
                    "q": "What does idempotency mean in the context of RESTful HTTP methods?",
                    "cat": QuestionCategory.technical, "topic": "Web Protocols", "diff": Difficulty.medium,
                    "exp": "An idempotent HTTP method (like GET, PUT, DELETE) produces identical side effects on the server regardless of how many times it is repeated.",
                    "opts": [("Making multiple identical requests produces the exact same server state as a single request", True), ("Requests execute synchronously without blocking", False), ("Payloads are automatically compressed", False), ("Endpoints require OAuth tokens", False)]
                },
                {
                    "q": "What is a Race Condition in concurrent programming?",
                    "cat": QuestionCategory.technical, "topic": "Concurrency", "diff": Difficulty.easy,
                    "exp": "A race condition occurs when multiple threads concurrently read and write shared data without synchronization, making the outcome order-dependent.",
                    "opts": [("Unsynchronized concurrent access to shared resources where final outcome depends on execution timing", True), ("A sorting algorithm comparison test", False), ("Hardware bus throttling", False), ("High network bandwidth latency", False)]
                },
                {
                    "q": "Which scheduling algorithm in Operating Systems can cause starvation for low-priority processes?",
                    "cat": QuestionCategory.technical, "topic": "Operating Systems", "diff": Difficulty.medium,
                    "exp": "Priority Scheduling without aging can indefinitely starve low-priority processes if higher-priority tasks keep arriving.",
                    "opts": [("Priority Scheduling", True), ("Round Robin", False), ("First-Come, First-Served", False), ("Shortest Job First with aging", False)]
                },
                {
                    "q": "What is the purpose of CORS (Cross-Origin Resource Sharing) in web browsers?",
                    "cat": QuestionCategory.technical, "topic": "Web Protocols", "diff": Difficulty.medium,
                    "exp": "CORS is an HTTP-header based security mechanism that lets servers specify which origins are permitted to access their resources from a browser.",
                    "opts": [("A security mechanism controlling how web browsers request resources from different domains", True), ("A protocol to compress image files", False), ("A database replication technique", False), ("A method to speed up DNS lookup", False)]
                }
            ]

            for item in raw_questions:
                q = Question(
                    question_text=item["q"],
                    category=item["cat"],
                    topic=item["topic"],
                    difficulty=item["diff"],
                    explanation=item["exp"],
                    is_active=True
                )
                db.add(q)
                db.flush()
                for idx, (opt_text, is_corr) in enumerate(item["opts"]):
                    opt = QuestionOption(
                        question_id=q.id,
                        option_text=opt_text,
                        is_correct=is_corr,
                        option_order=idx + 1
                    )
                    db.add(opt)
            db.commit()

        # 9. Projects (8 projects)
        print("Seeding Projects...")
        if db.query(Project).count() < 5:
            projects_data = [
                {
                    "title": "Employee Management REST API",
                    "skills_covered": "Java, Spring Boot, MySQL, REST API, JWT",
                    "difficulty": Difficulty.medium,
                    "duration_days": 14,
                    "why_it_helps": "Directly demonstrates enterprise backend skills assessed by TCS, Infosys, and Cognizant technical interviewers.",
                    "technologies": "Java 17, Spring Boot 3, Spring Security, MySQL, Swagger"
                },
                {
                    "title": "Student Placement Preparation Portal",
                    "skills_covered": "React, JavaScript, Tailwind CSS, REST APIs",
                    "difficulty": Difficulty.medium,
                    "duration_days": 10,
                    "why_it_helps": "Shows full component lifecycle, state management, and modern responsive UI engineering.",
                    "technologies": "React 18, Vite, Tailwind CSS, Axios, Recharts"
                },
                {
                    "title": "DSA Practice Platform & Code Tracker",
                    "skills_covered": "Python, DSA, Algorithms, Problem Solving",
                    "difficulty": Difficulty.easy,
                    "duration_days": 7,
                    "why_it_helps": "Strengthens algorithmic thinking and showcases self-directed coding discipline.",
                    "technologies": "Python 3, SQLite, CLI / Flask"
                },
                {
                    "title": "E-Commerce Microservices Backend",
                    "skills_covered": "Java, Spring Boot, Docker, Microservices, PostgreSQL",
                    "difficulty": Difficulty.hard,
                    "duration_days": 21,
                    "why_it_helps": "Impresses product company interviewers (Zoho, IBM) with distributed architecture knowledge.",
                    "technologies": "Spring Cloud, Kafka, Docker, PostgreSQL"
                },
                {
                    "title": "Real-time Chat & Collaboration App",
                    "skills_covered": "JavaScript, WebSockets, Node.js, React",
                    "difficulty": Difficulty.hard,
                    "duration_days": 14,
                    "why_it_helps": "Demonstrates bidirectional communication and event-driven architecture.",
                    "technologies": "Node.js, Express, Socket.IO, React"
                },
                {
                    "title": "Financial Data Analysis & Stock Predictor",
                    "skills_covered": "Python, Pandas, SQL, Data Visualization",
                    "difficulty": Difficulty.medium,
                    "duration_days": 10,
                    "why_it_helps": "Ideal portfolio project for Data Analyst and Python Engineering tracks.",
                    "technologies": "Python, Pandas, NumPy, Matplotlib, SQLite"
                },
                {
                    "title": "Library & Inventory Management System",
                    "skills_covered": "Java, OOP, SQL, JDBC, DBMS",
                    "difficulty": Difficulty.easy,
                    "duration_days": 7,
                    "why_it_helps": "Classic interview project testing clean OOP design patterns and database normalization.",
                    "technologies": "Java, MySQL, JDBC"
                },
                {
                    "title": "API Rate Limiter & Token Bucket Service",
                    "skills_covered": "System Design, DSA, Redis, Concurrency",
                    "difficulty": Difficulty.hard,
                    "duration_days": 12,
                    "why_it_helps": "Demonstrates advanced system design, low-level concurrency, and caching proficiency.",
                    "technologies": "Go / Java, Redis, Docker"
                }
            ]
            for pd in projects_data:
                p = Project(
                    title=pd["title"],
                    skills_covered=pd["skills_covered"],
                    difficulty=pd["difficulty"],
                    duration_days=pd["duration_days"],
                    why_it_helps=pd["why_it_helps"],
                    technologies=pd["technologies"]
                )
                db.add(p)
            db.commit()

        # 10. Resources (15 resources)
        print("Seeding Resources...")
        if db.query(Resource).count() < 10:
            res_data = [
                ("Java", "Oracle Java SE Official Documentation", ResourceType.documentation, "https://docs.oracle.com/en/java/", "Complete reference for Java syntax, standard libraries, and JVM architecture."),
                ("Java", "Java Programming Masterclass", ResourceType.tutorial, "https://dev.java/learn/", "Structured guides covering OOP, Collections, Multithreading, and modern Java features."),
                ("DSA", "NeetCode 150 - Curated Algorithm Roadmap", ResourceType.practice, "https://neetcode.io", "Essential LeetCode pattern questions grouped by array, two-pointer, tree, and graph categories."),
                ("DSA", "GeeksforGeeks Data Structures", ResourceType.tutorial, "https://www.geeksforgeeks.org/data-structures/", "Comprehensive textbook explanations with code snippets in C++, Java, and Python."),
                ("SQL", "SQLZoo Interactive Query Tutorials", ResourceType.practice, "https://sqlzoo.net", "Interactive browser-based exercises for SELECT, JOINs, GROUP BY, and nested subqueries."),
                ("SQL", "Mode Analytics SQL Guide", ResourceType.tutorial, "https://mode.com/sql-tutorial/", "Deep dive into real-world business SQL queries, window functions, and analytics joins."),
                ("OOP", "Refactoring Guru - Design Patterns & SOLID", ResourceType.article, "https://refactoring.guru/design-patterns", "Visual explanations of Creational, Structural, and Behavioral software design patterns."),
                ("DBMS", "CMU Database Group - Database Architecture", ResourceType.video, "https://15445.courses.cs.cmu.edu", "World-class lecture materials on storage engines, buffer pool managers, and concurrency."),
                ("Operating Systems", "OSTEP - Operating Systems in Three Easy Pieces", ResourceType.documentation, "https://pages.cs.wisc.edu/~remzi/OSTEP/", "Free, authoritative textbook on Virtualization, Concurrency, and Persistence."),
                ("Computer Networks", "Computer Networking: A Top-Down Approach Notes", ResourceType.tutorial, "https://gaia.cs.umass.edu/kurose_ross/", "Foundational reference for the Application, Transport, and Network layer concepts."),
                ("Aptitude", "IndiaBIX Quantitative Aptitude", ResourceType.practice, "https://www.indiabix.com", "Classic bank of company placement aptitude questions with step-by-step solutions."),
                ("Interview Skills", "Tech Interview Handbook", ResourceType.article, "https://www.techinterviewhandbook.org", "Curated technical interview cheat sheets, behavioral STAR frameworks, and resume advice.")
            ]
            for top, title, r_type, url, desc in res_data:
                r = Resource(
                    topic=top,
                    title=title,
                    resource_type=r_type,
                    url=url,
                    description=desc,
                    is_free=True
                )
                db.add(r)
            db.commit()

        # 11. Create an active demo roadmap for Alex Johnson for TCS Software Developer
        print("Setting up initial demo roadmap for Alex Johnson...")
        tcs = db.query(Company).filter(Company.name == "TCS").first()
        if tcs and student:
            tcs_role = db.query(CompanyRole).filter(CompanyRole.company_id == tcs.id).first()
            if tcs_role:
                from app.services.roadmap import generate_roadmap
                # Generate a 30-day preparation roadmap
                roadmap = generate_roadmap(
                    db=db,
                    student_id=student.id,
                    company_id=tcs.id,
                    company_role_id=tcs_role.id,
                    total_days=30,
                    daily_hours=2.5
                )
                # Mark first 3 tasks as completed for instant visual progress
                if roadmap.tasks:
                    for t in roadmap.tasks[:3]:
                        t.status = TaskStatus.completed
                        t.score = 85.0
                        t.completed_at = datetime.utcnow()
                    db.commit()

        print("\n=======================================================")
        print("SEEDING COMPLETE!")
        print("Admin user:   admin@prepplanner.com  / Admin@123")
        print("Student user: student@example.com    / Student@123")
        print(f"Total Companies: {db.query(Company).count()}")
        print(f"Total Questions: {db.query(Question).count()}")
        print(f"Total Skills:    {db.query(Skill).count()}")
        print(f"Total Projects:  {db.query(Project).count()}")
        print("=======================================================\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
