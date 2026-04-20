import sys
import os

with open("/tmp/mcp_debug.log", "a") as f:
    f.write("Wrapper called\n")
    f.write(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}\n")
    f.write(f"PATH: {os.environ.get('PATH')}\n")
    f.flush()
    try:
        import aws_batch_mcp
        f.write("Successfully imported\n")
    except Exception as e:
        f.write(f"Exception: {e}\n")
