class RHSMConstants(object):
    sam_cons = {
    "username":                     "admin",
    "password":                     "admin",
    "prefix":                       "sam/api",

    "autosubprod":                  "CloudForms (10-pack)",
    "installedproductname":         "Red Hat Enterprise Linux Server",
    "productid":                    "MCT2358",

    "pid":                          "69",
    "pkgtoinstall":                 "zsh",
    "servicelevel":                 "Premium",

    "default_org":                  "ACME_Corporation",
    "default_org_sat":              "Default_Organization",
    "prefix_sat":                   "rhsm",

    # rhel 6 constance
    "productrepo":                  "rhel-6-server-rpms",
    "betarepo":                     "rhel-6-server-beta-rpms",
    "releaselist":                  "6.1,6.2,6.3,6.4,6.5,6.6,6.7,6.8,6Server",

    # rhel 7 constance
    "productrepo_el7":              "rhel-7-server-rpms",
    "betarepo_el7":                 "rhel-7-server-beta-rpms",
    "releaselist_el7":              "7.0,7.1,7.2,7Server",

    "proxy_server":                 "10.66.128.144:3128",
    }

    stage_cons = {
    "username":                     "new_test",
    "password":                     "redhat",

    "hostname":                     "subscription.rhsm.stage.redhat.com",
    # "baseurl":                      "cdn.qa.redhat.com",
    "baseurl":                      "cdn.redhat.com",

    "prefix":                       "subscription",
    "autosubprod":                  "Red Hat Enterprise Linux Server",
    "installedproductname":         "Red Hat Enterprise Linux Server",
    "productid":                    "RH0103708",
    "productid-6":                  "MCT0346",
    "pid":                          "69",
    "pkgtoinstall":                 "zsh",
    "default_org":                  "7967630",
    # for rhel7
    "productrepo_el7":              "rhel-7-server-rpms",
    "betarepo_el7":                 "rhel-7-server-beta-rpms",
    "releaselist_el7":              "7.0,7.1,7.2,7Server",
    # for rhel6
    "productrepo":                  "rhel-6-server-rpms",
    "betarepo":                     "rhel-6-server-beta-rpms",
    "servicelevel":                 "Premium",
    "releaselist":                  "6.1,6.2,6.3,6.4,6.5,6.6,6.7,6.8,6Server",

    "proxy_server":                 "10.66.129.188:3128",
    #special accounts
    "username_ram":                 "ram_qq",
    "password_ram":                 "redhat",
    "username_core":                "ram_qq",
    "password_core":                "redhat",
    "username_sap":                 "sap_test",
    "password_sap":                 "redhat",
    "username_ha":                  "ha_test",
    "password_ha":                  "redhat",     
    "username_rh00073":             "rhelde_test",
    "password_rh00073":             "redhat",
    "username_nocon":               "nocon_test",
    "password_nocon":               "redhat",
    "username_addon":               "smartaddon_test",
    "password_addon":               "redhat",
    "username_mgtaddon":            "management_add_on",
    "password_mgtaddon":            "redhat",
    "username_stackable":           "stack_test",
    "password_stackable":           "redhat",
    "username_arch":                "arch_test",
    "password_arch":                "redhat",
    "username_no_subscription":     "nosub_test",
    "password_no_subscription":     "redhat",
    "username_socket":              "socket_qq",
    "password_socket":              "redhat",
    "username_market":              "mkt_pdt_test",
    "password_market":              "redhat",
    "username_special":             "spw_test",
    "password_special":             "\':ofTe_`!(D=k\'",
    "username_nomulti":             "nomulti_test",
    "password_nomulti":             "redhat",
    "username_skt4":                "skt4_test",
    "password_skt4":                "redhat",
    "username_gui":                 "gui_test",
    "password_gui":                 "redhat"}

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RHSMConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized): return
        else: self.__initialized = True
