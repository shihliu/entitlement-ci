#!/bin/bash
pushd $WORKSPACE/entitlement-ci/utils/xmlparser/
  export PYTHONPATH=$WORKSPACE/entitlement-ci
  #echo "polarion.template={polarion_template}" > $WORKSPACE/POLARION.txt
  python polarion_name_to_id.py $WORKSPACE/nosetests.xml $WORKSPACE/POLARION.txt
  export RHEL_COMPOSE_FOR_POLARION=`echo $RHEL_COMPOSE | sed "s/\./_/g"`
popd