# tango_recruitment_task
Tango recruitment task - calendar app

RUN ON DOCKER(UNTESTED DUE TO WSL PROBLEMS ON MY MACHINE)
docker build -t calendar_app .
docker run -it -p 8000:8000 calendar_app

RUN ON PIPENV
requires Python 3.12
pipenv shell
pip install -r requirements.txt
python3 manage.py runserver

