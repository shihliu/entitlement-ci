package com.redhat.utils;

import java.sql.Time;
import java.util.Enumeration;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.DeliveryMode;
import javax.jms.Destination;
import javax.jms.MapMessage;
import javax.jms.Message;
import javax.jms.TextMessage;

import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;

public class MessageUtils {

    private static final Logger log = Logger.getLogger(MessageUtils.class.getName());

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

    private static String formatHeaders (Message message) {
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
