# Database Initialization Guide

This guide explains how to initialize the IT Provisioning Platform database with sample data for testing.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start the database:**
   ```bash
   docker-compose up db -d
   ```

2. **Wait for database to be ready (about 10-15 seconds)**

3. **Run the initialization script:**
   ```bash
   docker-compose exec backend python init_database.py
   ```

### Option 2: Direct Python Execution

1. **Ensure PostgreSQL is running** (either via Docker or locally)

2. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your database connection details
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Run initialization:**
   ```bash
   cd backend
   python init_database.py
   ```

## What Gets Created

### Users
- **Admin:** alice.admin@company.com (ID: 1)
- **Manager 1:** bob.manager@company.com (ID: 2) 
- **Manager 2:** carol.manager@company.com (ID: 3)
- **4 Regular Users:** david.employee@company.com, eva.worker@company.com, frank.staff@company.com, grace.lead@company.com

### Shared Mailboxes
- **Sales Team** (sales@company.com) - Managed by Bob Manager
- **Marketing Campaigns** (marketing@company.com) - Managed by Carol Manager  
- **Customer Support** (support@company.com) - Managed by Bob Manager
- **HR Recruitment** (recruitment@company.com) - Managed by Carol Manager

### Sample Data
- 3 TEMP accounts (for testing temporary account assignment)
- 1 Form definition (New User Access Request)
- 1 Walkthrough template (New Employee Onboarding)
- 1 Sample request (submitted by Bob Manager)

## Testing the Mailbox Management Interface

1. **Start the application:**
   ```bash
   docker-compose up
   ```

2. **Open the frontend:** http://localhost:5173

3. **Login as a manager:**
   - Use the login dropdown
   - Select "Manager User (ID 2)" or "Manager User (ID 3)"

4. **Navigate to mailbox management:**
   - Click "🛠️ Tools" → "📧 Manage Mailboxes"

5. **Test the interface:**
   - You should see 2 mailboxes assigned to each manager
   - Each mailbox shows current users with full access
   - Try searching for users: "david", "eva", "frank", "grace"
   - Add/remove users and submit requests

## Resetting the Database

To completely reset and reinitialize:

```bash
# Stop all services
docker-compose down

# Remove the database volume (this deletes all data!)
docker volume rm it-provisioning-platform_postgres-data

# Restart and reinitialize
docker-compose up db -d
# Wait 10-15 seconds
docker-compose exec backend python init_database.py
```

## Environment Configuration

The script uses these environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Enable debug mode (optional)

For Docker Compose, these are automatically configured. For local development, copy `.env.example` to `.env` and adjust as needed.

## Troubleshooting

### "Connection refused" errors
- Make sure PostgreSQL is running and accepting connections
- Check that the DATABASE_URL is correct
- For Docker: ensure the `db` service is healthy before running init

### "Permission denied" errors  
- Check PostgreSQL user permissions
- Ensure the database exists and is accessible

### "Module not found" errors
- Make sure you're in the backend directory
- Install requirements: `pip install -r requirements.txt`
- Set PYTHONPATH if needed: `export PYTHONPATH=/path/to/backend`
