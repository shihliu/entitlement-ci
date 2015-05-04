import os
import sys
import urllib2
import logging
import keystoneclient.v2_0.client as ksclient
import glanceclient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s '
                           '%(levelname)-5s %(message)s')

LOG = logging.getLogger(__file__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../lib', '../config', '../project']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

from provision_parser import (
    get_json_props,
    create_global_defaults,
    merge_all_props
)

BASEURL = os.environ.get('BASEURL',
                         'http://download.devel.redhat.com/brewroot/packages')

GLOBAL_DEFAULTS = \
    os.environ.get('GLOBAL_DEFAULTS', THIS_DIR +
                   '/../jobs/global_defaults.json')
PROJECT_DEFAULTS = \
    os.environ.get('PROJECT_DEFAULTS', THIS_DIR +
                   '/../project/config/project_defaults.json')


def _get_fetcher(resource):
    """
        Return a function that allows out to get a specific property,
        first from the os.environment, then from the given resource,
        and at if not there return the default passed.
    """
    def _get_prop(pname, ename=None, default=None):
        if ename is None:
            ename = pname.upper()
        return os.environ.get(pname.upper(), resource.get(pname, default))
    return _get_prop


def _check_image_exists(glance, image_name):
    """
        Find if image exits in Glance for provided image name.
        Return True if exists else False if not
    """
    images = list(glance.images.list())
    img = [im_ for im_ in images if im_.id == image_name]
    img = img or [im_ for im_ in images if im_.name == image_name]
    if img:
        return True
    else:
        return False

global_data = get_json_props(GLOBAL_DEFAULTS)
global_defaults = create_global_defaults(global_data)
project_data = get_json_props(PROJECT_DEFAULTS)
final_props = merge_all_props([global_defaults, project_data])

glance_creds = {}
nova_creds = {}
_get_prop = _get_fetcher(final_props['sites'][0])
# Openstack site properties
glance_creds['auth_url'] = _get_prop('endpoint', default=None)
_get_prop = _get_fetcher(final_props['resources'][0])
glance_creds['username'] = _get_prop('username', default=None)
glance_creds['password'] = _get_prop('password', default=None)
glance_creds['tenant_name'] = _get_prop('project', default=None)

# Credential used for keystone and glance
keystone = ksclient.Client(**glance_creds)
glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
glance = glanceclient.Client('1', glance_endpoint, token=keystone.auth_token)

# This should come from the CI Message bus
PKGNAME = os.environ.get('PKGNAME', 'rhel-atomic-cloud')
VERSION = os.environ.get('VERSION', None)
RELEASE = os.environ.get('RELEASE', None)
NVR = os.environ.get('NVR', None)
ARCH = os.environ.get('ARCH', 'x86_64')

# Image is provided instead don't use url location
IMAGE = os.environ.get('IMAGE', None)

if IMAGE is not None:
    LOG.info("IMAGE was defined using %s" % IMAGE)
    image_name = os.path.splitext(IMAGE)[0]
    LOG.info("Image name is %s" % image_name)
    if _check_image_exists(glance, image_name):
        LOG.info("Image %s already exists" % image_name)
    else:
        LOG.info("Uploading image %s" % image_name)
        try:
            with open(IMAGE) as fimage:
                image_out = glance.images.create(name=image_name,
                                                 is_public=True,
                                                 disk_format="qcow2",
                                                 container_format="bare",
                                                 data=fimage)
            LOG.info("Result: %s" % image_out)
        except Exception, ex:
            msg = "Upload of image %s FAILED" % image_name
            LOG.error(msg)
            raise Exception(msg)
elif VERSION is not None and RELEASE is not None and NVR is not None:
    LOG.info("NVR, VERSION, and RELEASE are defined uploading from URL")
    LOG.info("PKGNAME: %s" % PKGNAME)
    LOG.info("NVR: %s" % NVR)
    LOG.info("VERSION: %s" % VERSION)
    LOG.info("RELEASE: %s" % RELEASE)
    image_name = NVR
    url = BASEURL + '/' + PKGNAME + '/' + VERSION + '/' + RELEASE + '/' \
                  + 'images/' + NVR + '.' + ARCH + '.qcow2'
    # Check if url is valid
    try:
        urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        msg = "HTTP ERROR %s on %s" % (e.code, url)
        LOG.error(msg)
        raise Exception(msg)
    except urllib2.URLError, e:
        msg = "URL ERROR %s on %s" % (e.code, url)
        LOG.error(msg)
        raise Exception(msg)
    LOG.info("Image Location: %s" % url)
    if _check_image_exists(glance, image_name):
        LOG.info("Image %s already exists" % image_name)
    else:
        LOG.info("Uploading image %s" % image_name)
        try:
            image_out = glance.images.create(name=image_name, is_public=True,
                                             disk_format="qcow2",
                                             container_format="bare",
                                             location=url)
            LOG.info("Result: %s" % image_out)
        except Exception, ex:
            msg = "Upload of image %s FAILED" % image_name
            LOG.error(msg)
            raise Exception(msg)
else:
    msg = "NVR, VERSION, and RELEASE NOT Found\n or IMAGE not specified\n"
    LOG.error(msg)
    raise Exception(msg)
