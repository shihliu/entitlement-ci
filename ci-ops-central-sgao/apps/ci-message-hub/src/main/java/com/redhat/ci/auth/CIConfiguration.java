package com.redhat.ci.auth;

import java.util.HashMap;

import javax.security.auth.login.AppConfigurationEntry;
import javax.security.auth.login.Configuration;

public class CIConfiguration extends Configuration {
	public static final String CI_APPLICATION_NAME = "CI-JMS";

	private static HashMap<String, AppConfigurationEntry[]> configs = new HashMap<String, AppConfigurationEntry[]>();

	static {
		AppConfigurationEntry[] entries = { 
			new AppConfigurationEntry("com.sun.security.auth.module.Krb5LoginModule", 
			                          AppConfigurationEntry.LoginModuleControlFlag.REQUIRED, 
			                          new HashMap<String, String>()) 
		};
		configs.put(CI_APPLICATION_NAME, entries);
	}

	@Override
	public AppConfigurationEntry[] getAppConfigurationEntry(String app) {
		return configs.get(app);
	}
}
