package com.redhat.ci.rcm;

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

public class RCMListener implements MessageListener {
	private final Logger log = Logger.getLogger(RCMListener.class.getName());

	public void onMessage(Message message) {
		log.info("RCM MESSAGE = \n" + CIMessage.formatMessage(message));
		try {
			ObjectMapper mapper = new ObjectMapper();
			ObjectNode root = mapper.createObjectNode();

			MapMessage mm = (MapMessage) message;

			HashMap<String, Object> props = new HashMap<String, Object>();
			props.put("CI_TYPE", message.getStringProperty("service").toLowerCase());

			@SuppressWarnings("unchecked")
			Enumeration<String> e = mm.getMapNames();
			while (e.hasMoreElements()) {
				String field = e.nextElement();
				root.put(field, Convert(mapper.convertValue(mm.getObject(field), JsonNode.class)));
			}

			// Copy over all the RCM message properties.
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
