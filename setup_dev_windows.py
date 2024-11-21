import subprocess
import os

print("Setting up dev env...")
subprocess.run(["python","-m","venv","env"])

#Set environment variables for project
print("Setting up environment variables ...")
base_dir = os.path.dirname(__file__)

env_vars = [f"set PYTHONPATH={os.path.join(base_dir,"src")}",
            f"set FLASK_APP={os.path.join(base_dir,"src","mange","server.py")}",
            "set FLASK_DEBUG=1",
            "set MANGE_SETTINGS_MODULE=mange.conf.dev"
           ]

#Append environment variables to environment activation script
with open(os.path.join(base_dir,"env","Scripts","activate.bat"),"a") as activationScript:
    activationScript.write("\n")
    for var in env_vars:
        activationScript.write(var + "\n")
print("Environment variables added.")
print("Activating environment ...")
subprocess.run([f"{os.path.join(base_dir,"env","Scripts","activate.bat")}"])
print("Environment activated... installing dependencies ...")
pip_exe = f"{os.path.join(base_dir,"env","Scripts","pip.exe")}"
subprocess.run([pip_exe,"install","-r","requirements.txt"])
subprocess.run([pip_exe,"install","-r","requirements.dev.txt"])
print("Job done.")