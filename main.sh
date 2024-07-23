if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    test $XDG_CACHE_HOME &&
        export BUNDLE_CACHE_DIR="$XDG_CACHE_HOME" ||
        export BUNDLE_CACHE_DIR="__cache__"
    test -d $BUNDLE_CACHE_DIR || mkdir $BUNDLE_CACHE_DIR
    export HUMBLE_BUNDLE_CACHE="$BUNDLE_CACHE_DIR/humble_bundle"
    test -f $HUMBLE_BUNDLE_CACHE || touch $HUMBLE_BUNDLE_CACHE
else
    export BUNDLE_CACHE_DIR="__cache__"
fi

python3 src/main.py
