#!/usr/bin/env bash
# Mirror the site's content (photos, résumé, rank list, manifests) out of the
# private S3 folder the live site serves from, into content/.
#
#   DEV_SITE_BUCKET=<bucket> bash scripts/pull_content.sh
#
# Never pulled: private/ (the owner-panel password hash) and music/ (the
# songs are commercial recordings; see CLAUDE.md, "Music"). music.json is
# rewritten to an empty playlist so the mirror runs silent instead of
# pointing at files it does not have.
set -euo pipefail
: "${DEV_SITE_BUCKET:?set DEV_SITE_BUCKET to the uploads bucket name}"
cd "$(dirname "$0")/.."
aws s3 sync "s3://${DEV_SITE_BUCKET}/dev-site/" content/ \
  --exclude "private/*" --exclude "music/*" --exclude "music.json" --delete --only-show-errors
printf '{"tracks": [], "volume": 0.6}\n' > content/music.json
echo "content/ now mirrors s3://…/dev-site/ (minus private/ and music/)"
