package com.redhat.utils;

import java.net.MalformedURLException;
import java.util.Calendar;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.xml.rpc.ServiceException;

import com.polarion.alm.ws.client.WebServiceFactory;
import com.polarion.alm.ws.client.builder.BuilderWebService;
import com.polarion.alm.ws.client.planning.PlanningWebService;
import com.polarion.alm.ws.client.projects.ProjectWebService;
import com.polarion.alm.ws.client.security.SecurityWebService;
import com.polarion.alm.ws.client.session.SessionWebService;
import com.polarion.alm.ws.client.testmanagement.TestManagementWebService;
import com.polarion.alm.ws.client.tracker.TrackerWebService;

public class PolarionWrapper {

    private static final Logger log = Logger.getLogger(PolarionWrapper.class.getName());

    private static final Integer TIMEOUT_SECONDS = 60;

    private Calendar last;

    private String server;
    private String user;
    private String password;

    private WebServiceFactory ws;
    private BuilderWebService builder;
    private PlanningWebService planning;
    private ProjectWebService project;
    private SecurityWebService security;
    private SessionWebService session;
    private TestManagementWebService testmanagement;
    private TrackerWebService tracker;

    public PolarionWrapper(String server, String user, String password) {
        this.server = server;
        this.user = user;
        this.password = password;

        try {
            this.ws = new WebServiceFactory(getServer());
            this.builder = ws.getBuilderService();
            this.planning = ws.getPlanningService();
            this.project = ws.getProjectService();
            this.security = ws.getSecurityService();
            this.session = ws.getSessionService();
            this.testmanagement = ws.getTestManagementService();
            this.tracker = ws.getTrackerService();
        } catch (MalformedURLException e) {
            log.log(Level.SEVERE, "Unhandled MalformedURLException in PolarionWrapper constructor.", e);
        } catch (ServiceException e) {
            log.log(Level.SEVERE, "Unhandled ServiceException in PolarionWrapper constructor.", e);
        }
    }

    private String getServer() {
        return server;
    }

    private String getUser() {
        return user;
    }

    private String getPassword() {
        return password;
    }

    public BuilderWebService getBuilder() {
        ensureLogin();
        return builder;
    }

    public PlanningWebService getPlanning() {
        ensureLogin();
        return planning;
    }

    public ProjectWebService getProject() {
        ensureLogin();
        return project;
    }

    public SecurityWebService getSecurity() {
        ensureLogin();
        return security;
    }

    public SessionWebService getSession() {
        ensureLogin();
        return session;
    }

    public TestManagementWebService getTestManagement() {
        ensureLogin();
        return testmanagement;
    }

    public TrackerWebService getTracker() {
        ensureLogin();
        return tracker;
    }

    private void ensureLogin() {
        try {
            if (!session.hasSubject() || last == null || (Calendar.getInstance().getTimeInMillis() - last.getTimeInMillis())/1000 > TIMEOUT_SECONDS) {
                this.session.logIn(getUser(), getPassword());
                last = Calendar.getInstance();
            }
        } catch (Exception e) {
            log.log(Level.SEVERE, "Unhandled exception during login.", e);
        }
    }
}
