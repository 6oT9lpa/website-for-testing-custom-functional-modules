# Flask Application with Docker

This is a Flask web application that allows users to create, manage, and execute custom functions. It includes user authentication, role-based access control, and integration with AI chat functionality.

## Features

- User registration and authentication
- Role-based permissions (user/admin)
- Function creation and execution (with code upload)
- Admin panel for user and function management
- Real-time chat with AI integration
- Rate limiting
- File uploads

## Security Warning

⚠️ **IMPORTANT**: This application executes user-uploaded Python code dynamically. This is extremely dangerous in production environments as it can lead to arbitrary code execution vulnerabilities. In a real-world scenario, you should:

- Use a sandboxed environment (e.g., Docker containers with restricted permissions)
- Implement code analysis and whitelisting
- Restrict allowed modules and functions
- Add proper input validation and sanitization

The current implementation includes basic warnings but is not production-ready for security.

## Prerequisites

- Docker and Docker Compose
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Copy the environment file and configure it:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your actual values:
   ```env
   SECRET_KEY=your-very-secure-secret-key-here
   SQLALCHEMY_DATABASE_URI=mysql://user:password@db:3306/project
   REDIS_URL=redis://redis:6379/0
   MYSQL_ROOT_PASSWORD=your-secure-root-password
   MYSQL_DATABASE=project
   MYSQL_USER=user
   MYSQL_PASSWORD=your-secure-password
   ```

3. Build and run the application:
   ```bash
   docker-compose up --build
   ```

4. The application will be available at `http://localhost:5000`

## Services

- **app**: Flask application (Python 3.11)
- **db**: MariaDB 10.11 database
- **redis**: Redis 7 for caching and rate limiting

## Development

To run in development mode:

1. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (see .env.example)

3. Run the application:
   ```bash
   python run.py
   ```

## Database Migrations

The application uses Flask-Migrate for database migrations. To create and apply migrations:

```bash
# Inside the container
flask db init
flask db migrate
flask db upgrade
```

Or use docker-compose exec:

```bash
docker-compose exec app flask db upgrade
```

## API Endpoints

- `/` - Home page
- `/auth` - Authentication page
- `/profile` - User profile
- `/admin-panel` - Admin panel (admin only)
- `/api/function` - Function management
- `/api/function/<id>/execute` - Execute function

## File Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── config.py
├── limiter.py
├── main.py
├── run.py
├── __init__.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
└── uploads/
    └── func_models/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | change-this-in-production |
| SQLALCHEMY_DATABASE_URI | Database connection string | mysql://user:password@db:3306/project |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| MYSQL_ROOT_PASSWORD | MySQL root password | - |
| MYSQL_DATABASE | MySQL database name | project |
| MYSQL_USER | MySQL user | user |
| MYSQL_PASSWORD | MySQL password | password |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]