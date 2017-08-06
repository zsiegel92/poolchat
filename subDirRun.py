import subprocess
print("running a subprocess!")
subprocess.call(["python","worker.py"],cwd="src")
