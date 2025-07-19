# IT Provisioning Platform

A modern IT access request management system built with FastAPI and SvelteKit, featuring real-time admin dashboard and dynamic form generation.

## 🚀 Features

### Core Functionality
- **Dynamic Form Engine** - Create and manage custom request forms
- **Request Submission Workflow** - Two-step process for managers to submit access requests
- **Real-Time Admin Dashboard** - Live updates using WebSockets for request monitoring
- **Status Management** - Track requests through pending, in-progress, completed, and rejected states
- **Multi-Language Support** - English and French localization

### Technical Highlights
- **Backend**: FastAPI with PostgreSQL, SQLAlchemy ORM, WebSocket support
- **Frontend**: SvelteKit with reactive UI components
- **Real-Time**: WebSocket-based live updates
- **Database**: PostgreSQL with JSONB for flexible form data storage
- **Containerized**: Docker Compose for easy deployment

## 🏗️ Architecture

```
├── backend/                 # FastAPI Application
│   ├── main.py             # API endpoints and WebSocket handling
│   ├── models.py           # Database models (User, FormDefinition, Request)
│   ├── schemas.py          # Pydantic schemas for API validation
│   ├── crud.py             # Database operations
│   ├── database.py         # Database configuration
│   ├── ws_manager.py       # WebSocket connection manager
│   └── requirements.txt    # Python dependencies
├── frontend/               # SvelteKit Application
│   ├── src/
│   │   ├── routes/         # Page routes
│   │   │   ├── admin/      # Admin dashboard and form management
│   │   │   ├── requests/   # Request submission and viewing
│   │   │   └── users/      # User management
│   │   ├── lib/            # Shared utilities (i18n)
│   │   └── locales/        # Translation files
│   └── package.json        # Node.js dependencies
└── docker-compose.yml      # Container orchestration
```

## 🚦 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd it-provisioning-platform
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development

For development with hot reloading:

```bash
# Start all services
docker-compose up --build

# Or start services individually
docker-compose up db backend  # Database and API
docker-compose up frontend    # Frontend only
```

## 📋 Usage

### For Managers
1. Navigate to "Submit a New Request"
2. Select a form template
3. Fill out the required fields
4. Submit the request

### For Administrators
1. Access the "Admin: Dashboard" for real-time request monitoring
2. Use "Admin: Forms" to create and manage form templates
3. Update request statuses directly from the dashboard

## 🔧 API Endpoints

### Core Endpoints
- `GET /users/` - List all users
- `POST /users/` - Create new user
- `GET /form-definitions/` - List form templates
- `POST /form-definitions/` - Create form template
- `GET /requests/` - List all requests
- `POST /requests/` - Submit new request
- `PUT /requests/{id}/status` - Update request status

### WebSocket
- `WS /ws/admin-dashboard` - Real-time admin updates

## 🗄️ Database Schema

### Users
- **id**: Primary key
- **full_name**: User's full name
- **email**: Email address (unique)
- **role**: admin | manager

### Form Definitions
- **id**: Primary key
- **name**: Form template name
- **description**: Form description
- **schema**: JSONB schema defining form fields
- **created_by_admin_id**: Foreign key to admin user

### Requests
- **id**: Primary key
- **form_definition_id**: Foreign key to form template
- **submitted_by_manager_id**: Foreign key to manager user
- **form_data**: JSONB data submitted by user
- **status**: pending | in_progress | completed | rejected

## 🌍 Internationalization

The application supports multiple languages:
- English (default)
- French

Language can be switched using the language selector in the navigation bar.

## 🔒 Security Notes

- In production, implement proper authentication and authorization
- The current implementation uses hardcoded manager lookup for demonstration
- Consider adding JWT tokens or session-based authentication
- Implement role-based access control for API endpoints

## 🚀 Deployment

### Production Deployment
1. Set environment variables for production database
2. Configure CORS origins for your domain
3. Use a reverse proxy (nginx) for SSL termination
4. Consider using a managed PostgreSQL service

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `FRONTEND_URL`: Frontend URL for CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at http://localhost:8000/docs
- Review the WebSocket implementation in `backend/ws_manager.py`

---

Built with ❤️ using FastAPI and SvelteKit
