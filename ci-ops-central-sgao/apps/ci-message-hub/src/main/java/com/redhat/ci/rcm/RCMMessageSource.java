package com.redhat.ci.rcm;

import com.redhat.ci.MessageSource;

public class RCMMessageSource extends MessageSource {
	private static final String RCM_PROPERTIES = "com/redhat/ci/rcm/rcm.properties";

	public RCMMessageSource() {
		super(RCM_PROPERTIES);
		setListener(new RCMListener());
	}
}
