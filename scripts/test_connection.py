"""Test database connection and diagnose issues."""
import os
import sys

# Set DATABASE_URL if not already set
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "mysql://root:RXXtpcEhPqTRhqzOuXvWQCedlaVWTjIn@maglev.proxy.rlwy.net:29969/railway"

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)

# Test 1: Direct pymysql connection
print("\n[TEST 1] Direct pymysql connection...")
try:
    import pymysql
    conn = pymysql.connect(
        host='maglev.proxy.rlwy.net',
        port=29969,
        user='root',
        password='RXXtpcEhPqTRhqzOuXvWQCedlaVWTjIn',
        database='railway',
        connect_timeout=30,
        read_timeout=60,
        write_timeout=60,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1 as test')
    result = cursor.fetchone()
    print(f"✓ Direct connection OK: {result}")
    
    # Check server variables
    cursor.execute('SELECT @@version, @@wait_timeout, @@interactive_timeout, @@max_allowed_packet')
    server_info = cursor.fetchone()
    print(f"  MySQL Version: {server_info[0]}")
    print(f"  wait_timeout: {server_info[1]}s")
    print(f"  interactive_timeout: {server_info[2]}s")
    print(f"  max_allowed_packet: {server_info[3]} bytes")
    
    conn.close()
except Exception as e:
    print(f"✗ Direct connection failed: {e}")
    sys.exit(1)

# Test 2: SQLAlchemy engine connection
print("\n[TEST 2] SQLAlchemy engine connection...")
try:
    from shared.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        print(f"✓ SQLAlchemy connection OK: {result.scalar()}")
except Exception as e:
    print(f"✗ SQLAlchemy connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Insert and query test
print("\n[TEST 3] Insert and query test...")
try:
    from shared.database import SessionLocal
    from plant.infrastructure.models import PlantModel
    
    session = SessionLocal()
    
    # Try to insert a test record
    test_plant = PlantModel(
        device_id='test-device-diagnostic',
        temperature=25.5,
        humidity=60.0,
        light=500,
        soil_humidity=45
    )
    
    session.add(test_plant)
    session.commit()
    print(f"✓ Insert successful: ID={test_plant.id}")
    
    # Query it back
    queried = session.query(PlantModel).filter_by(device_id='test-device-diagnostic').first()
    if queried:
        print(f"✓ Query successful: {queried.device_id}, temp={queried.temperature}")
    
    # Clean up
    session.delete(queried)
    session.commit()
    session.close()
    print("✓ Cleanup successful")
    
except Exception as e:
    print(f"✗ Insert/query test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
