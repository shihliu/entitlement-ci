#!/bin/bash
ls *.yaml | grep -v "defaults\|triggers" | xargs -i -d "\n" sed -i -e "s/node: master/node: '{jmastername}'/g" -e "/    jslavename:/a\    jmastername: jslave-static-entitlement-master" {}