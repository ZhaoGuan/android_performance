rm -rf build dist
#pyinstaller -F ./main.py -n android_performance \
#  --hidden-import=yaml \
#  --hidden-import=jinja2
pyinstaller ./main.py -n android_performance
cp -rf moudle/mitmproxy ./dist/android_performance
cp -rf proxy ./dist/android_performance
