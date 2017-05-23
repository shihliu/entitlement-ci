#!/bin/bash

echo "setup before runtest begins ..."
#rhel 7, work around for issue: "CTR mode needs counter parameter, not IV"
#sed -i "s/iv, counter/'', counter/g" /usr/lib/python2.7/site-packages/paramiko/transport.py

#change slave time for log time display
#cp -n /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime