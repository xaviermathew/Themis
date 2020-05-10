PROJECT_DIR=`pwd`
VIRTUAL_ENV_ROOT=$(HOME)/virtual_env
VIRTUAL_ENV_NAME=polidicks
CRONTAB_FILE=config/crontab/crontab

link_manage_py:
	ln -s $(PROJECT_DIR)/manage.py $(VIRTUAL_ENV_ROOT)/$(VIRTUAL_ENV_NAME)/bin/manage.py
make_dirs:
	mkdir $(PROJECT_DIR)/logs/
pull:
	git pull
update_cron:
	crontab $(CRONTAB_FILE)
	sudo service cron restart
deploy: pull update_cron
	pip install -r requirements.txt
	./manage.py create_search_indices
	./manage.py migrate