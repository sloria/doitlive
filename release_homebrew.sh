#!/bin/sh
# Sends a PR to homebrew-core for a new version of doitlive
# Usage: ./release_homebrew.sh https://files.pythonhosted.org/packages/8c/41/b08e2883c256d52f63f00f622cf8a33d3bf36bb5714af337e67476f8b3fe/doitlive-2.8.0.tar.gz

# Validate argument
[ "$#" -eq 1 ] || { echo 'ERROR: Must pass a URL'; exit 1; }
echo $1 | grep -q '^https://files\.pythonhosted\.org' || { echo 'ERROR: URL must start with https://files.pythonhosted.org'; exit 1; }
URL=$1

# Create a temporary directory
WORK_DIR=`mktemp -d`
# check if tmp dir was created
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  echo "Could not create temp dir"
  exit 1
fi
# deletes the temp directory
function cleanup {
  echo "Cleaning up..."
  rm -rf "$WORK_DIR"
  echo "Done."
}
# remove temporary directory after exiting
trap cleanup EXIT

OUTPUT_PATH="$WORK_DIR/doitlive.tar.gz"
curl $URL -o $OUTPUT_PATH
SHA256=`shasum -a 256 $OUTPUT_PATH | head -1 | grep -o '^\S\+'`
echo "URL: $URL"
echo "SHA: $SHA256"

brew update
echo '*** Sending PR to homebrew-core... ***'
brew bump-formula-pr --strict --sha256=$SHA256 --url=$URL doitlive
