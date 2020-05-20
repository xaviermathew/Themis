PROJECT_DIR=`pwd`
VIRTUAL_ENV_ROOT=$(HOME)/virtual_env
VIRTUAL_ENV_NAME=polidicks
CRONTAB_FILE=config/crontab/crontab

link_manage_py:
	ln -s $(PROJECT_DIR)/manage.py $(VIRTUAL_ENV_ROOT)/$(VIRTUAL_ENV_NAME)/bin/manage.py
make_dirs:
	mkdir -p $(PROJECT_DIR)/logs/
	mkdir -p $(PROJECT_DIR)/logs/celery/
	mkdir -p $(PROJECT_DIR)/pids/
	mkdir -p $(PROJECT_DIR)/pids/celery/
	mkdir -p $(PROJECT_DIR)/static/
pull:
	git pull
update_cron:
	crontab $(CRONTAB_FILE)
	sudo service cron restart
update_systemd:
	sudo cp config/systemd/* /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl restart gunicorn
	sudo systemctl restart celery
static:
	# ./manage.py collectstatic --noinput
migrate:
	./manage.py migrate
	./manage.py create_search_indices
pip:
	pip install -r requirements.txt
fresh_code: pull pip make_dirs migrate static
deploy: fresh_code update_cron update_systemd