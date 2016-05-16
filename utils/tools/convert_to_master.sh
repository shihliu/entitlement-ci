#!/bin/bash
# if no parameter provided, convert to unified master jobs, else convert back
if [ ! -n "$1" ]
then
    echo "convert to unified master jobs"
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/node: master/node: '{jmastername}'/g" {}
    ls *.yaml | grep -v "virt-who-defaults.yaml" | xargs -i -d "\n" sed -i -e "/    jmastername: jslave-static-entitlement-master/d" -e "\$a\    jmastername: jslave-static-entitlement-master" {}
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/provision_jslave.sh --site/provision_jslave.sh --jenkins_master_username=sgao --jenkins_master_password=0bdd1e1626c4701fc0023fa87474459d --site/g" {}
else
    echo "convert to private master jobs"
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/node: '{jmastername}'/node: master/g" -e "/    jmastername: jslave-static-entitlement-master/d" {}
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/provision_jslave.sh --jenkins_master_username=sgao --jenkins_master_password=0bdd1e1626c4701fc0023fa87474459d --site/provision_jslave.sh --site/g" {}
fi