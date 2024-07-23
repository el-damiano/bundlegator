export BUNDLE_CACHE_DIR="__cache__"
test -d $BUNDLE_CACHE_DIR || mkdir $BUNDLE_CACHE_DIR
export HUMBLE_BUNDLE_CACHE="$BUNDLE_CACHE_DIR/humble_bundle"
test -f $HUMBLE_BUNDLE_CACHE || touch $HUMBLE_BUNDLE_CACHE

python -m unittest discover -s src

rm -r $HUMBLE_BUNDLE_CACHE
