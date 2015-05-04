package com.redhat.ci;

import com.redhat.ci.brew.BrewMessageSource;
import com.redhat.ci.errata.ErrataMessageSource;
import com.redhat.ci.rcm.RCMMessageSource;

public class Onboard {

	public static void main(String[] args) {
		Boolean startBrew = false;
        Boolean startErrata = false;
        Boolean startRCM = false;
		for (int i = 0; i < args.length; i++) {
			if (args[i].equalsIgnoreCase("-brew")) {
				startBrew = true;
            } else if (args[i].equalsIgnoreCase("-errata")) {
                startErrata = true;
            } else if (args[i].equalsIgnoreCase("-rcm")) {
                startRCM = true;
			}
		}

		if (startBrew) {
			new BrewMessageSource().start();
		}

        if (startErrata) {
            new ErrataMessageSource().start();
        }

        if (startRCM) {
            new RCMMessageSource().start();
        }
	}
}
