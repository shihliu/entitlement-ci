#!/usr/bin/env python

"""
This script will append current usage information for an OpenStack cloud to
a csv file. It requires admin credentials which are taken from the following
environment variables:

OS_USERNAME
OS_TENANT_NAME
OS_PASSWORD
OS_AUTH_URL
"""

import argparse
import csv
import datetime
import logging
import os
import time

import keystoneclient.v2_0.client as keystone_client
import novaclient.client as nova_client

LOG = logging.getLogger(__name__)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def get_tenant_by_name(tenants, name):
    for t in tenants:
        if t.name == name:
            return t
    else:
        raise Exception("No tenant found: %s" % name)


def get_usage(nova, flavor_map, tenant):
    vcpu = 0
    ram = 0
    disk = 0
    u = {}
    u['tenant_name'] = tenant.name
    u['timestamp'] = str(datetime.datetime.utcnow())
    search_opts = {'all_tenants': True, 'tenant_id': tenant.id}
    servers = nova.servers.list(search_opts=search_opts)
    quotas = nova.quotas.get(tenant.id)
    for server in servers:
        flavor = flavor_map[server.flavor['id']]
        vcpu += flavor.vcpus
        ram += flavor.ram
        disk += flavor.disk
    u['vcpu'] = vcpu
    u['ram_mb'] = ram
    u['disk_gb'] = disk
    u['instances'] = len(servers)

    def positivise(n):
        return n if n >= 0 else 0x7fffffff

    u['quota_cores'] = positivise(quotas.cores)
    u['quota_ram'] = positivise(quotas.ram)
    u['quota_instances'] = positivise(quotas.instances)
    return u


def write_csv(filename, usages):
    fields = ['tenant_name', 'timestamp', 'vcpu', 'ram_mb', 'disk_gb',
              'instances', 'quota_cores', 'quota_ram', 'quota_instances']
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fields, extrasaction='ignore')
        for usage in usages:
            writer.writerow(usage)


def parse_arguments():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--tenant', default=None,
                        help="Gather data for a single tenant")
    parser.add_argument('--csv-file', default=None, required=True,
                        help="Path csv file. Current usage will be appended")
    return parser.parse_args()


def main():
    args = parse_arguments()
    logging.basicConfig(format=LOG_FORMAT)
    LOG.setLevel(logging.INFO)
    (user, password, tenant, auth_url) = (os.environ['OS_USERNAME'],
                                          os.environ['OS_PASSWORD'],
                                          os.environ['OS_TENANT_NAME'],
                                          os.environ['OS_AUTH_URL'])
    nova = nova_client.Client('2', user, password, tenant, auth_url)
    keystone = keystone_client.Client(username=user,
                                      password=password,
                                      tenant_name=tenant,
                                      auth_url=auth_url)
    tenants = keystone.tenants.list()
    if args.tenant:
        tenants = [get_tenant_by_name(tenants, args.tenant)]

    flavor_map = {}
    for flavor in nova.flavors.list():
        flavor_map[flavor.id] = flavor

    usages = []
    for tenant in tenants:
        u = get_usage(nova, flavor_map, tenant)
        LOG.info("Tenant: %s %s" % (u['tenant_name'], u))
        usages.append(u)
        # Be a little nice to the cloud
        time.sleep(2)

    usages = sorted(usages,
                    key=lambda k: k['vcpu'],
                    reverse=True)
    write_csv(args.csv_file, usages)


if __name__ == "__main__":
    main()
