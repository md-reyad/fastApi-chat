import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

def test_connection():
    """Test the database connection with detailed error reporting."""
    print("Testing PostgreSQL connection...")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    
    try:
        # Create database URL
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            
        print("\n✅ Connection successful!")
        print(f"PostgreSQL version: {version}")
        return True
        
    except ImportError as e:
        print(f"\n❌ Module import error: {e}")
        print("Make sure you have installed psycopg2-binary with: pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        
        # Provide more specific guidance based on the error
        error_str = str(e).lower()
        if "could not connect to server" in error_str:
            print("\nPossible solutions:")
            print("1. Make sure PostgreSQL is running")
            print("2. Check if the host and port are correct")
            print("3. Verify that PostgreSQL is accepting connections")
        elif "password authentication failed" in error_str:
            print("\nPossible solutions:")
            print("1. Check if the username and password are correct")
            print("2. Verify that the user has permission to connect")
        elif "database" in error_str and "does not exist" in error_str:
            print("\nPossible solutions:")
            print(f"1. Create the database with: CREATE DATABASE {DB_NAME};")
            print("2. Check if the database name is spelled correctly")
        
        return False

if __name__ == "__main__":
    test_connection() 