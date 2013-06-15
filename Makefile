build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rv build/

unittest:
	python -m unittest discover -s test/
