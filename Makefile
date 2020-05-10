PROJECT_DIR=`pwd`
VIRTUAL_ENV_ROOT=$(HOME)/virtual_env
VIRTUAL_ENV_NAME=polidicks

link_manage_py:
	ln -s $(PROJECT_DIR)/manage.py $(VIRTUAL_ENV_ROOT)/$(VIRTUAL_ENV_NAME)/bin/manage.py
deploy:
	git pull
	pip install -r requirements.txt
	./manage.py create_search_indices
	./manage.py migrate