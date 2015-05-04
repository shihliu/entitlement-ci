package com.redhat.ci;

import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.Connection;
import javax.jms.Destination;
import javax.jms.ExceptionListener;
import javax.jms.JMSException;
import javax.jms.MessageConsumer;
import javax.jms.MessageListener;
import javax.jms.Session;
import javax.security.auth.Subject;
import javax.security.auth.login.LoginContext;
import javax.security.auth.login.LoginException;

import com.redhat.ci.auth.CIConfiguration;
import com.redhat.ci.auth.CIContext;
import com.redhat.ci.auth.CILoginCallbackHandler;
import com.redhat.ci.auth.CIPrivilegedAction;

public class MessageOnboarder implements Runnable {
	private static final Logger log = Logger.getLogger(MessageOnboarder.class.getName());

	private static final String CONFIG_URI = "uri";
	private static final String CONFIG_ADDRESS = "address";
	private static final String CONFIG_USERNAME = "username";
	private static final String CONFIG_PASSWORD = "password";
	private static final String CONFIG_APPLICATION = "application";
	private static final String CONFIG_SELECTOR = "selector";
	private static final String CONFIG_INTERVAL_SECONDS = "seconds";

	private Properties props;
	private MessageListener listener;
	private boolean running = false;

	Connection connection;
	MessageConsumer consumer;
	CIContext context;
	
	public MessageOnboarder(Properties props, MessageListener listener) {
		this.props = props;
		this.listener = listener;
	}

	public void run() {
		running = true;
		log.info("Connecting to application '" + props.getProperty(CONFIG_APPLICATION) + "' address:\n" + props.getProperty(CONFIG_ADDRESS));

		try {
			startup();
			Integer sleep_secs = Integer.parseInt(props.getProperty(CONFIG_INTERVAL_SECONDS));
			while (running) {
				Thread.sleep(sleep_secs*1000);
			}
		} catch (LoginException e) {
			log.log(Level.SEVERE, "CI login authentication failed.", e);
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandled exception in run", e);
		} finally {
			try {
				shutdown();
			} catch (Exception e) {
			}			
		}
	}

	public void stop() {
		running = false;
	}

	private void startup() throws Exception {
		LoginContext lc = new LoginContext(CIConfiguration.CI_APPLICATION_NAME, 
				new Subject(), 
				new CILoginCallbackHandler(props.getProperty(CONFIG_USERNAME), props.getProperty(CONFIG_PASSWORD)), 
				new CIConfiguration());
		lc.login();
		CIContext context = CIContext.getCIContext(props.getProperty(CONFIG_URI), props.getProperty(CONFIG_ADDRESS));
		Connection connection = Subject.doAs(lc.getSubject(), new CIPrivilegedAction(context));
		connection.setExceptionListener(new OnboarderExceptionListener());
		Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
		Destination destination = (Destination) context.lookup(CIContext.DESTINATION_NAME);
		MessageConsumer consumer;
		if (props.getProperty(CONFIG_SELECTOR) != null) {
			consumer = session.createConsumer(destination, props.getProperty(CONFIG_SELECTOR));
		} else {
			consumer = session.createConsumer(destination);
		}
		consumer.setMessageListener(listener);
		connection.start();
	}
	
	private void shutdown() throws Exception {
		if (consumer != null) {
			consumer.close();
		}
		if (connection != null) {
			connection.close();
		} 
		if (context != null) {
			context.close();
		}
	}
	
	private void restart() throws Exception {
		shutdown();
		startup();
	}
	
	private class OnboarderExceptionListener implements ExceptionListener {

		public void onException(JMSException arg0) {
			try {
				log.log(Level.WARNING, "Exception onboarder, going to restart.\n", arg0);
				restart();
			} catch (Exception e) {
				log.log(Level.SEVERE, "Unhandled exception in onException:\n", e);
			}
		}
		
	}
}
