# Welcome to OSOM.Codex sandbox edition!
# Please open terminal and follow setup steps below to make your project up and running in minutes.


# Libraries setup.
# lib: Setup OSOM.js GIT submodule.
git submodule init
git submodule update


# lib: Install NPM packages for frontend development.
$ mkdir -p ./lib/node_modules
$ npm install --prefix ./lib

# NOTE: Use the same command for installation of different NPM packages.
# $ npm install --prefix ./lib {PACKAGE_NAME}


# backend: Setup Python virtual environment for backend libraries.
$ python3 -m venv .venv

# backend: Activate virtual environment so you could install required backend packages.
$ source .venv/bin/activate

# backend: Install packages required into virtual environment.
(.venv)$ pip install -r requirements.txt

# NOTE: If mysqlclient installation fails, install: 
# apt-get install libmariadb-dev


# backend: Initialize and apply DB migrations (don't forget to cd into 'dev' folder first).
(.venv)$ cd ./dev
(.venv)$ python manage.py makemigrations
(.venv)$ python manage.py migrate

# Create superuser
# U: admin@test.indeform.com
# P: SeCure99#
(.venv)$ python manage.py createsuperuser


# === Below are some Utility scripts (make sure to make them executable) and commands to start and initialize projects faster. ===

# Django/NPM startup script (double click "run.sh" if marked as "executable").
# Note: to mark executable: Mouse Right Click -> Properties -> Permissions -> Allow executing file as program.
# Ctrl+Click http://127.0.0.1:8000/ in Terminal
bash run.sh


# Automate localization (*.po -> *.mo) building. (double click "localize.sh" if marked as "executable")
bash localize.sh


# Create your own module:
(.venv)$ python ../manage.py startapp mymodulename


# Good luck!
