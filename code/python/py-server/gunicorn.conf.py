import os

bind = "0.0.0.0:5010"
workers = 1
threads = 2
reload = True
reload_extra_files = ["/app"]

def when_ready(server):
    print("Server is ready. Development server: http://localhost:5010")
    print(f"Current directory: {os.getcwd()}")
    print(f"Current directory contents: {os.listdir('.')}")

def on_exit(server):
    print("Server is shutting down")