import xml.etree.ElementTree as XML


def ci_trigger(parser, xml_parent, data):
    """yaml: ci-trigger
    Triggers the job using CI Build Trigger.
    Requires the Jenkins `ci-trigger Plugin.
    <com.redhat.jenkins.plugins.ci">`_

    :arg string jms-selector: JMS selector. (default '')
    """
    data = data if data else {}
    st = XML.SubElement(
        xml_parent,
        'com.redhat.jenkins.plugins.ci.CIBuildTrigger'
    )
    # spec is a required element, but is not used by the Jenkins CIBuildTrigger
    # creating an empty spec element
    XML.SubElement(st, 'spec').text = ''
    XML.SubElement(st, 'selector').text = str(data.get('jms-selector', ''))
