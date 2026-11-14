
import sys
import platform
import subprocess

print("=" * 50)
print("PYTHON INSTALLATION VERIFICATION")
print("=" * 50)

# 1. Python version
print("\n1. Python Version:")
print(sys.version)

# 2. Python installation location
print("\n2. Python Executable Location:")
print(sys.executable)

# 3. Operating system
print("\n3. Operating System:")
print(platform.system())
print(platform.platform())

# 4. Processor architecture
print("\n4. Processor Architecture:")
print(platform.machine())

# 5. Python implementation
print("\n5. Python Implementation:")
print(platform.python_implementation())

# 6. Check pip availability
print("\n6. Pip Installation:")

try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "--version"],
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout.strip())

except subprocess.CalledProcessError:
    print("Pip is not available for this Python installation.")

# 7. Basic Python execution test
print("\n7. Basic Python Execution Test:")

a = 10
b = 20
result = a + b

print(f"10 + 20 = {result}")

if result == 30:
    print("Python execution: SUCCESS")
else:
    print("Python execution: FAILED")

# 8. Standard library import test
print("\n8. Standard Library Import Test:")

try:
    import os
    import csv
    import json
    import math
    import statistics

    print("All standard library imports successful.")

except ImportError as error:
    print(f"Import error: {error}")

print("\n" + "=" * 50)
print("VERIFICATION COMPLETED")
print("=" * 50)
