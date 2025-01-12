from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create shared extensions
db = SQLAlchemy()
login_manager = LoginManager()
