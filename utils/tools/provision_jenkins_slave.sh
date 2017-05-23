#!/bin/bash
# Provision Jenkins Slave

if [ "$JSLAVENAME" != "master" ]
then
    $WORKSPACE/ci-ops-central/bootstrap/provision_jslave.sh --site=$SITE --project_defaults={project_defaults} \
    --topology=ci-ops-central/project/config/aio_jslave --ssh_keyfile={ssh_keyfile} \
    --jslavename={jslavename} --jslaveflavor={jslaveflavor} --jslaveimage={jslaveimage} \
    --jslave_execs={jslave_execs} --jslavecreate --resources_file={jslavename}.json
    TR_STATUS=$?
    if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning jenkins slave failed, STATUS: $TR_STATUS"; exit 1; fi
fi