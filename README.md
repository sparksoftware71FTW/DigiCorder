# DigiCorder
- Enhance/replace recorders in the RSU
- Possibly integrate additional hardware/software to assist with other duties as well!

# Dev Environment Setup Instructions:
*Note: these instructions are Windows-centric, but they are almost identical for Linux/MacOS.*

1. Install python and setup virtual environment
   - Download and install python 3.10.5 on your machine
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
   - When you have a terminal open in the target directory run `git clone https://github.com/Gmunster33/DigiCorder.git`
     - Note: if you do not have `Git` installed on your machine, download and run the installer here: https://git-scm.com/downloads
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

4. Install `Docker` and run a stripped down virtual machine with a Redis RAM database to support our application's asynchronous features with fast, in-RAM queing
   - Download from https://www.docker.com/
   - Run the installation executable, and when complete, run the command below in a terminal: 
   > `docker run -p 6379:6379 -d redis:5`
   - This will download and instantiate the Redis 5 database VM that our app will hook into via localhost port 6379 mapped to the VM's port 6379.
   - This port will need to change to 80 when deployed most likely due to common routing rules (especially if the VM is on a different machine altogether than the one our app is running on).
   - Either use Docker's desktop app or its proprietary terminal commands to shut down, save, or restart this VM as needed going forward.

5. **IMPORTANT:** by default, the server will pull ADSB data from https://rapidapi.com/adsbx/api/adsbexchange-com1/ every second. This costs real money for every data pull.
   - To disable the ADSB data stream, (with the server not running) run the powershell command `$env:ENABLE_ADSB='False'` in the same terminal window that you will run the server from.
   - To re-enable it, just set this environment variable to `'True'` (again, when the server is shut down).

6. Run the server! Just navigate to the `..\Digicorder\Digicorder\DigicorderServer\` directory and punch in the commands below into a terminal: 
	> `python manage.py runserver`
   
7. Visit `http://localhost:8000/AutoRecorder/` in the browser of your choice, login, and enjoy!
8. Also checkout the admin site in your browser, and login with the credentials you specified earlier `http://localhost:8000/admin/`. You can then manage the permissions of any other user that registers an account on the site. By default, a newly registered account cannot see any of the dashboard or Form 355 pages. An admin must mark each account with `staff` permissions before users can see or do anything useful.
