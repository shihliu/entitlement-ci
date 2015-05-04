package com.redhat.jenkins.plugins.ci;

import javax.jms.Connection;
import javax.jms.TopicSubscriber;

public class CITriggerInfo {
    private Connection connection;
    private TopicSubscriber subscriber;

    public CITriggerInfo(Connection connection, TopicSubscriber subscriber) {
        this.connection = connection;
        this.subscriber = subscriber;
    }

    public Connection getConnection() {
        return connection;
    }
    public void setConnection(Connection connection) {
        this.connection = connection;
    }
    public TopicSubscriber getSubscriber() {
        return subscriber;
    }
    public void setSubscriber(TopicSubscriber subscriber) {
        this.subscriber = subscriber;
    }
}