# 

# Requirements
To install all requirements, use the following snippet after installing python on your machine.

    pip install -r requirements.txt

Or just use:

    pip install *pkg_name*


# Usage

On Windows:

Open a console on the Mange directory.

If if the first time executing the project run setup_dev_windows.py to install a virtual environment with the dependencies
of the project.

To run the database server
Activate the virtual environment calling activate.bat
Run w.py with the corresponding arguments.
Exmples:
	python w.py migrate    To create a new database
	python w.py runserver  To start the database server

# Testing

