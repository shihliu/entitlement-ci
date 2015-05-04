package com.redhat.ci.brew;

import com.redhat.ci.MessageSource;

public class BrewMessageSource extends MessageSource {
	private static final String BREW_PROPERTIES = "com/redhat/ci/brew/brew.properties";
	private static final String CONFIG_XMLRPC = "xmlrpc";
	
	public BrewMessageSource() {
		super(BREW_PROPERTIES);
		setListener(new BrewListener(getProperties().getProperty(CONFIG_XMLRPC)));
	}
}
