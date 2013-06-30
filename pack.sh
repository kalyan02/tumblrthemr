if [ -d dist ]; then
	rm -rf dist/
fi

if [ -d build ]; then
	rm -rf build/
fi

# get a build number using number of total commits
# not the best way, but this will have to do
B_NUMBER=`git log | grep ^commit | wc -l | perl -ne '$_=~s/[^0-9]//g;print $_;'`
# put it in a conf file so we can show it that way in the ui dialog
echo "build_version = 'build $B_NUMBER'" > src/conf.py

# arch -i386 python2.7 setup.py py2app $1 $2 $3

# cd dist/
# zip -r -9 TumblrTemplatr.zip TumblrTemplatr.app
