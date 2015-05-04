package com.redhat.jenkins.plugins.ci;

import hudson.Extension;
import hudson.Launcher;
import hudson.model.BuildListener;
import hudson.model.Result;
import hudson.model.AbstractBuild;
import hudson.model.AbstractProject;
import hudson.tasks.BuildStepDescriptor;
import hudson.tasks.BuildStepMonitor;
import hudson.tasks.Notifier;
import hudson.tasks.Publisher;
import hudson.util.ListBoxModel;

import java.io.IOException;
import java.io.StringReader;
import java.util.Enumeration;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jms.Connection;
import javax.jms.Destination;
import javax.jms.JMSException;
import javax.jms.MessageProducer;
import javax.jms.Session;
import javax.jms.TextMessage;

import net.sf.json.JSONObject;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.apache.commons.lang.text.StrSubstitutor;
import org.kohsuke.stapler.DataBoundConstructor;
import org.kohsuke.stapler.QueryParameter;
import org.kohsuke.stapler.StaplerRequest;

import com.redhat.utils.MessageUtils;

public class CINotifier extends Notifier {

    private static final Logger log = Logger.getLogger(CINotifier.class.getName());

    private static final String JSON_TYPE = "application/json";

    private enum MESSAGE_TYPE {
        CodeQualityChecksDone("code-quality-checks-done"),
        ComponentBuildDone("component-build-done"),
        EarlyPerformanceTestingDone("early-performance-testing-done"),
        EarlySecurityTestingDone("early-security-testing-done"),
        ImageUploaded("image-uploaded"),
        FunctionalTestCoverageDone("functional-test-coverage-done"),
        FunctionalTestingDone("functional-testing-done"),
        NonfunctionalTestingDone("nonfunctional-testing-done"),
        OotbTestingDone("ootb-testing-done"),
        PeerReviewDone("peer-review-done"),
        ProductAcceptedForReleaseTesting("product-accepted-for-release-testing"),
        ProductBuildDone("product-build-done"),
        ProductBuildInStaging("product-build-in-staging"),
        ProductTestCoverageDone("product-test-coverage-done"),
        PullRequest("pull-request"),
        SecurityChecksDone("security-checks-done"),
        Tier0TestingDone("tier-0-testing-done"),
        Tier1TestingDone("tier-1-testing-done"),
        Tier2IntegrationTestingDone("tier-2-integration-testing-done"),
        Tier2ValidationTestingDone("tier-2-validation-testing-done"),
        Tier3TestingDone("tier-3-testing-done"),
        UnitTestCoverageDone("unit-test-coverage-done"),
        UpdateDefectStatus("update-defect-status");

        private String message;

        MESSAGE_TYPE(String value) {
            this.message = value;
        }

        public String getMessage() {
            return message;
        }

        public static MESSAGE_TYPE fromString(String value) {
            for (MESSAGE_TYPE t : MESSAGE_TYPE.values()) {
                if (value.equalsIgnoreCase(t.name())) {
                    return t;
                }
            }
            return null;
        }

        public String toDisplayName() {
            String v = name();
            if (v == null || v.isEmpty())
                return v;

            StringBuilder result = new StringBuilder();
            result.append(v.charAt(0));
            for (int i = 1; i < v.length(); i++) {
                if (Character.isUpperCase(v.charAt(i))) {
                    result.append(" ");
                }
                result.append(v.charAt(i));
            }
            return result.toString();
        }
    }

    private MESSAGE_TYPE messageType;
    private String messageProperties;
    private String messageContent;

    public MESSAGE_TYPE getMessageType() {
        return messageType;
    }
    public void setMessageType(MESSAGE_TYPE messageType) {
        this.messageType = messageType;
    }
    public String getMessageProperties() {
        return messageProperties;
    }
    public void setMessageProperties(String messageProperties) {
        this.messageProperties = messageProperties;
    }
    public String getMessageContent() {
        return messageContent;
    }
    public void setMessageContent(String messageContent) {
        this.messageContent = messageContent;
    }

    @DataBoundConstructor
    public CINotifier(final MESSAGE_TYPE messageType, final String messageProperties, final String messageContent) {
        super();
        this.messageType = messageType;
        this.messageProperties = messageProperties;
        this.messageContent = messageContent;
    }

    //	public static final DescriptorImpl DESCRIPTOR = new DescriptorImpl();

    @Override
    public DescriptorImpl getDescriptor() {
        return (DescriptorImpl) super.getDescriptor();
    }

    public BuildStepMonitor getRequiredMonitorService() {
        return BuildStepMonitor.NONE;
    }

    public boolean needsToRunAfterFinalized() {
        return true;
    }

    @Override
    public boolean perform(AbstractBuild<?, ?> build, Launcher launcher, BuildListener listener) throws InterruptedException, IOException {
        log.info("Sending CI message for job '" + build.getProject().getName() + "'.");
        GlobalCIConfiguration config = GlobalCIConfiguration.get();

        Connection connection = null;
        Session session = null;
        MessageProducer publisher = null;

        try {
            String user = config.getUser();
            String password = config.getPassword().getPlainText();
            String broker = config.getBroker();
            String topic = config.getTopic();

            ActiveMQConnectionFactory connectionFactory = new ActiveMQConnectionFactory(user, password, broker);
            connection = connectionFactory.createConnection();
            connection.start();

            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
            Destination destination = session.createTopic(topic);
            publisher = session.createProducer(destination);

            TextMessage message;
            message = session.createTextMessage("");
            message.setJMSType(JSON_TYPE);

            message.setStringProperty("CI_NAME", build.getProject().getName());
            message.setStringProperty("CI_TYPE", messageType.getMessage());
            message.setStringProperty("CI_STATUS", (build.getResult()== Result.SUCCESS ? "passed" : "failed"));

            StrSubstitutor sub = new StrSubstitutor(build.getEnvironment(listener));

            if (messageProperties != null && !messageProperties.trim().equals("")) {
                Properties props = new Properties();
                props.load(new StringReader(messageProperties));
                @SuppressWarnings("unchecked")
                Enumeration<String> e = (Enumeration<String>) props.propertyNames();
                while (e.hasMoreElements()) {
                    String key = e.nextElement();
                    message.setStringProperty(key, sub.replace(props.getProperty(key)));
                }
            }

            message.setText(sub.replace(messageContent));

            publisher.send(message);
            log.info("Sent " + messageType.toString() + " message for job '" + build.getProject().getName() + "':\n" + MessageUtils.formatMessage(message));

        } catch (Exception e) {
            log.log(Level.SEVERE, "Unhandled exception in perform.", e);
        } finally {
            if (publisher != null) {
                try {
                    publisher.close();
                } catch (JMSException e) {
                }
            }
            if (session != null) {
                try {
                    session.close();
                } catch (JMSException e) {
                }
            }
            if (connection != null) {
                try {
                    connection.close();
                } catch (JMSException e) {
                }
            }
        }
        return true;
    }

    @Extension
    public static class DescriptorImpl extends BuildStepDescriptor<Publisher> {
        private MESSAGE_TYPE messageType;
        private String messageProperties;
        private String messageContent;

        public DescriptorImpl() {
            load();
        }

        public MESSAGE_TYPE getMessageType() {
            return messageType;
        }

        public void setMessageType(MESSAGE_TYPE messageType) {
            this.messageType = messageType;
        }

        public String getMessageProperties() {
            return messageProperties;
        }

        public void setMessageProperties(String messageProperties) {
            this.messageProperties = messageProperties;
        }

        public String getMessageContent() {
            return messageContent;
        }

        public void setMessageContent(String messageContent) {
            this.messageContent = messageContent;
        }

        @SuppressWarnings("rawtypes")
        @Override
        public boolean isApplicable(Class<? extends AbstractProject> arg0) {
            return true;
        }

        @Override
        public CINotifier newInstance(StaplerRequest sr) {
            setMessageType(MESSAGE_TYPE.fromString(sr.getParameter("messageType")));
            setMessageProperties(sr.getParameter("messageProperties"));
            setMessageContent(sr.getParameter("messageContent"));
            return new CINotifier(getMessageType(), getMessageProperties(), getMessageContent());
        }

        @Override
        public boolean configure(StaplerRequest sr, JSONObject formData) throws FormException {
            setMessageType(MESSAGE_TYPE.fromString(formData.optString("messageType")));
            setMessageProperties(formData.optString("messageProperties"));
            setMessageContent(formData.optString("messageContent"));
            try {
                new CINotifier(getMessageType(), getMessageProperties(), getMessageContent());
            } catch (Exception e) {
                throw new FormException("Failed to initialize notifier - check your global notifier configuration settings", e, "");
            }
            save();
            return super.configure(sr, formData);
        }

        @Override
        public String getDisplayName() {
            return "CI Notifier";
        }

        public ListBoxModel doFillMessageTypeItems(@QueryParameter String messageType) {
            MESSAGE_TYPE current = MESSAGE_TYPE.fromString(messageType);
            ListBoxModel items = new ListBoxModel();
            for (MESSAGE_TYPE t : MESSAGE_TYPE.values()) {
                items.add(new ListBoxModel.Option(t.toDisplayName(), t.name(), (t == current) || items.size() == 0));
            }
            return items;
        }
    }
}
