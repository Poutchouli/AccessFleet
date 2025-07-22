# init_database.py
# This script initializes the IT Provisioning Platform database in PostgreSQL.
# It creates the schema and populates it with sample data for testing.

import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import our models to ensure they're registered
import models
from database import Base, SQLALCHEMY_DATABASE_URL

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    engine = None
    # Retry loop to wait for the database container to be ready
    while not engine:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception as e:
            print(f"Waiting for database connection... ({e})")
            time.sleep(2)
    
    print("✅ Database connection established successfully.")
    return engine

def drop_and_create_tables(engine):
    """Drops all existing tables and recreates them from the models."""
    print("\nDropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All existing tables dropped.")
    
    print("\nCreating database schema from models...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema created successfully.")

def insert_sample_data(engine):
    """Inserts sample data for testing the mailbox management interface."""
    print("\nInserting sample data...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create Users (Managers and Admins)
        admin_user = models.User(
            full_name="Alice Administrator",
            email="alice.admin@company.com", 
            role=models.UserRole.admin,
            service="IT Department"
        )
        
        manager1 = models.User(
            full_name="Bob Manager",
            email="bob.manager@company.com",
            role=models.UserRole.manager,
            service="Sales Department"
        )
        
        manager2 = models.User(
            full_name="Carol Manager", 
            email="carol.manager@company.com",
            role=models.UserRole.manager,
            service="Marketing Department"
        )
        
        # Create some regular users for the mailbox user lists
        regular_users = [
            models.User(
                full_name="David Employee",
                email="david.employee@company.com",
                role=models.UserRole.manager,  # Using manager role as we only have 2 roles
                service="Sales Department"
            ),
            models.User(
                full_name="Eva Worker",
                email="eva.worker@company.com", 
                role=models.UserRole.manager,
                service="Marketing Department"
            ),
            models.User(
                full_name="Frank Staff",
                email="frank.staff@company.com",
                role=models.UserRole.manager,
                service="Operations"
            ),
            models.User(
                full_name="Grace Team Lead",
                email="grace.lead@company.com",
                role=models.UserRole.manager,
                service="HR Department"
            )
        ]
        
        # Create Shared Mailboxes
        mailbox1 = models.SharedMailbox(
            display_name="Sales Team",
            primary_smtp_address="sales@company.com",
            full_access_users="david.employee@company.com;eva.worker@company.com"
        )
        
        mailbox2 = models.SharedMailbox(
            display_name="Marketing Campaigns",
            primary_smtp_address="marketing@company.com", 
            full_access_users="eva.worker@company.com;grace.lead@company.com"
        )
        
        mailbox3 = models.SharedMailbox(
            display_name="Customer Support",
            primary_smtp_address="support@company.com",
            full_access_users="frank.staff@company.com"
        )
        
        mailbox4 = models.SharedMailbox(
            display_name="HR Recruitment",
            primary_smtp_address="recruitment@company.com",
            full_access_users="grace.lead@company.com;david.employee@company.com"
        )
        
        # Create TEMP Accounts for testing
        temp_accounts = [
            models.TempAccount(
                user_principal_name="temp001@company.com",
                display_name="Temporary Account 001",
                is_in_use=False
            ),
            models.TempAccount(
                user_principal_name="temp002@company.com",
                display_name="Temporary Account 002", 
                is_in_use=False
            ),
            models.TempAccount(
                user_principal_name="temp003@company.com",
                display_name="Temporary Account 003",
                is_in_use=True
            )
        ]
        
        # Create a sample Form Definition for testing
        sample_form = models.FormDefinition(
            name="New User Access Request",
            description="Standard form for requesting access to systems for new employees",
            schema={
                "title": "New User Access Request",
                "type": "object",
                "properties": {
                    "employee_name": {"type": "string", "title": "Employee Name"},
                    "department": {"type": "string", "title": "Department"},
                    "start_date": {"type": "string", "format": "date", "title": "Start Date"},
                    "required_systems": {
                        "type": "array",
                        "title": "Required Systems",
                        "items": {"type": "string", "enum": ["Email", "File Server", "CRM", "ERP"]}
                    }
                },
                "required": ["employee_name", "department", "start_date"]
            }
        )
        
        # Create a sample Walkthrough Template
        sample_walkthrough = models.WalkthroughTemplate(
            name="New Employee Onboarding",
            description="Complete checklist for setting up a new employee",
            steps={
                "steps": [
                    {"id": 1, "title": "Create AD Account", "completed": False},
                    {"id": 2, "title": "Assign Email", "completed": False}, 
                    {"id": 3, "title": "Setup File Access", "completed": False},
                    {"id": 4, "title": "Provide Equipment", "completed": False}
                ]
            },
            tools=["new_user_form", "temp_account_assignment"]
        )
        
        # Add all entities to the session
        db.add(admin_user)
        db.add(manager1)
        db.add(manager2)
        
        for user in regular_users:
            db.add(user)
            
        db.add(mailbox1)
        db.add(mailbox2)
        db.add(mailbox3)
        db.add(mailbox4)
        
        for temp_account in temp_accounts:
            db.add(temp_account)
            
        db.add(sample_form)
        db.add(sample_walkthrough)
        
        # Flush to assign IDs
        db.flush()
        
        # Now we can reference the auto-generated IDs
        # Set up mailbox permissions for managers
        # manager1 can manage Sales Team and Customer Support
        manager1.visible_mailboxes.extend([mailbox1, mailbox3])
        
        # manager2 can manage Marketing Campaigns and HR Recruitment  
        manager2.visible_mailboxes.extend([mailbox2, mailbox4])
        
        # Set the created_by_admin_id and suggested_walkthrough_id after flush
        sample_form.created_by_admin_id = admin_user.id
        
        # Create a sample request (this will use auto-increment ID)
        sample_request = models.Request(
            status=models.RequestStatus.pending,
            form_data={
                "employee_name": "John NewHire",
                "department": "Sales",
                "start_date": "2025-01-15",
                "required_systems": ["Email", "CRM"]
            },
            submitted_by_manager_id=manager1.id,  # Use the auto-generated ID
            form_definition_id=sample_form.id,
            assigned_temp_account_id=temp_accounts[0].id
        )
        
        db.add(sample_request)
        
        # Commit all changes
        db.commit()
        print("✅ Sample data inserted successfully.")
        print(f"   - Created {len([admin_user, manager1, manager2] + regular_users)} users")
        print(f"   - Created {len([mailbox1, mailbox2, mailbox3, mailbox4])} shared mailboxes") 
        print(f"   - Created {len(temp_accounts)} TEMP accounts")
        print(f"   - Set up mailbox permissions for 2 managers")
        print(f"   - Created 1 sample form definition and walkthrough")
        print(f"   - Created 1 sample request")
        
        print("\n🎉 Database initialization complete!")
        print("\n📋 Test Login Credentials:")
        print(f"   Admin: alice.admin@company.com (ID: {admin_user.id})")
        print(f"   Manager 1: bob.manager@company.com (ID: {manager1.id}) - manages Sales Team & Customer Support")
        print(f"   Manager 2: carol.manager@company.com (ID: {manager2.id}) - manages Marketing Campaigns & HR Recruitment")
        print("\n🧪 Testing Tips:")
        print(f"   1. Login as a manager (ID {manager1.id} or {manager2.id})")
        print("   2. Navigate to Tools → Manage Mailboxes")
        print("   3. You should see their assigned mailboxes with current users")
        print("   4. Try searching for users and adding/removing them")
        print("   5. Submit a request to test the full workflow")
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to orchestrate the database initialization."""
    print("--- Starting IT Provisioning Platform Database Initialization ---")
    
    try:
        engine = get_db_connection()
        if engine is None: 
            return

        drop_and_create_tables(engine)
        insert_sample_data(engine)

    except Exception as error:
        print(f"\n❌ A critical error occurred: {error}")

    print("\n--- Initialization Script Finished ---")

if __name__ == "__main__":
    main()
