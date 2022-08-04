# DigiCorder
- Enhance/replace recorders in the RSU
- Possibly host a ORM management app

# Dev environment setup instructions:
1. Install python and setup virtual environment
   - Download and install python 3.10 on your machine
   - Make a directory for the project (something like ..\Digicorder\)
   - Open a terminal in the project directory and run the following commands:
   > python -m venv env1
   > .\env1\Scripts\activate.bat **Note: you may need to allow scripts to run on your windows machine for this to run**
   > pip install -r requirements.txt

2. Clone Digicorder folder into prefered directory. We recommend doing this right next to where you installed your virtual environment '..\Digicorder\' - though NOT in the '..\Digicorder\env1' directory... This will cause git to track several thousand unnecessaryt virtual environment files.

3. Setup the database...
	$sudo apt-get install python-dev libpq-dev postgresql postgresql-contrib
	$sudo -su postgres
	$psql
	=>CREATE DATABASE x;
	=>CREATE USER server WITH PASSWORD 'server';
	=>ALTER ROLE server SET client_encoding TO 'utf8';
	=>ALTER ROLE server SET default_transaction_isolation TO 'read committed';
	=>ALTER ROLE server SET timezone TO 'UTC';
	=>GRANT ALL PRIVILEGES ON DATABASE x TO server;
	=>\q
	$exit

4. Activate virtual environment and make database migrations:
	$cd <parent_directories>/Digicorder/Autocorder
	$source bin/activate
	$python3 manage.py makemigrations
	$python3 manage.py migrate

5. Run the server!
	$python3 manage.py runserver
