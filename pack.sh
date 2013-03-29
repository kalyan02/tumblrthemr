if [ -d dist ]; then
	rm -rf dist/
fi

if [ -d build ]; then
	rm -rf build/
fi

arch -i386 python2.7 setup.py py2app $1
