from flask import render_template
import subprocess
import signal
import os

def handle_init(app):
    # Function to kill a process running on a specific port
    def kill_process_on_port(port):
        # Run a shell command to find the process using the specified port
        result = subprocess.run(
            f"netstat -ano | findstr :{port}",
            shell=True,
            capture_output=True,
            text=True
        )
        # Split the output into lines
        lines = result.stdout.splitlines()
        # Loop through the lines to find and kill the process
        for line in lines:
            parts = line.split()  # Split the line into parts
            pid = parts[-1]  # Get the process ID (PID)
            if pid:
                # Kill the process using the PID
                os.kill(int(pid), signal.SIGTERM)

    # Renders the face detection page with player data.
    @app.route('/')
    def home():
        # Render the index (home) page
        return render_template('index.html')
