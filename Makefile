
.PHONY: all target clean install uninstall reinstall

TARGET := dist/*.whl

all: $(TARGET)

$(TARGET):
	python -m build --wheel

clean:
	rm -rf build dist *.egg-info docs/_build brunhilda/_version.py

install: $(TARGET)
	pip install --user dist/*.whl

uninstall:
	pip uninstall brunhilda -y

reinstall: uninstall clean install
