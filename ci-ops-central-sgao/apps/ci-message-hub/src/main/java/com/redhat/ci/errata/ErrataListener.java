package com.redhat.ci.errata;

import java.io.IOException;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.MapMessage;
import javax.jms.Message;
import javax.jms.MessageListener;

import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ArrayNode;
import org.codehaus.jackson.node.JsonNodeFactory;
import org.codehaus.jackson.node.ObjectNode;
import org.codehaus.jackson.node.TextNode;

import com.redhat.ci.CIMessage;

public class ErrataListener implements MessageListener {
	private final Logger log = Logger.getLogger(ErrataListener.class.getName());

	private static final String PROPERTY_ERRATA_STATUS = "ERRATA_STATUS";

	public void onMessage(Message message) {
		log.info("ERRATA MESSAGE = \n" + CIMessage.formatMessage(message));
		try {
			ObjectMapper mapper = new ObjectMapper();
			ObjectNode root = mapper.createObjectNode();

			MapMessage mm = (MapMessage) message;

			HashMap<String, Object> props = new HashMap<String, Object>();
			props.put("CI_TYPE", message.getStringProperty("qpid.subject").toLowerCase());

			@SuppressWarnings("unchecked")
			Enumeration<String> e = mm.getMapNames();
			while (e.hasMoreElements()) {
				String field = e.nextElement();
				root.put(field, Convert(mapper.convertValue(mm.getObject(field), JsonNode.class)));

				if (field.equalsIgnoreCase("to") && root.get(field).getTextValue() != null) {
                    props.put(PROPERTY_ERRATA_STATUS, root.get(field).getTextValue());
                    props.put("to", root.get(field).getTextValue());
                } else if (field.equalsIgnoreCase("from") && root.get(field).getTextValue() != null) {
                    props.put("from", root.get(field).getTextValue());
                } else if (field.equalsIgnoreCase("who") && root.get(field).getTextValue() != null) {
                    props.put("who", root.get(field).getTextValue());
                } else if (field.equalsIgnoreCase("brew_build") && root.get(field).getTextValue() != null) {
                    props.put("brew_build", root.get(field).getTextValue());
                } else if (field.equalsIgnoreCase("errata_id")) {
                    props.put("errata_id", root.get(field).getIntValue());
				}
			}

			// Copy over all the errata message properties.
			@SuppressWarnings("unchecked")
			Enumeration<String> propNames = message.getPropertyNames();
			while (propNames.hasMoreElements()) {
				String propertyName = propNames.nextElement ();
				props.put(propertyName, message.getObjectProperty (propertyName));
			}

			// Now put our message out on the ci exchange.
			CIMessage.send(props, mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandled exception processing message:\n" + message.toString(), e);
		}
	}

	private JsonNode Convert(JsonNode n) {
		if (n != null) {
			if (n.isArray()) {
				ArrayNode a = (ArrayNode)n;
				ArrayNode r = JsonNodeFactory.instance.arrayNode();
				for (int i = 0; i < a.size(); i++) {
					r.add(Convert(a.get(i)));
				}
				return r;
			} else if (n.isObject()) {
				ObjectNode o = (ObjectNode)n;
				ObjectNode r = JsonNodeFactory.instance.objectNode();
				Iterator<String> i = o.getFieldNames();
				while (i.hasNext()) {
					String f = i.next();
					r.put(f, Convert(o.get(f)));
				}
				return r;
			} else if (n.isBinary()) {
				try {
					return new TextNode(new String(n.getBinaryValue()));
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
		return n;

	}
}
