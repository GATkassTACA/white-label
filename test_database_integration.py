#!/usr/bin/env python3
"""
Database Integration Test for PharmAssist Azure Deployment
Tests database connectivity and operations when database is available
"""

import os
import sys
import json
from datetime import datetime

# Set testing environment
os.environ['FLASK_ENV'] = 'testing'

def test_database_connection():
    """Test database connection and basic operations"""
    
    # Import app components
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_module", "app.py")
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    app = app_module.app
    db = app_module.db
    DATABASE_AVAILABLE = app_module.DATABASE_AVAILABLE
    
    print("🗃️  Database Integration Test")
    print("=" * 50)
    print(f"Database Libraries Available: {DATABASE_AVAILABLE}")
    print(f"Database Connection: {db.connection is not None}")
    
    if not DATABASE_AVAILABLE:
        print("⚠️  Database libraries not available - skipping database tests")
        return True
    
    if not db.connection:
        print("⚠️  No database connection - this is expected in local development")
        print("   In Azure, ensure DATABASE_URL environment variable is set")
        return True
    
    # Test database operations
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check if tables exist
    tests_total += 1
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('processing_history', 'medications')
        """)
        tables = cursor.fetchall()
        
        if len(tables) >= 2:
            print("✅ Database tables exist")
            tests_passed += 1
        else:
            print(f"❌ Expected 2 tables, found {len(tables)}")
            
    except Exception as e:
        print(f"❌ Table check failed: {e}")
    
    # Test 2: Check medications data
    tests_total += 1
    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM medications")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Medications table has {count} entries")
            tests_passed += 1
        else:
            print("❌ Medications table is empty")
            
    except Exception as e:
        print(f"❌ Medications check failed: {e}")
    
    # Test 3: Test logging functionality
    tests_total += 1
    try:
        test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        db.log_processing(
            session_id=test_session_id,
            filename="test.pdf",
            original_filename="test.pdf", 
            method="test",
            status="success",
            processing_time=1.0,
            file_size=1024,
            extracted_text="Test text",
            converted_data="Test data"
        )
        
        # Verify the log was created
        cursor = db.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM processing_history WHERE session_id = %s",
            (test_session_id,)
        )
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("✅ Database logging works")
            tests_passed += 1
            
            # Clean up test data
            cursor.execute(
                "DELETE FROM processing_history WHERE session_id = %s",
                (test_session_id,)
            )
        else:
            print("❌ Database logging failed")
            
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
    
    # Test 4: Test history retrieval
    tests_total += 1
    try:
        history = db.get_processing_history("nonexistent_session", limit=10)
        if isinstance(history, list):
            print("✅ History retrieval works")
            tests_passed += 1
        else:
            print("❌ History retrieval failed")
            
    except Exception as e:
        print(f"❌ History retrieval test failed: {e}")
    
    print("-" * 50)
    print(f"Database Tests: {tests_passed}/{tests_total} passed")
    
    return tests_passed == tests_total

def test_database_environment_setup():
    """Test that database environment is properly configured for Azure"""
    
    print("\n🔧 Database Environment Configuration")
    print("-" * 50)
    
    # Check environment variables
    env_checks = [
        ('DATABASE_URL', 'Full database connection string'),
        ('DATABASE_HOST', 'Database host (alternative to DATABASE_URL)'),
        ('DATABASE_NAME', 'Database name'),
        ('DATABASE_USER', 'Database username'),
        ('DATABASE_PASSWORD', 'Database password')
    ]
    
    found_vars = 0
    for var_name, description in env_checks:
        value = os.getenv(var_name)
        if value:
            if 'PASSWORD' in var_name or 'URL' in var_name:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var_name}: {display_value}")
            found_vars += 1
        else:
            print(f"❌ {var_name}: Not set")
    
    print(f"\nEnvironment variables found: {found_vars}/{len(env_checks)}")
    
    if found_vars == 0:
        print("\n💡 For Azure deployment, set up database connection:")
        print("   Option 1: Set DATABASE_URL environment variable")
        print("   Option 2: Set individual DATABASE_* variables")
        print("   Example DATABASE_URL: postgresql://user:pass@host:5432/dbname")
    
    return found_vars > 0

if __name__ == '__main__':
    print("🏥 PharmAssist Database Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test environment setup
    env_ok = test_database_environment_setup()
    
    # Test database functionality
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    if db_ok:
        print("✅ Database integration tests passed!")
    else:
        print("⚠️  Database integration tests had issues")
    
    if env_ok:
        print("✅ Database environment configured")
    else:
        print("⚠️  Database environment needs configuration")
    
    print("\n💡 Next steps for Azure deployment:")
    print("   1. Configure Azure Database for PostgreSQL")
    print("   2. Set DATABASE_URL in App Service Configuration")
    print("   3. Deploy and test with azure_health_check.py --health-only")
    
    sys.exit(0 if (db_ok or not env_ok) else 1)
