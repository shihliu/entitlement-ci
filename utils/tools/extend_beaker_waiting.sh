#!/bin/bash
sed -i -e 's/MAX_QUEUED_ATTEMPTS = 4/MAX_QUEUED_ATTEMPTS = 400/' -e 's/MAX_ATTEMPTS = 60/MAX_ATTEMPTS = 600/' $WORKSPACE/ci-ops-central/tasks/get_bkrnodes_task.py