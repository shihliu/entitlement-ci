import xml.etree.ElementTree as XML


def ci_publisher(parser, xml_parent, data):
    """yaml: ci-publisher
    Publishes messages on CI message bus.
    Requires the Jenkins `ci-trigger Plugin.
    <com.redhat.jenkins.plugins.ci">`_

    :arg string message-type: valid JJB YAML message type (default '')
    :arg string message-content: message content (default '')
    :arg string message-properties: KEY=value pairs, one per line (default '')
    """
    data = data if data else {}
    st = XML.SubElement(
        xml_parent,
        'com.redhat.jenkins.plugins.ci.CINotifier'
    )
    XML.SubElement(st, 'messageType').text = str(data.get('message-type', ''))
    XML.SubElement(st, 'messageContent').text = \
        str(data.get('message-content', ''))
    XML.SubElement(st, 'messageProperties').text = \
        str(data.get('message-properties', ''))
