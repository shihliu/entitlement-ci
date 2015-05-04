package com.redhat.ci;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.MessageListener;

public abstract class MessageSource {
	private static final Logger log = Logger.getLogger(MessageSource.class.getName());

	private Properties props;
	private MessageListener listener;
	
	public MessageSource(String propfile) {
		props = new Properties();
		InputStream in = getClass().getClassLoader().getResourceAsStream(propfile);
		try {
			props.load(in);
			in.close();
		} catch (IOException e) {
			log.log(Level.SEVERE, "Unhandled exception loading properties file: " + propfile, e);
		}
	}
	
	public void start() {
		MessageOnboarder onboarder = new MessageOnboarder(props, listener);
		new Thread(onboarder).start();
	}
	
	protected Properties getProperties() {
		return props;
	}
	
	protected void setListener(MessageListener listener) {
		this.listener = listener;
	}
}
