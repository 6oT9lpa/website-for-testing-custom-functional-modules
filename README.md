# Flask Application

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

- Use a sandboxed environment (e.g., isolated execution environments or restricted permissions)
- Implement code analysis and whitelisting
- Restrict allowed modules and functions
- Add proper input validation and sanitization

The current implementation includes basic warnings but is not production-ready for security.

## Prerequisites

- Python 3.11+
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables (optional, defaults are in config.py):
   ```bash
   export SECRET_KEY=your-very-secure-secret-key-here
   export SQLALCHEMY_DATABASE_URI=sqlite:///project.db
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. The application will be available at `http://localhost:8000`

## Development

To run in development mode:

1. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (optional, defaults are in config.py)

3. Run the application:
   ```bash
   python run.py
   ```

## Database Migrations

The application uses Flask-Migrate for database migrations. To create and apply migrations:

```bash
flask db init
flask db migrate
flask db upgrade
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
├── __init__.py
├── config.py
├── main.py
├── models.py
├── README.md
├── requirements.txt
├── run.py
├── .gitignore
├── instance/
│   └── project.db
├── routes/
│   ├── api.py
│   ├── auth.py
│   ├── functions.py
│   └── users.py
├── static/
│   ├── css/
│   │   ├── adminpanel-style.css
│   │   ├── function-editor.css
│   │   ├── index-style.css
│   │   ├── profile-style.css
│   │   └── root-style.css
│   └── js/
│       ├── admin-script.js
│       ├── function-editor.js
│       ├── index-script.js
│       ├── profile-script.js
│       ├── root-script.js
│       └── modules/
│           ├── function-executor.js
│           ├── function-selector.js
│           └── ui-helpers.js
├── templates/
│   ├── admin_panel.html
│   ├── function_editor.html
│   ├── index.html
│   └── profile.html
└── utils/
    └── code_execution.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | change-this-in-production |
| SQLALCHEMY_DATABASE_URI | Database connection string | sqlite:///project.db |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
