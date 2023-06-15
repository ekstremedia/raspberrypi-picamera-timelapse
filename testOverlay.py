#!/usr/bin/python
import subprocess

# Set the command as a list of strings
command = [
    'python', 
    'new_overlay.py', 
    '--file', 
    '/var/www/html/testimg.jpg', 
    '--test'
]

# Use subprocess to run the command
subprocess.run(command)