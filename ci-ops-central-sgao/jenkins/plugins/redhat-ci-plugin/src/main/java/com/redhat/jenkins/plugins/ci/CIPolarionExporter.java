package com.redhat.jenkins.plugins.ci;

import hudson.Extension;
import hudson.FilePath;
import hudson.Launcher;
import hudson.model.BuildListener;
import hudson.model.AbstractBuild;
import hudson.model.AbstractProject;
import hudson.tasks.BuildStepDescriptor;
import hudson.tasks.BuildStepMonitor;
import hudson.tasks.Notifier;
import hudson.tasks.Publisher;
import hudson.util.FormValidation;
import hudson.util.Secret;

import java.io.File;
import java.io.FileFilter;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.StringReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.rmi.RemoteException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.servlet.ServletException;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;

import net.sf.json.JSONObject;

import org.apache.axis.AxisFault;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.WildcardFileFilter;
import org.apache.commons.lang3.StringUtils;
import org.kohsuke.stapler.DataBoundConstructor;
import org.kohsuke.stapler.QueryParameter;
import org.kohsuke.stapler.StaplerRequest;
import org.rendersnake.HtmlCanvas;

import com.polarion.alm.ws.client.WebServiceFactory;
import com.polarion.alm.ws.client.session.SessionWebService;
import com.polarion.alm.ws.client.types.Text;
import com.polarion.alm.ws.client.types.projects.Project;
import com.polarion.alm.ws.client.types.projects.User;
import com.polarion.alm.ws.client.types.testmanagement.TestRecord;
import com.polarion.alm.ws.client.types.testmanagement.TestRun;
import com.polarion.alm.ws.client.types.testmanagement.TestsConfiguration;
import com.polarion.alm.ws.client.types.tracker.EnumOptionId;
import com.polarion.alm.ws.client.types.tracker.WorkItem;
import com.redhat.jenkins.plugins.Messages;
import com.redhat.utils.PolarionWrapper;
import com.redhat.xunit.Error;
import com.redhat.xunit.Failure;
import com.redhat.xunit.Testcase;
import com.redhat.xunit.Testsuite;
import com.redhat.xunit.Testsuites;

public class CIPolarionExporter extends Notifier {

    private static final Logger log = Logger.getLogger(CIPolarionExporter.class.getName());

    private static String POLARION_PROJECT_NAME = "polarion.project";
    private static String POLARION_RUN_NAME = "polarion.run";
    private static String POLARION_TEMPLATE_NAME = "polarion.template";

    private static String POLARION_DEFAULT_TEMPLATE_NAME = "Empty";

    private static String MIME_TYPE_TEXT_HTML = "text/html";

    private String server = "https://polarion.engineering.redhat.com/polarion/ws/services/";
    private String user = "ci-ops-central-jenkins";
    private Secret password = Secret.fromString("tQrYdOHhBqOMJi/k");
    private String propfile;
    private String proplist;

    private static SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd hh-mm-ss");

    public CIPolarionExporter() {
    }

    @DataBoundConstructor
    public CIPolarionExporter(final String server, final String user, final Secret password, final String propfile, final String proplist) {
        super();
        this.server = server;
        this.user = user;
        this.password = password;
        this.propfile = propfile;
        this.proplist = proplist;
    }

    public String getServer() {
        return server;
    }

    public void setServer(final String server) {
        this.server = StringUtils.stripToNull(server);
    }

    public String getUser() {
        return user;
    }

    public void setUser(String user) {
        this.user = user;
    }

    public Secret getPassword() {
        return password;
    }

    public void setPassword(Secret password) {
        this.password = password;
    }

    public void setPassword(String password) {
        this.password = Secret.fromString(password);
    }

    public String getPropfile() {
        return propfile;
    }

    public void setPropfile(String propfile) {
        this.propfile = StringUtils.stripToNull(propfile);
    }

    public String getProplist() {
        return proplist;
    }

    public void setProplist(String proplist) {
        this.proplist = StringUtils.stripToNull(proplist);
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
        FilePath ws = build.getWorkspace();
        Properties props = new Properties();

        if (getPropfile() != null) {
            File pf = getPropertiesFilePath(ws, getPropfile());
            if (pf != null) {
                InputStream in = FileUtils.openInputStream(pf);
                try {
                    props.load(in);
                    in.close();
                } catch (Exception e) {
                    log.log(Level.SEVERE, "Unhandled exception loading properties file: " + getPropfile(), e);
                }
            }
        }

        if (getProplist() != null) {
            try {
                props.load(new StringReader(getProplist()));
            } catch (Exception e) {
                log.log(Level.SEVERE, "Unhandled exception loading properties list.", e);
            }
        }


        FileFilter filter = new WildcardFileFilter("*.xml");
        for (FilePath f : ws.list(filter)) {
            exportXunitFile(listener.getLogger(), props, f.getRemote());
        }

        return true;
    }

    private void exportXunitFile(PrintStream logger, Properties props, String filename) {
        logger.println("Starting export of Xunit results to Polarion: " + filename);
        File file = new File(filename);

        try {
            PolarionWrapper p = new PolarionWrapper(getServer(), getUser(), Secret.toString(getPassword()));

            p.getSession().beginTransaction();

            try {
                JAXBContext context = JAXBContext.newInstance(Testsuites.class);
                Unmarshaller um = context.createUnmarshaller();
                Testsuite s = (Testsuite) um.unmarshal(new FileReader(file));
                String pname = getPolarionValue(props, POLARION_PROJECT_NAME, s.getName());
                Project project = p.getProject().getProject(pname);
                if (!project.isUnresolvable()) {
                    logger.println("  Exporting results for Polarion project '" + pname + "'.");
                    User user = p.getProject().getUser(getUser());

                    String trname = getPolarionValue(props, POLARION_RUN_NAME, generateTestRunName(project.getId()));
                    TestRun run = p.getTestManagement().getTestRunById(project.getId(), trname);
                    if (run.isUnresolvable()) {
                        run = p.getTestManagement().getTestRunByUri(p.getTestManagement().createTestRun(project.getId(), trname, getPolarionValue(props, POLARION_TEMPLATE_NAME, POLARION_DEFAULT_TEMPLATE_NAME)));
                    }
                    run.setFinishedOn(Calendar.getInstance());

                    logger.println("  Exporting results to Polarion test run '" + trname + "'.");

                    TestsConfiguration config = p.getTestManagement().getTestsConfiguration(project.getId());

                    for (Testcase c : s.getTestcase()) {
                        String tcname = getPolarionValue(props, c.getName(), c.getName());
                        WorkItem tc = p.getTracker().getWorkItemById(project.getId(), tcname);
                        if (!tc.isUnresolvable()) {

                            TestRecord rec = new TestRecord();
                            rec.setTestCaseURI(tc.getUri());
                            if (c.getSkipped() == null) {
                                rec.setExecuted(Calendar.getInstance());
                                if (c.getTime() != null) {
                                    rec.setDuration(Float.parseFloat(c.getTime()));
                                }
                                rec.setExecutedByURI(user.getUri());

                                Text t = new Text();
                                t.setContentLossy(false);
                                t.setType(MIME_TYPE_TEXT_HTML);
                                HtmlCanvas html = new HtmlCanvas();
                                html = html.p();

                                EnumOptionId eo = new EnumOptionId(config.getResultPassedEnumId());
                                if (c.getFailure() != null && c.getFailure().size() > 0) {
                                    html = html.h4().content("Failure Information");
                                    html = html.ul();
                                    for (Failure f : c.getFailure()) {
                                        html = html.li().p().content(f.getType() + " => " + f.getMessage()).p().content(f.getContent())._li();
                                    }
                                    html = html._ul();
                                    eo.setId(config.getResultFailedEnumId());
                                    logger.println("  Setting test case '" + tcname + "' (" + c.getName() + ") to fail.");
                                } else if (c.getError() != null && c.getError().size() > 0) {
                                    html = html.h4().content("Failure Information")._h2();
                                    html = html.ul();
                                    for (Error e : c.getError()) {
                                        html = html.li().p().content(e.getType() + " => " + e.getMessage()).p().content(e.getContent())._li();
                                    }
                                    html = html._ul();
                                    eo.setId(config.getResultErrorEnumId());
                                    logger.println("  Setting test case '" + tcname + "' (" + c.getName() + ") to error.");
                                } else {
                                    logger.println("  Setting test case '" + tcname + "' (" + c.getName() + ") to pass.");
                                    // Test passed.
                                }

                                if (c.getSystemOut() != null) {
                                    html = html.h4().content("System Output").p().pre().content(StringUtils.join(c.getSystemOut(), "\n"))._p();
                                }

                                if (c.getSystemErr() != null) {
                                    html = html.h4().content("System Error").p().pre().content(StringUtils.join(c.getSystemErr(), "\n"))._p();
                                }

                                html = html._p();

                                t.setContent(html.toHtml());
                                rec.setComment(t);
                                rec.setResult(eo);
                            } else {
                                logger.println("  Setting test case '" + tcname + "' (" + c.getName() + ") to skip.");
                            }

                            p.getTestManagement().addTestRecordToTestRun(run.getUri(), rec);
                        } else {
                            logger.println("  Unable to find test case '" + tcname + "'.");
                        }
                    }
                    run.setStatus(new EnumOptionId(config.getStatusOkEnumId()));
                    p.getTestManagement().updateTestRun(run);
                    p.getSession().endTransaction(false);

                    try {
                        URI uri = new URI(getServer());
                        String url = uri.getScheme() + "://" + uri.getHost() +
                                     (uri.getPort() == -1 ? "" : ":" + uri.getPort()) + "/polarion/#/project/"  +
                                     project.getId() + "/testrun?id=" + URLEncoder.encode(run.getId(), "UTF-8").replace("+", "%20");
                        logger.println("  Polarion test run: " + url);
                    } catch (Exception e) {
                        log.log(Level.WARNING, "Unable to generate URL for test run.", e);
                    }
                } else {
                    logger.println("  Unable to find project '" + pname + "'.");
                }
            } catch (JAXBException j) {
                p.getSession().endTransaction(true);
                j.printStackTrace(logger);
            } catch (FileNotFoundException f) {
                p.getSession().endTransaction(true);
                f.printStackTrace(logger);;
            } catch (IOException i) {
                p.getSession().endTransaction(true);
                i.printStackTrace(logger);;
            } finally {
                p.getSession().endSession();
            }
        } catch (RemoteException r) {
            r.printStackTrace(logger);;
        }
        logger.println("Finished export of Xunit results to Polarion: " + filename);
    }

    private String generateTestRunName(String id) {
        StringBuffer sb = new StringBuffer();
        sb.append(id);
        sb.append(" ");
        sb.append(sdf.format(Calendar.getInstance().getTime()));
        return sb.toString();
    }
    private String getPolarionValue(Properties props, String key, String default_value) {
        // The key parameter should be a Java properties file key.
        return props.getProperty(key, default_value);
    }

    private File getPropertiesFilePath (FilePath workspace, String filename) {
        File f = new File(filename);
        if (!f.exists()) {
            f = new File(workspace.getRemote() + File.separator + filename);
        }
        if (f.exists()) {
            return f;
        }
        return null;
    }

    @Extension
    public static class DescriptorImpl extends BuildStepDescriptor<Publisher> {
        private String server;
        private String user;
        private Secret password;
        private String propfile;
        private String proplist;

        public DescriptorImpl() {
            CIPolarionExporter e = new CIPolarionExporter();
            setServer(e.getServer());
            setUser(e.getUser());
            setPassword(e.getPassword());
            setPropfile(e.getPropfile());
            setProplist(e.getProplist());
            load();
        }

        public String getServer() {
            return server;
        }

        public void setServer(final String server) {
            this.server = StringUtils.stripToNull(server);
        }

        public String getUser() {
            return user;
        }

        public void setUser(String user) {
            this.user = user;
        }

        public Secret getPassword() {
            return password;
        }

        public void setPassword(Secret password) {
            this.password = password;
        }

        public void setPassword(String password) {
            this.password = Secret.fromString(password);
        }

        public String getPropfile() {
            return propfile;
        }

        public void setPropfile(String propfile) {
            this.propfile = StringUtils.stripToNull(propfile);
        }

        public String getProplist() {
            return proplist;
        }

        public void setProplist(String proplist) {
            this.proplist = StringUtils.stripToNull(proplist);
        }

        @SuppressWarnings("rawtypes")
        @Override
        public boolean isApplicable(Class<? extends AbstractProject> arg0) {
            return true;
        }

        @Override
        public CIPolarionExporter newInstance(StaplerRequest sr) {
            setServer(sr.getParameter("server"));
            setUser(sr.getParameter("user"));
            setPassword(sr.getParameter("password"));
            setPropfile(sr.getParameter("propfile"));
            setProplist(sr.getParameter("proplist"));
            return new CIPolarionExporter(getServer(), getUser(), getPassword(), getPropfile(), getProplist());
        }

        @Override
        public boolean configure(StaplerRequest sr, JSONObject formData) throws FormException {
            setServer(formData.optString("server"));
            setUser(formData.optString("user"));
            setPassword(formData.optString("password"));
            setPropfile(formData.optString("propfile"));
            setProplist(formData.optString("proplist"));
            try {
                new CIPolarionExporter(getServer(), getUser(), getPassword(), getPropfile(), getProplist());
            } catch (Exception e) {
                throw new FormException("Failed to initialize Polarion exporter - check your configuration settings", e, "");
            }
            save();
            return super.configure(sr, formData);
        }

        @Override
        public String getDisplayName() {
            return "CI Polarion Exporter";
        }

        public FormValidation doTestConnection(
                @QueryParameter("server") String server,
                @QueryParameter("user") String user,
                @QueryParameter("password") Secret password,
                @QueryParameter("propfile") String propfile,
                @QueryParameter("proplist") String proplist) throws ServletException {
            server = StringUtils.stripToNull(server);
            if (server != null && isValidURL(server)) {
                try {
                    WebServiceFactory ws = new WebServiceFactory(server);
                    SessionWebService session = ws.getSessionService();

                    try {
                        session.logIn(user, Secret.toString(password));
                        return FormValidation.ok(Messages.Success());
                    } catch (AxisFault a) {
                        if (a.getFaultString().contains("Authentication failed.")) {
                            return FormValidation.error(Messages.AuthFailure());
                        }
                        throw a;
                    } finally {
                        if (session != null) {
                            session.endSession();
                        }
                    }
                } catch (Exception e) {
                    log.log(Level.SEVERE, "Unhandled exception in doTestConnection: ", e);
                    return FormValidation.error(Messages.Error() + ": " + e);
                }
            }
            return FormValidation.error(Messages.InvalidURI());
        }

        //        private boolean testConnection(String server, String user, Secret password) throws Exception {
        //            server = StringUtils.stripToNull(server);
        //            if (server != null && isValidURL(server)) {
        //                WebServiceFactory ws = new WebServiceFactory(server);
        //                SessionWebService session = ws.getSessionService();
        //
        //                try {
        //                    session.logIn(user, Secret.toString(password));
        //                } finally {
        //                    if (session != null) {
        //                        session.endSession();
        //                    }
        //                }
        //                return true;
        //            }
        //            return false;
        //
        //        }

        private static boolean isValidURL(String url) {
            try {
                new URI(url);
            } catch (URISyntaxException e) {
                log.log(Level.SEVERE, "URISyntaxException, returning false.");
                return false;
            }
            return true;
        }
    }
}
