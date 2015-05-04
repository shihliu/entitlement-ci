package com.redhat.ci;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Time;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.Connection;
import javax.jms.DeliveryMode;
import javax.jms.Destination;
import javax.jms.JMSException;
import javax.jms.MapMessage;
import javax.jms.Message;
import javax.jms.MessageProducer;
import javax.jms.Session;
import javax.jms.TextMessage;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;

public class CIMessage {
	private static final Logger log = Logger.getLogger(MessageSource.class.getName());

	private static final String JSON_TYPE = "application/json";

	private static final String CI_PROPERTIES = "com/redhat/ci/ci.properties";
	private static final String CONFIG_BROKER = "broker";
	private static final String CONFIG_TOPIC = "topic";
	private static final String CONFIG_USERNAME = "username";
	private static final String CONFIG_PASSWORD = "password";

	private static CIMessage ref;

	private Properties props;
	private MessageProducer publisher;
	private Session session;
	private Connection connection;

	private CIMessage() {
		props = new Properties();
		InputStream in = getClass().getClassLoader().getResourceAsStream(CI_PROPERTIES);
		try {
			props.load(in);
			in.close();
		} catch (IOException e) {
			log.log(Level.SEVERE, "Unhandled exception loading properties file: " + CI_PROPERTIES, e);
		}
		try {
			String user = props.getProperty(CONFIG_USERNAME);
			String password = props.getProperty(CONFIG_PASSWORD);
			String broker = props.getProperty(CONFIG_BROKER);
			String topic = props.getProperty(CONFIG_TOPIC);

			ActiveMQConnectionFactory connectionFactory = new ActiveMQConnectionFactory(user, password, broker);
			connection = connectionFactory.createConnection();
			connection.start();

			session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
			Destination destination = session.createTopic(topic);
			publisher = session.createProducer(destination);
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandled exception in run CIMessage constructor.", e);
		}
	}

	private void shutdown() {
		try {
			if (publisher != null) {
				publisher.close();
				publisher = null;
			}
			if (session != null) {
				session.close();
				session = null;
			}
			if (connection != null) {
				connection.close();
				connection = null;
			}
			ref = null;
		} catch (Exception e) {
			log.warning("Unhandled exception in shutdown.");
		}
	}

	private Session getSession() {
		return session;
	}

	private MessageProducer getPublisher() {
		return publisher;
	}

	private void sendMessage(HashMap<String, Object> props, String content) throws JMSException {
		TextMessage message;
		message = getSession().createTextMessage(content);
		message.setJMSType(JSON_TYPE);

		for (String p : props.keySet()) {
			message.setObjectProperty(p, props.get(p));
		}
		log.info("SENDING CI MESSAGE:\n" + formatMessage(message));
		getPublisher().send(message);
	}

	private static CIMessage getInstance() {
		if (ref == null) {
			ref = new CIMessage();
		}
		return ref;
	}

	public static void send(HashMap<String, Object> props, String content) {
		CIMessage obj = CIMessage.getInstance();
		try {
			obj.sendMessage(props, content);
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandled exception in send, retrying....", e);
			obj.shutdown();
			obj = CIMessage.getInstance();
			try {
				obj.sendMessage(props, content);
			} catch (Exception j) {
				log.log(Level.SEVERE, "Unhandled exception in send.", e);
			}
		}
	}

	public static String formatMessage (Message message) {
		StringBuilder sb = new StringBuilder();

		try {
			String headers = formatHeaders(message);
			if (headers.length() > 0) {
				sb.append("Message Headers:\n");
				sb.append(headers);
			}

			sb.append("Message Properties:\n");
			@SuppressWarnings("unchecked")
			Enumeration<String> propNames = message.getPropertyNames();
			while (propNames.hasMoreElements()) {
				String propertyName = propNames.nextElement ();
				sb.append("  ");
				sb.append(propertyName);
				sb.append(": ");
				if (message.getObjectProperty(propertyName) != null) {
				    sb.append(message.getObjectProperty (propertyName).toString());
				}
				sb.append("\n");
			}

			sb.append("Message Content:\n");
			if (message instanceof TextMessage) {
				sb.append(((TextMessage) message).getText());
			} else if (message instanceof MapMessage) {
				MapMessage mm = (MapMessage) message;
				ObjectMapper mapper = new ObjectMapper();
				ObjectNode root = mapper.createObjectNode();

				@SuppressWarnings("unchecked")
				Enumeration<String> e = mm.getMapNames();
				while (e.hasMoreElements()) {
					String field = e.nextElement();
					root.put(field, mapper.convertValue(mm.getObject(field), JsonNode.class));
				}
				sb.append(mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
			} else {
				sb.append("  Unhandled message type: " + message.getJMSType());
			}
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unable to format message:", e);
		}

		return sb.toString();
	}

    public static String formatHeaders (Message message) {
        Destination  dest = null;
        int delMode = 0;
        long expiration = 0;
        Time expTime = null;
        int priority = 0;
        String msgID = null;
        long timestamp = 0;
        Time timestampTime = null;
        String correlID = null;
        Destination replyTo = null;
        boolean redelivered = false;
        String type = null;

        StringBuilder sb = new StringBuilder();
        try {

            try {
                dest = message.getJMSDestination();
                sb.append("  JMSDestination: ");
                sb.append(dest);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSDestination header\n", e);
            }

            try {
                delMode = message.getJMSDeliveryMode();
                if (delMode == DeliveryMode.NON_PERSISTENT) {
                    sb.append("  JMSDeliveryMode: non-persistent\n");
                } else if (delMode == DeliveryMode.PERSISTENT) {
                    sb.append("  JMSDeliveryMode: persistent\n");
                } else {
                    sb.append("  JMSDeliveryMode: neither persistent nor non-persistent; error\n");
                }
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSDeliveryMode header\n", e);
            }

            try {
                expiration = message.getJMSExpiration();
                if (expiration != 0) {
                    expTime = new Time(expiration);
                    sb.append("  JMSExpiration: ");
                    sb.append(expTime);
                    sb.append("\n");
                } else {
                    sb.append("  JMSExpiration: 0\n");
                }
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSExpiration header\n", e);
            }

            try {
                priority = message.getJMSPriority();
                sb.append("  JMSPriority: ");
                sb.append(priority);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSPriority header\n", e);
            }

            try {
                msgID = message.getJMSMessageID();
                sb.append("  JMSMessageID: ");
                sb.append(msgID);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSMessageID header\n", e);
            }

            try {
                timestamp = message.getJMSTimestamp();
                if (timestamp != 0) {
                    timestampTime = new Time(timestamp);
                    sb.append("  JMSTimestamp: ");
                    sb.append(timestampTime);
                    sb.append("\n");
                } else {
                    sb.append("  JMSTimestamp: 0\n");
                }
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSTimestamp header\n", e);
            }

            try {
                correlID = message.getJMSCorrelationID();
                sb.append("  JMSCorrelationID: ");
                sb.append(correlID);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSCorrelationID header\n", e);
            }

           try {
                replyTo = message.getJMSReplyTo();
                sb.append("  JMSReplyTo: ");
                sb.append(replyTo);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSReplyTo header\n", e);
            }

            try {
                redelivered = message.getJMSRedelivered();
                sb.append("  JMSRedelivered: ");
                sb.append(redelivered);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSRedelivered header\n", e);
            }

            try {
                type = message.getJMSType();
                sb.append("  JMSType: ");
                sb.append(type);
                sb.append("\n");
            } catch (Exception e) {
            	log.log(Level.WARNING, "Unable to generate JMSType header\n", e);
            }

        } catch (Exception e) {
        	log.log(Level.WARNING, "Unable to generate JMS headers\n", e);
        }
        return sb.toString();
    }
}
