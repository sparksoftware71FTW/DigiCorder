# DigiCorder
- Enhance/replace recorders in the RSU
- Possibly host a ORM management app

# Dev Environment Setup Instructions:
*Note: these instructions are Windows-centric, but almost identical for Linux/MacOS.*

1. Install python and setup virtual environment
   - Download and install python 3.10 on your machine
   - Make a directory for the project (something like ..\Digicorder\)
   - Open a terminal in the project directory and run the following commands:
   > `python -m venv env1`

   > `.\env1\Scripts\activate` 
   - *Note*: you may need to allow scripts to run on your windows machine for this to run, see https:/go.microsoft.com/fwlink/?LinkID=135170
   - Possibly run a powershell command like:
   > `Set-ExecutionPolicy -ExecutionPolicy unrestricted -scope CurrentUser`
   - before reattempting to run the `.\env1\Scripts\activate` script again
   - Now, once the virtual environment is running and you see the `(env1)` or equivalent on the current line in your terminal,  

2. Clone the Digicorder repo into prefered directory, and use `pip` to install the dependencies in `requirements.txt`. 
   - Recommend cloning the repo right *next to* where you installed your virtual environment `..\Digicorder\` - though NOT in the `..\Digicorder\env1` directory... This will cause git to track over a thousand unnecessary virtual environment files.
   - Once cloned, `cd` into the repo directory (`..\Digicorder\Digicorder` if you've been following along exactly so far and you used Git default naming)
   - Now run the command below to install the project's dependencies:
   > `pip install -r requirements.txt`

3. Setup the database, and create an admin user
   - Download postgresql v14.4 from https://www.postgresql.org/download/
   - Run the installer and restart the system if required. Be sure to re-activate your python virtual environment aftwards though...
   - Next, run:
   > `python manage.py makemigrations`
   - This leverages Django's builtin database controll modules to setup everying needed to layout our project's database schemas
   - Finally, for the moment of truth, run:
   > `python manage.py migrate`
   - This will actually create database tables for Django's builtin data as well as all of the installed apps' `models.py` classes.
   - from the `..\Digicorder\Digicorder\DigicorderServer\` directory, run the command below to create an admin account called `admin`:
   > `python manage.py createsuperuser`
   - Follow the instructions that populate. Email and other fields are not strictly necessary.

4.  Run the server!
	> `python manage.py runserver`

5. Checkout the admin site in your browser, and login with the credentials you specified earlier `http://localhost:8000/admin/`.
