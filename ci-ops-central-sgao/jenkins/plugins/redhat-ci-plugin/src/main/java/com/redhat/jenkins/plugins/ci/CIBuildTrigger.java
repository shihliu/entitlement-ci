package com.redhat.jenkins.plugins.ci;
import hudson.Extension;
import hudson.model.Item;
import hudson.model.ParameterValue;
import hudson.model.AbstractProject;
import hudson.model.ParameterDefinition;
import hudson.model.ParametersAction;
import hudson.model.ParametersDefinitionProperty;
import hudson.model.StringParameterValue;
import hudson.triggers.Trigger;
import hudson.triggers.TriggerDescriptor;

import java.net.Inet4Address;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.WeakHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.Connection;
import javax.jms.ExceptionListener;
import javax.jms.JMSException;
import javax.jms.MapMessage;
import javax.jms.Message;
import javax.jms.MessageListener;
import javax.jms.Session;
import javax.jms.TextMessage;
import javax.jms.Topic;
import javax.jms.TopicSubscriber;

import jenkins.model.Jenkins;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.apache.commons.lang.StringUtils;
import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;
import org.kohsuke.stapler.DataBoundConstructor;

import com.redhat.jenkins.plugins.Messages;
import com.redhat.utils.MessageUtils;

public class CIBuildTrigger extends Trigger<AbstractProject<?, ?>> {

	public static final String PLUGIN_APPID = "remote-build";

	private static final String PLUGIN_NAME = Messages.PluginName();

	private static final Logger log = Logger.getLogger(CIBuildTrigger.class.getName());

	public static final transient WeakHashMap<String, CITriggerInfo> triggerInfo = new WeakHashMap<String, CITriggerInfo>();;
	private String selector;

	@DataBoundConstructor
	public CIBuildTrigger(String selector) {
		super();
		this.selector = StringUtils.stripToNull(selector);
	}

	@Override
	public void start(AbstractProject<?, ?> project, boolean newInstance) {
		super.start(project, newInstance);
		connect();
	}

	@Override
	public void stop() {
		super.stop();
		disconnect();
	}

	protected Boolean connect() {
		disconnect();
		log.info("Subscribing job '" + job.getFullName() + "' to CI topic with selector: " + selector);
		GlobalCIConfiguration config = GlobalCIConfiguration.get();

		String user = config.getUser();
		String password = config.getPassword().getPlainText();
		String broker = config.getBroker();
		String topic = config.getTopic();

		if (user != null && password != null && topic != null && broker != null) {
			try {
				ActiveMQConnectionFactory connectionFactory = new ActiveMQConnectionFactory(user, password, broker);
				Connection connection = connectionFactory.createConnection();

				connection.setExceptionListener(new CIExceptionListener());
				connection.setClientID(Inet4Address.getLocalHost().getHostAddress() + "_" + job.getFullName());
				Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
				Topic destination = session.createTopic(topic);

				TopicSubscriber subscriber = session.createDurableSubscriber(destination, job.getFullName(), selector, false);
				subscriber.setMessageListener(new CIMessageListener(job.getFullName()));
				connection.start();

                triggerInfo.put(job.getFullName(), new CITriggerInfo(connection, subscriber));
                return true;
			} catch (Exception e) {
				log.log(Level.SEVERE, "Unhandled exception in connect", e);
			}
		}
		return false;
	}

	protected void disconnect() {
		log.info("Unsubcribing job '" + job.getFullName() + "' from the CI topic.");
		try {
			CITriggerInfo i = triggerInfo.get(job.getFullName());
			if (i != null && i.getConnection() != null) {
			    try {
			        i.getConnection().close();
			    } catch (Exception ce) {
		            log.log(Level.SEVERE, "Unhandled exception closing connection in disconnect", ce);
			    } finally {
			        i.setConnection(null);
			    }
			}
			if (i != null && i.getSubscriber() != null) {
                try {
                    i.getSubscriber().close();
                } catch (Exception se) {
                    log.log(Level.SEVERE, "Unhandled exception closing subscriber in disconnect", se);
                } finally {
                    i.setSubscriber(null);
                }
			}
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandled exception in disconnect", e);
		} finally {
		    triggerInfo.remove(job.getFullName());
		}
	}

	public String getSelector() {
		return selector;
	}

	public void setSelector(String selector) {
		this.selector = selector;
	}

	public void scheduleBuild(List<ParameterValue> ciParams) {
		List<ParameterValue> parameters = getUpdatedParameters(ciParams, getDefinitionParameters(job));
		job.scheduleBuild2(0, new CIBuildCause(), new ParametersAction(parameters));
	}

	private List<ParameterValue> getUpdatedParameters(List<ParameterValue> ciParams, List<ParameterValue> definedParams) {
		HashMap<String, ParameterValue> newParams = new HashMap<String, ParameterValue>();
		for (ParameterValue def : definedParams) {
			newParams.put(def.getName().toLowerCase(), def);
		}
		for (ParameterValue p : ciParams) {
			newParams.put(p.getName().toLowerCase(), p);
		}
		return new ArrayList<ParameterValue>(newParams.values());
	}

	private List<ParameterValue> getDefinitionParameters(AbstractProject<?, ?> project) {
		List<ParameterValue> parameters = new ArrayList<ParameterValue>();
		ParametersDefinitionProperty properties = project.getProperty(ParametersDefinitionProperty.class);

		if (properties != null) {
			for (ParameterDefinition paramDef : properties.getParameterDefinitions()) {
				ParameterValue param = paramDef.getDefaultParameterValue();
				if (param != null) {
					parameters.add(param);
				}
			}
		}

		return parameters;
	}

	@Override
	public DescriptorImpl getDescriptor() {
	    return (DescriptorImpl)super.getDescriptor();
	}

	public static CIBuildTrigger findTrigger(String fullname) {
        Jenkins jenkins = Jenkins.getInstance();
        AbstractProject<?, ?> p = jenkins.getItemByFullName(fullname, AbstractProject.class);
        if (p != null) {
            return p.getTrigger(CIBuildTrigger.class);
        }
        return null;
	}

	@Extension
	public static class DescriptorImpl extends TriggerDescriptor {

		@Override
		public boolean isApplicable(Item item) {
			return true;
		}

		@Override
		public String getDisplayName() {
			return PLUGIN_NAME;
		}
	}

	private class CIMessageListener implements MessageListener {
		private final Logger LOGGER = Logger.getLogger(CIMessageListener.class.getName());
		private String fullname;

		public CIMessageListener(String fullname) {
			this.fullname = fullname;
		}

		public void onMessage(Message message) {
			try {
				String text = "";
				if (message instanceof MapMessage) {
					MapMessage mm = (MapMessage) message;
					ObjectMapper mapper = new ObjectMapper();
					ObjectNode root = mapper.createObjectNode();

					@SuppressWarnings("unchecked")
					Enumeration<String> e = mm.getMapNames();
					while (e.hasMoreElements()) {
						String field = e.nextElement();
						root.put(field, mapper.convertValue(mm.getObject(field), JsonNode.class));
					}
					text = mapper.writer().writeValueAsString(root);
				} else if (message instanceof TextMessage) {
					TextMessage tm = (TextMessage) message;
					text = tm.getText();
				} else {
					LOGGER.log(Level.SEVERE, "Unsupported message type:\n" + MessageUtils.formatMessage(message));
					return;
				}

				if (text == null) {
					text = "";
				}
				ArrayList<ParameterValue> params = new ArrayList<ParameterValue>();
				params.add(new StringParameterValue("CI_MESSAGE", text));

				@SuppressWarnings("unchecked")
				Enumeration<String> e = message.getPropertyNames();
				while (e.hasMoreElements()) {
					String s = e.nextElement();
					if (message.getStringProperty(s) != null) {
						params.add(new StringParameterValue(s, message.getObjectProperty(s).toString()));
					}
				}

				CIBuildTrigger trigger = findTrigger(fullname);
				if (trigger != null) {
	                LOGGER.info("Scheduling job '" + fullname + "' based on message:\n" + MessageUtils.formatMessage(message));
				    trigger.scheduleBuild(params);
				} else {
				    LOGGER.log(Level.WARNING, "Unable to find CIBuildTrigger for '" + fullname + "'.");
				}
			} catch (Exception e) {
				LOGGER.log(Level.SEVERE, "Unhandled exception processing message:\n" + MessageUtils.formatMessage(message), e);
			}
		}
	}

	private class CIExceptionListener implements ExceptionListener {

		public void onException(JMSException e) {
			log.log(Level.SEVERE, "CIExceptionListener - unhandled exception:\n", e);
			disconnect();
    		while (true) {
    		    try {
    		        if (connect()) {
    		            break;
    		        }
    		    } catch (Exception ex) {
    		        log.log(Level.SEVERE, "CIExceptionListener - exception trying to re-establish connection.", ex);
    		    }

    		    try {
    		        Thread.sleep(2000);
    		    } catch (InterruptedException ex) {
    		        Thread.currentThread().interrupt();
    		    }
			}
		}
	}
}