cd cmake-only
rm -rf build-*
set -v
ls
ccc --root-dir $PWD info
ccc --root-dir $PWD build
