package com.redhat.mikeb.test.brew;

import org.apache.xmlrpc.serializer.TypeSerializerImpl;
import org.xml.sax.ContentHandler;
import org.xml.sax.SAXException;

/** A {@link TypeSerializer} for null values.
 */
public class NilSerializer extends TypeSerializerImpl {
        /** Tag name of a nil value. */

    public static final String NIL_TAG = "nil";

    public void write(ContentHandler pHandler, Object pObject) throws SAXException {
        pHandler.startElement("", VALUE_TAG, VALUE_TAG, ZERO_ATTRIBUTES);
        pHandler.startElement("", NIL_TAG, NIL_TAG, ZERO_ATTRIBUTES);
        pHandler.endElement("", NIL_TAG, NIL_TAG);
        pHandler.endElement("", VALUE_TAG, VALUE_TAG);
    }
}