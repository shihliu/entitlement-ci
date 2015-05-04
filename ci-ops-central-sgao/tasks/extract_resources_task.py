import os
import json
import string

import taskrunner

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_JSON = os.environ.get('RESOURCES_JSON', THIS_DIR
                                + '/../../resources.json')


class ExtractResources(taskrunner.Task):
    """
       Extract resources from resources_files
    """

    def __init__(self, resources_files, resources_output, ansible_inventory,
                 **kwargs):
        """
        :param resources_files: all the resources_files that need to be parsed
        :param resources_output: ip addresses from node creation in a file
                                used for env
        """
        super(ExtractResources, self).__init__(**kwargs)
        self.resources_files = resources_files
        self.resources_output = resources_output
        self.ansible_inventory = ansible_inventory
        self.resources_json = RESOURCES_JSON

    def run(self, context):
        self._extract_resources()

    def cleanup(self, context):
        pass

    def _extract_resources(self):
        nodes = []
        existing_nodes = ''
        private_ips = ''
        label = os.environ.get('LABEL', '')
        uuid = os.environ.get('UUID', '')
        site = os.environ.get('SITE', 'qeos')
        jenkins_master_url = os.environ.get('JENKINS_MASTER_URL', '')
        job_name = os.environ.get('JOB_NAME', '')
        build_number = os.environ.get('BUILD_NUMBER', '')
        provision_job = os.environ.get('PROVISION_JOB', jenkins_master_url +
                                       '/view/All/job/' + job_name + '/' +
                                       build_number)

        if self.resources_files != []:
            resources_out = open(self.resources_output, 'a')
            ansible_inv = open(self.ansible_inventory, 'w')
            r_json = open(self.resources_json, 'w')
            job_id = ''
            for resources_file in self.resources_files:
                in_filesize = os.path.getsize(resources_file)

                if in_filesize > 0:
                    input_file = open(resources_file, 'r')
                    data = json.load(input_file)
                    input_file.close

                    for idx, resources in data.iteritems():
                        for resource in resources:
                            if 'nodes' in resource:
                                for node in resource['nodes']:
                                    node['ip'] = str(node['ip'])
                                    node['private_ip'] \
                                        = str(node['private_ip'])
                                    nodes.append(node)
                                    existing_nodes = \
                                        existing_nodes + node['ip'] + ","
                                    private_ips = \
                                        private_ips + node['private_ip'] + ","
                            if 'system' in resource:
                                resource['system'] = str(resource['system'])
                                nodes.append(resource)
                                existing_nodes = \
                                    existing_nodes + resource['system'] + ","
                        if 'job_id' in idx:
                            job_id = resources
            existing_nodes = existing_nodes[:-1]
            private_ips = private_ips[:-1]

            resources_out.write("EXISTING_NODES=" + existing_nodes)
            resources_out.write("\nPRIVATE_IPS=" + private_ips)
            resources_out.write("\nBKR_JOBID=J:" + job_id)
            resources_out.write("\nSITE=" + site)
            resources_out.write("\nLABEL=" + label)
            resources_out.write("\nUUID=" + uuid)
            resources_out.write("\nPROVISION_JOB=" + provision_job)

            resources = {'resources': nodes}
            json.dump(resources, r_json, indent=4)
            r_json.close()
            resources_out.write("\n")
            resources_out.close()
            ansible_nodes = string.replace(existing_nodes, ',', '\n')
            ansible_inv.write("[local]\nlocalhost   "
                              "ansible_connection=local\n")
            ansible_inv.write("\n[testsystems]\n" + ansible_nodes)
            ansible_inv.write("\n")
            ansible_inv.close()
