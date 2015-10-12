class RHSMConstants(object):
    sam_cons = {
    "username":                     "admin",
    "password":                     "admin",

    "autosubprod":                  "CloudForms (10-pack)",
    "installedproductname":         "Red Hat Enterprise Linux Server",
    "productid":                    "MCT2358",

    "pid":                          "69",
    "pkgtoinstall":                 "zsh",
    "servicelevel":                 "Premium",

    "default_org":                  "ACME_Corporation",
    "default_org_sat":              "Default_Organization",

    # rhel 6 constance
    "productrepo":                  "rhel-6-server-rpms",
    "betarepo":                     "rhel-6-server-beta-rpms",
    "releaselist":                  "6.1,6.2,6.3,6.4,6.5,6.6,6Server",

    # rhel 7 constance
    "productrepo_el7":              "rhel-7-server-rpms",
    "betarepo_el7":                 "rhel-7-server-beta-rpms",
    "releaselist_el7":              "7.0,7.1,7Server",

    "proxy_server":                 "10.66.128.144:3128",
    }

    stage_cons = {
    "username":                     "stage_test_12_new",
    "password":                     "redhat",

    "baseurl":                      "https://subscription.rhn.stage.redhat.com:443",
    "prefix":                       "/subscription",
    "autosubprod":                  "Red Hat Enterprise Linux Server",
    "installedproductname":         "Red Hat Enterprise Linux Server",
    "productid":                    "RH0103708",
    "pid":                          "69",
    "pkgtoinstall":                 "zsh",
    # for rhel7
    "productrepo_el7":              "rhel-7-server-rpms",
    "betarepo_el7":                 "rhel-7-server-beta-rpms",
    "releaselist_el7":              "7.0,7.1,7Server",
    # for rhel6
    "productrepo":                  "rhel-6-server-rpms",
    "betarepo":                     "rhel-6-server-beta-rpms",
    "servicelevel":                 "PREMIUM",
    "releaselist":                  "6.1,6.2,6.3,6.4,6Server",
    }

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RHSMConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance
  
    def __init__(self):
        if(self.__initialized): return
        else: self.__initialized = True
