# Run from project root

set -e # Stop on error

rm -rf dist/core dist/core.zip
mkdir -p dist/core
cp audio.json core.json data.json input.json interact.json variants.json video.json ../quartus/reverse/bitstream.rbf_r dist/core
(cd dist && zip -r core.zip core)
