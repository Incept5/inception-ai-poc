import os

bind = "0.0.0.0:9871"
workers = 1
threads = 2

# Set reload based on the ENABLE_HOT_RELOAD environment variable
reload = os.environ.get('ENABLE_HOT_RELOAD', 'false').lower() == 'true'

if reload:
    reload_extra_files = ["/app"]

def when_ready(server):
    print("Server is ready. Development server: http://localhost:9871")
    print(f"Current directory: {os.getcwd()}")
    print(f"Current directory contents: {os.listdir('.')}")
    print(f"Hot reload is {'enabled' if reload else 'disabled'}")

def on_exit(server):
    print("Server is shutting down")