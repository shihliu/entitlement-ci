package com.redhat.ci.errata;

import com.redhat.ci.MessageSource;

public class ErrataMessageSource extends MessageSource {
	private static final String ERRATA_PROPERTIES = "com/redhat/ci/errata/errata.properties";

	public ErrataMessageSource() {
		super(ERRATA_PROPERTIES);
		setListener(new ErrataListener());
	}
}
