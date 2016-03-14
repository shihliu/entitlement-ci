#!/bin/bash
# if no parameter provided, convert to unified master jobs, else convert back
if [ ! -n "$1" ]
then
    echo "convert to unified master jobs"
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/node: master/node: '{jmastername}'/g" {}
    ls *.yaml | grep -v "virt-who-defaults.yaml" | xargs -i -d "\n" sed -i -e "/    jmastername: jslave-static-entitlement-master/d" -e "\$a\    jmastername: jslave-static-entitlement-master" {}
else
    echo "convert to private master jobs"
    ls *.yaml | xargs -i -d "\n" sed -i -e "s/node: '{jmastername}'/node: master/g" -e "/    jmastername: jslave-static-entitlement-master/d" {}
fi