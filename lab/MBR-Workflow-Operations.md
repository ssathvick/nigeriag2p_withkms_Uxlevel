# Current Master Registry authority — 14 November 2026

Native Registry and AWE own capture, review, resubmission and publication. The current UI is registry-ui-source/; household and individual records remain in native PostgreSQL tables. The supplemental /registration/mbr write API and its importer are retired. Do not run deploy-mbr-workflow.py, deploy-mbr-integration.py or enable iqs-mbr-native-import.timer for a new installation.

Use the repository README and docs/current/INSTALLATION.md for the staged native installation. meeting-native/changes.json records the version-scoped Registry/AWE backend mounts. The current survey does not display an enumerator selector; stored values/history are retained. Staff management and offline setup are authenticated utilities, not a second registry approval engine.

The earlier migration account, row counts and supplemental workflow procedures are retained only in MBR-Workflow-History-pre-20261114.md as historical context. They do not describe the current workflow owner and must not be used as a fresh-machine installation recipe.
