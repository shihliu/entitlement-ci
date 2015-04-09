'''
commands to create virt-who kickstart file
make sure repo/distros exist, add repo/profiles/ and repo/kickstarts/libvirt/RHEL[5,6,7]/ 
'''
import os, time
from utils import logger
from utils.tools.shell.command import Command

runtime_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "runtime/"))
kickstart_repo_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "runtime/repo/"))
dir_sample_kickstart = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "data/kickstart/"))

class VirtWhoKickstart(Command):

    def create(self, compose):
        build, date, distro_name = self.__get_distro_name(compose)
        profile_name = "ent-%s-server-x64-%s-kvm-libvirt.profile" % (build, date)
        kickstart_name = "ent-ks-%s-server-x64-%s-kvm-libvirt.cfg" % (build, date)
        distro_file = kickstart_repo_dir + "/distros/" + distro_name
        profile_file = kickstart_repo_dir + "/profiles/" + profile_name
        kickstart_file = kickstart_repo_dir + "/kickstarts/libvirt/RHEL%s/" % self.get_rhel_version(kickstart_name) + kickstart_name 
        self.__check_git_repo()
#         self.__check_distro(distro_file)
        self.__create_distro(compose, distro_file)
        self.__create_kickstart(compose, kickstart_file)
        self.__create_profile(distro_name, kickstart_name, profile_file)
        if self.get_rhel_version(compose) == 5:
            profile_xen_name = "ent-%s-server-x64-%s-xen-libvirt.profile" % (build, date)
            profile_xen_file = kickstart_repo_dir + "/profiles/" + profile_xen_name
            kickstart_xen_name = "ent-ks-%s-server-x64-%s-xen-libvirt.cfg" % (build, date)
            kickstart_xen_file = kickstart_repo_dir + "/kickstarts/libvirt/RHEL%s/" % self.get_rhel_version(kickstart_xen_name) + kickstart_xen_name
            self.__create_kickstart(compose, kickstart_xen_file)
            self.__create_profile(distro_name, kickstart_xen_name, profile_xen_file)
            self.__git_add(profile_xen_file)
            self.__git_add(kickstart_xen_file)
        self.__git_add(distro_file)
        self.__git_add(profile_file)
        self.__git_add(kickstart_file)
        self.__git_push()

    def __get_distro_name(self, compose):
#         RHEL6.5-20131213.0
#         RHEL6u5-Server-x64-20131213.0.distro
#         RHEL-7.0-20140507.0
#         RHEL-7u0-Server-x64-20140507.0.distro
#         RHEL5.11-Server-20140625.0
#         RHEL5u11-Server-x86_64-20140625.0.distro
        if self.get_rhel_version(compose) == 5:
            build = compose.split("-")[0].replace(".", "u")
            date = compose.split("-")[2]
            return build, date, "ent-%s-Server-x86_64-%s.distro" % (build, date)
        elif self.get_rhel_version(compose) == 6:
            # change from 6.6 begining
#             build = compose.split("-")[0].replace(".", "u")
#             date = compose.split("-")[1]
#             return build, date, "ent-%s-Server-x64-%s.distro" % (build, date)
            build = compose.split("-")[0] + "-" + compose.split("-")[1].replace(".", "u")
            date = compose.split("-")[2]
            return build, date, "ent-%s-Server-x64-%s.distro" % (build, date)
        elif self.get_rhel_version(compose) == 7:
            build = compose.split("-")[0] + "-" + compose.split("-")[1].replace(".", "u")
            date = compose.split("-")[2]
            return compose.split("-")[0] + compose.split("-")[1].replace(".", "u"), date, "ent-%s-Server-x64-%s.distro" % (build, date)

    def __get_build_name(self, compose):
        if self.get_rhel_version(compose) == 5:
            build = compose.split("-")[0].replace(".", "u")
            date = compose.split("-")[2]
            return "%s-Server-x86_64-%s.distro" % (build, date)
        elif self.get_rhel_version(compose) == 6:
            build = compose.split("-")[0].replace(".", "u")
            date = compose.split("-")[1]
            return "%s-Server-x64-%s.distro" % (build, date)
        elif self.get_rhel_version(compose) == 7:
            build = compose.split("-")[0] + "-" + compose.split("-")[1].replace(".", "u")
            date = compose.split("-")[2]
            return "%s-Server-x64-%s.distro" % (build, date)

    def __check_git_repo(self):
        if not self.__check_path_exist(kickstart_repo_dir):
            logger.info("git repo not exist, cloning now ...")
            cmd = "git clone git+ssh://git@qe-git.englab.nay.redhat.com/~/repo/virt-qe/repo"
            if not self.__check_path_exist(runtime_dir):
                self.__create_path(runtime_dir)
            self.git_run(cmd, runtime_dir)
#         cmd = "pushd /root/workspace/entitlement/utils/tools/shell/repo/ && git pull && popd"
        cmd = "git pull"
        self.git_run(cmd, kickstart_repo_dir)

    def __check_distro(self, distro_name):
        # will add time out, if fail, add distro
        while not self.__check_file_exist(distro_name):
            logger.info("distro_name %s not exist yet, waiting 1 minute ..." % distro_name)
            time.sleep(60)

    def __create_distro(self, compose, distro_file):
        rhel_version = self.get_rhel_version(compose)
        if rhel_version == 5:
            compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/tree-x86_64/" % compose
        elif rhel_version == 6:
#           compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/%s/Server/x86_64/os/" % (compose, self.get_rhel_version(compose))
            compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/compose/Server/x86_64/os/" % compose
        elif rhel_version == 7:
            compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/compose/Server/x86_64/os/" % compose
        if not self.__check_file_exist(distro_file):
            if rhel_version == 7:
                modified_rhel_version = 6
            else:
                modified_rhel_version = rhel_version
            cmd = ('cat <<EOF > %s\n'
                '[General]\n'
                'arch : x86_64\n'
                'breed : redhat\n'
                'comment :\n'
                '\n'
                'kernel : %simages/pxeboot/vmlinuz\n'
                'initrd : %simages/pxeboot/initrd.img\n'
                'kernel_options : biosdevname=0 reboot=pci\n'
                'kernel_options_post :\n'
                'ks_meta :\n'
                'mgmt_classes :\n'
                '\n'
                'os_version : rhel%s\n'
                'redhat_management_key :\n'
                'redhat_management_server :\n'
                'template_files :\n'
                'EOF' % (distro_file, compose_url, compose_url, modified_rhel_version)
                )
            logger.info("Created distro file: %s" % distro_file)
            self.run(cmd)
        else:
            logger.info("Distro file: %s already existed ..." % distro_file)

    def __create_kickstart(self, compose, kickstart_file):
        if not self.__check_file_exist(kickstart_file):
            if "xen" in kickstart_file:
                sample_kickstart = "ent-ks-rhel5-xen-sample.cfg"
            else:
                sample_kickstart = "ent-ks-rhel%s-kvm-sample.cfg" % self.get_rhel_version(compose)
            if self.get_rhel_version(compose) == 5:
                compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/tree-x86_64" % compose
            elif self.get_rhel_version(compose) == 6:
                compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/%s/Server/x86_64/os/" % (compose, self.get_rhel_version(compose))
            elif self.get_rhel_version(compose) == 7:
                compose_url = "http://download.englab.nay.redhat.com/pub/rhel/rel-eng/%s/compose/Server/x86_64/os/" % compose
            cmd = "sed -e 's#auto-rhel-compose-url#%s#g' %s > %s" % (compose_url, dir_sample_kickstart + "/" + sample_kickstart, kickstart_file)
            logger.info("Created kickstart: %s" % kickstart_file)
            self.run(cmd)
        else:
            logger.info("kickstart: %s already existed ..." % kickstart_file)

    def __create_profile(self, distro_name, kickstart_name, profile_file):
        if not self.__check_file_exist(profile_file):
            cmd = ('cat <<EOF > %s\n'
                '[General]\n'
                'distro = %s\n'
                'kickstart = libvirt/RHEL%s/%s\n'
                'EOF' % (profile_file, distro_name.strip(".distro"), self.get_rhel_version(distro_name), kickstart_name)
                )
            logger.info("Created profile: %s" % profile_file)
            self.run(cmd)
        else:
            logger.info("Profile: %s already existed ..." % profile_file)

    def __git_push(self):
        cmd = "git commit -m 'Auto add virt-who kickstart file'"
        self.run(cmd)
        cmd = "git push"
        self.git_run(cmd, kickstart_repo_dir)

    def __git_add(self, file):
        logger.info("Git add: %s" % file)
        cmd = "git add %s" % file
        self.run(cmd)

    def __check_file_exist(self, file_name):
        return os.path.isfile(file_name)

    def __check_path_exist(self, path_name):
        return os.path.exists(path_name)

    def __create_path(self, path_name):
        os.makedirs(path_name)

if __name__ == "__main__":
#     virt_who_kick = VirtWhoKickstart().create("RHEL6.5-20131213.0")
#     virt_who_kick = VirtWhoKickstart().create("RHEL-7.0-20140507.0")
    virt_who_kick = VirtWhoKickstart().create("RHEL-6.6-20140718.0")
#     sam_command.add_sam_repo("SAM-1.4.0-RHEL-6-20140512.0")

