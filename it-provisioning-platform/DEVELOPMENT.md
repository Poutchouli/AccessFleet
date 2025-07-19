# Development Guide

## Development Setup

### Prerequisites
- Docker Desktop
- Git
- VS Code (recommended)

### Local Development

1. **Clone and start services**
   ```bash
   git clone <repository>
   cd it-provisioning-platform
   docker-compose up --build
   ```

2. **Access services**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Database: localhost:5432

### Code Structure

#### Backend (`./backend/`)
- `main.py` - FastAPI app with all endpoints and WebSocket handling
- `models.py` - SQLAlchemy database models
- `schemas.py` - Pydantic validation schemas
- `crud.py` - Database operations
- `ws_manager.py` - WebSocket connection management

#### Frontend (`./frontend/src/`)
- `routes/` - SvelteKit pages and layouts
- `lib/` - Shared utilities and i18n
- `locales/` - Translation files

### Making Changes

#### Backend Changes
1. Edit files in `./backend/`
2. Changes auto-reload with uvicorn
3. Test at http://localhost:8000/docs

#### Frontend Changes
1. Edit files in `./frontend/src/`
2. Vite provides hot module reloading
3. View changes at http://localhost:5173

#### Database Changes
1. Modify models in `models.py`
2. Restart backend container: `docker-compose restart backend`
3. Database schema updates automatically with `create_all()`

### Testing

#### Manual Testing
1. Create form templates at `/admin/forms`
2. Submit requests at `/requests/new`
3. Monitor real-time updates at `/admin/dashboard`

#### API Testing
- Use FastAPI docs at http://localhost:8000/docs
- Test WebSocket connection with browser dev tools

### Common Tasks

#### Add New API Endpoint
1. Add route in `main.py`
2. Add schema in `schemas.py` if needed
3. Add CRUD operation in `crud.py` if needed

#### Add New Page
1. Create `.svelte` file in `frontend/src/routes/`
2. Add navigation link in `+layout.svelte`
3. Add translations in locale files

#### Add New Database Model
1. Define model in `models.py`
2. Add corresponding schemas in `schemas.py`
3. Add CRUD operations in `crud.py`
4. Restart backend to create tables

### Debugging

#### Backend Logs
```bash
docker-compose logs backend -f
```

#### Frontend Logs
```bash
docker-compose logs frontend -f
```

#### Database Access
```bash
docker-compose exec db psql -U admin -d provisioning_db
```

### Production Considerations

1. Change database passwords in `docker-compose.yml`
2. Set proper CORS origins in `main.py`
3. Add authentication middleware
4. Use environment variables for secrets
5. Add proper logging
6. Implement health checks
7. Use a reverse proxy (nginx)
8. Set up SSL certificates
