#!/usr/bin/env bash
# Keep an explicit rollback control available after promotion.
set -Eeuo pipefail
exec xterm -hold -title 'PsyCachy activation' -e sudo /bin/bash /usr/local/lib/psycachy/activate.sh
