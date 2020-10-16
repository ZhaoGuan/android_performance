rm -rf build dist
pyinstaller ./main.spec
cp -rf moudle/mitmproxy ./dist/android_performance
cp -rf proxy ./dist/client_url_statistics
