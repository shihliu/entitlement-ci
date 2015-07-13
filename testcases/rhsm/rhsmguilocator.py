from testcases.rhsm.rhsmconstants import RHSMConstants

class RHSMGuiLocator(RHSMConstants):

    # ========================================================
    #       RHSM GUI test elements
    # ========================================================
    element_locators = {

    ######## Window Elements ########
    'main-window-5':                         'Subscription Manager',
    'main-window':                           'frmSubscriptionManager',
    'register-dialog-5':                     'register_dialog',
    'register-dialog':                       'dlgregister_dialog',
    'subscribe-dialog-5':                    'Subscribe System',
    'subscribe-dialog':                      'frmSubscribeSystem',
    'import-cert-dialog':                    'dlgImportCertificates',
    'select-file-dialog':                    'dlgSelectAFile',
    'system-facts-dialog-7':                 'frmSubscriptionManager-Facts',
    'system-facts-dialog':                   'dlgfacts_dialog',
    'search-dialog':                         'frmSearching',
    'proxy-configuration-dialog':            'dlgProxyConfiguration',
    'information-dialog':                    'dlgInformation',
    'question-dialog':                       'dlgQuestion',
    'error-dialog':                          'dlgError',
    'system-preferences-dialog':             'dlgSystemPreferences',
    'subscription-manager-manual-window':    'frmSubscriptionManagerManual',
    'onlinedocumentation-window':            'frmRedHatSubscriptionManagement-RedHatCustomerPortal-MozillaFireFox',
    'security-warning-dialog':               'dlgSecurityWarning',
    'about-subscription-manager-dialog':     'dlgAboutSubscriptionManager',
    'rhsm-notification-dialog':              'dlgNotification',
    'filter-options-window':                 'frmFilterOptions',
    'error-cert-dialog':                     'dlgError',
    'sm-gui-warning-classic-dialog':         'dlgWarning',
    'firstboot-main-window':                 'frm0',
    'firstboot-wng-dialog':                  'dlgWarning',
    'firstboot-err-dialog':                  'dlgError',
    'classic-main-window':                   'frmSystemRegistration',
    'classic-confirm-osrelease-window':      'dlgConfirmoperationsystemreleaseselection',
    'classic-updates-configured-window':     'frmUpdatesConfigured',

    ######## Tab Elements ########
    'all-tabs':                              'ptl0',
    'my-installed-software-5':               'My Installed Products',
    'my-installed-software':                 'ptabMyInstalledSoftware',
    'my-subscriptions-5':                    'My Subscriptions',
    'my-subscriptions':                      'ptabMySubscriptions',
    'all-available-subscriptions-5':         'All Available Subscriptions',
    'all-available-subscriptions':           'ptabAllAvailableSubscriptions',
    'my-installed-software':                 'ptabMyInstalledProducts',

    ######## Button Elements ########
    # button in main window
    'toggle-desktop':                        'tbtnDesktop',
    'proxy-save-button':                     'btnSaveButton',
    'proxy-close-button-7':                  'btnCancelButton',
    'attach-subscription':                   'btnAttach',
    'register-button-5':                     'Register System',
    'register-button':                       'btnRegisterSystem',
    'unregister-button-5':                   'btnUnregister',
    'unregister-button':                     'btnUnregister',
    'auto-subscribe-button-5':               'Auto-subscribe',
    'auto-subscribe-button':                 'btnAuto-attach',
    'unsubscribe-button':                    'btnUnsubscribe',
    # button in register dialog
    'dialog-register-button-5':              'register_button',
    'dialog-register-button':                'btnregisterbutton',
    'dialog-cancle-button-5':                'cancel_button',
    'dialog-cancle-button':                'btncancelbutton',
    # button in subscribe dialog
    'dialog-subscribe-button-5':             'btnSubscribe',
    'dialog-subscribe-button':               'btnSubscribe',
    'dialog-back-button':                    'btnBack',
    # button in register dialog
    'configure-proxy-button':                'btnproxybutton',
    # button in import-certificate-dialog
    'ok-button':                             'btnOK',
    'import-file-button':                    'btnImport',
    'type-pem-name-button':                  'tbtnTypefilename',
    'certificate-location-button':           'btn(None)',
    # button in select-file-dialog
    'type-file-name-button':                 'tbtnTypeafilename',
    'open-file-button':                      'btnOpen',
    'proxy-close-button':                    'btnCloseButton',
    'yes-button':                            'btnYes',
    # button in system-preferences-dialog
    'close-button':                          'btnClose',
    # button in firstboot gui
    'firstboot-fwd-button':                  'btnForward',
    'firstboot-agr-button':                  'rbtnYes,IagreetotheLicenseAgreement',
    'firstboot-yes-button':                  'btnYes',
    'firstboot-ok-button':                   'btnOK',
    'firstboot-finish-button':               'btnFinish',
    'firstboot-register-now-button':         'rbtnYes,I\'dliketoregisternow',
    'firstboot-register-rhsm-button':        'rbtnRedHatSubscriptionManagement',
    'firstboot-classic-select-button':       'rbtnRedHatNetwork(RHN)Classic',
    # button in rhn_classic gui
    'classic-forward-button':                'btnForward',
    'classic-confirm-osrelease-yes-button':              'btnYes,Continue',
    'classic-updates-configured-finish-button':          'btnFinish',
    # else
    'remove-subscriptions-button':       'btnRemove',
    'system-preferences-button':         'btnSystemPreferences',
    'proxy-configuration-button':        'btnProxyConfiguration',
    'view-system-facts-button':          'btnViewSystemFacts',
    'import-certificate-button':         'btnImportCertificate',
    'help-button':                       'btnHelp',
    'update-button':                     'btnSearch',
    'filters-button':                    'btnFilters',

    ######## Table Elements ########
    'table-places':                          'tblPlaces',
    'table-files':                           'tblFiles',
    'my-product-table-5':                    'Installed View',
    'my-product-table':                      'tblBundledProductsTable',
    'my-subscription-table-5':               'My Subscriptions View',
    'my-subscription-table':                 'ttblMySubscriptionsView',
    'all-subscription-table-5':              'AllSubscriptionsView',
    'all-subscription-table':                'ttblAllSubscriptionsView',
    'all-product-table-5':                   'tblAllAvailableBundledProductTable',
    'all-product-table':                     'tblAllAvailableBundledProductTable',
    'installed-product-table-5':             'tblInstalledView',
    'installed-product-table':               'tblInstalledView',
    'facts-view-table':                      'ttblfactsview',
    'orgs-view-table':                       'tblownertreeview',

     ######## Text Elements ########
    'text-product':                          'txtProductText',
    'filter-subscriptions-text':             'txtTextinSubscription',
    'login-text-5':                          'txtaccountlogin',
    'login-text':                            'account_login',
    'password-text-5':                       'txtaccountpassword',
    'password-text':                         'account_password',
    # text in select-file-dialog
    'location-text':                         'txtLocation',
    'proxy-location-text':                   'txtProxyLocation',
    'server-url-text':                       'txtserverentry',
    # firstboot
    'firstboot-login-text':                  'txtaccountlogin',
    'firstboot-password-text':               'txtaccountpassword',
    'firstboot-organization-entry-text':     'txtorganizationentry',
    'firstboot-activation-key-text':         'txtactivationkeyentry',
    # rhn_classic
    'classic-login-text':                    'txtLogin',
    'classic-password-text':                 'txtPassword',
    'classic-set-systemname-text':           'txtSystemName',
    'text-service-level':                    'txtAllAvailableSupportLevelAndTypeText',


    ######## Menu Elements ########
    # under System menu
    'system-menu':                           'mnuSystem',
    'register-menu':                         'mnuRegister',
    'unregister-menu':                       'mnuUnregister',
    'importcert-menu':                       'mnuImportCert',
    'viewsystemfacts-menu':                  'mnuViewSystemFacts',
    'configureproxy-menu':                   'mnuConfigureProxy',
    'preferences-menu':                      'mnuPreferences',
    'quit-menu':                             'mnuQuit',
    # under Help menu
    'help-menu':                             'mnuHelp',
    'gettingstarted-menu':                   'mnuGettingStarted',
    'onlinedocumentation-menu':              'mnuOnlineDocumentation',
    'about-menu':                            'mnuAbout',
    # service level menu
    'sl-notset-menu':                        'mnuNotSet1',
    'none-menu':                             'mnuNone',
    'premium-menu':                          'mnuPremium',
    'standard-menu':                         'mnuStandard',
    'standard-menu-7':                       'mnuSTANDARD',
    'self-support-menu':                     'mnuSelf-Support',
    'self-support-menu-7':                   'mnuSELF-SUPPORT',
    'layered-menu':                          'mnuLayered',

    # release version menu
    'rv-notset-menu':                       'mnuNotSet',
    '6.1-menu':                             'mnu61',
    '6.2-menu':                             'mnu62',
    '6.3-menu':                             'mnu63',
    '6.4-menu':                             'mnu64',
    '6.5-menu':                             'mnu65',
    '7.0-menu':                             'mnu70',
    '6server-menu':                         'mnu6Server',
    '7server-menu':                         'mnu7Server',
    # import cert, certificates select menu
    'certificate-menu':                     'mnuCertificates',
    ######## Checkbox Element ########
    'manual-attach-checkbox':                'chkautobind',
    'proxy-checkbox':                        'chkProxyCheckbox',
    'match-system-checkbox':                 'chkMatchSystem',
    'match-installed-checkbox':              'chkMatchInstalled',
    'do-not-overlap-checkbox':               'chkDoNotOverlap',
    # ##firstboot checkbox for RHEL6
    'firstboot-manual-checkbox':             'chkautobind',
    'firstboot_activationkey-checkbox':      'chkIwilluseanActivationKey',

    ######## Label Element ########
    'label-org':                             'lblOrganizationValue',
    'label-id':                              'lblSystemIdentityValue',
    'nosubscriptions-in-filter-label':       'lblNosubscriptionsmatchcurrentfilters',
    'import-cert-success-label':                 'lblCertificateimportwassuccessful',
    'register-error-label':                      'lblUnabletoregisterthesystemInvalidusernameorpasswordTocreatealogin,pleasevisithttps//wwwredhatcom/wapps/ugc/registerhtmlPleasesee/var/log/rhsm/rhsmlogformoreinformation',
    'search-subscriptions-hint-label':           'lbl2applied',
    'error-user-label':                          'lblUserusertestisnotabletoregisterwithanyorgs',
    'warning-classic-already-label':             'lblWARNINGThissystemhasalreadybeenregisteredwithRedHatusingRHNClassicThetoolyouareusingisattemptingtore-registerusingRedHatSubscriptionManagementtechnologyRedHatrecommendsthatcustomersonlyregisteronceTolearnhowtounregisterfromeitherservicepleaseconsultthisKnowledgeBaseArticlehttps//accessredhatcom/kb/docs/DOC-45563',
    # firstboot label
    'firstboot-registeration-warning-label':     'lblYoursystemwasregisteredforupdatesduringinstallation',
    'firstboot_creat_user-label':                'lblYoumustcreatea\'username\'forregular(non-administrative)useofyoursystemTocreateasystem\'username\',pleaseprovidetheinformationrequestedbelow',
    'firstboot-skip-auto-label':                 'lblYouhaveoptedtoskipauto-attach',
    'firstboot-classic-reviewsubscription-label':      'lblReviewSubscription',
    'firstboot-classic-finishupdate-label':            'lblFinishUpdatesSetup',
    # rhn_classic label
    'classic-software-update-label':             'lblSetUpSoftwareUpdates',
    'classic-choose-service-label':              'lblChooseService',
    'classic-redhat-account-label':              'lblRedHatAccount',
    'classic-OS-realeaseversion-label':          'lblOperatingSystemReleaseVersion',
    'classic-create-profile-label':              'lblCreateProfile',
    'classic-review-subscription-label':         'lblReviewSubscription',

    ######## Combobox Element ########
    'service-level-combobox':                    'cboslaselectioncombobox',
    'release-version-combobox':                  'cboreleaseselectioncombobox',

#     'service-level-notset-combobox':             'cboNotSet',
#     'service-level-premium-combobox':            'cboPremium',
#     'service-level-none-combobox':               'cboNone',
#     'release-version-combobox':                  'cbo1',
#     'release-version-6server-combobox':          'cbo6Server',

    ######## Other Element ########
    'register-progressbar':                      'pbarregisterprogressbar',
    }

    os_serial = ""
    def __init__(self):
        if self.os_serial == "":
            self.os_serial = self.get_os_serials()

    def get_locator(self, name):
        if name + "-" + self.os_serial in self.element_locators.keys():
            return self.element_locators[name + "-" + self.os_serial]
        else:
            return self.element_locators[name]
