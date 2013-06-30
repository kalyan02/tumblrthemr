# get a build number using number of total commits
B_NUMBER=`git log | grep ^commit | wc -l | perl -ne '$_=~s/[^0-9]//g;print $_;'`
# put it in a conf file so we can show it that way in the ui dialog
echo "build_version = 'build $B_NUMBER'" > src/conf.py

cd src/
python main.py
