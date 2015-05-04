package com.redhat.ci.brew;

import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeSet;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.jms.MapMessage;
import javax.jms.Message;
import javax.jms.MessageListener;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;

import com.redhat.ci.CIMessage;
import com.redhat.mikeb.test.brew.XmlRpcTypeNil;
import com.redhat.product.ProductPages;
import com.redhat.product.Release;

public class BrewListener implements MessageListener {
    private final Logger log = Logger.getLogger(BrewListener.class.getName());
    private static final String OS_PRODUCT_NAME = "rhel";
    private static final String PROPERTY_SCRATCH_BUILD = "scratch";
    private static final String PROPERTY_OWNER = "owner";
    private static final String PROPERTY_TARGET = "target";

    //	private static final Pattern patCandidate = Pattern.compile("-candidate");
    private static final Pattern patRHEL_X_Y_Z = Pattern.compile("rhel-\\d+\\.\\d+-z", Pattern.CASE_INSENSITIVE);
    private static final Pattern patRHEL_X_Y_FASTRACK = Pattern.compile("((rhel-\\d+)\\.\\d+)-fastrack", Pattern.CASE_INSENSITIVE);
    private static final Pattern patRHEL_X_FASTRACK = Pattern.compile("(rhel-\\d+)-fastrack", Pattern.CASE_INSENSITIVE);
    private static final Pattern patRHEL_X_Y = Pattern.compile("rhel-\\d+\\.\\d+", Pattern.CASE_INSENSITIVE);
    private static final Pattern patRHEL_X = Pattern.compile("rhel-\\d+", Pattern.CASE_INSENSITIVE);
    private static final Pattern patNVR = Pattern.compile("(.*)(-debuginfo)?-([^-]+)-([^-]+)\\.([^.]+)\\.rpm", Pattern.CASE_INSENSITIVE);

    private String xmlrpc;

    private static final String BREW_DOWNLOAD = "http://download.devel.redhat.com/brewroot/packages";
    private static final Map<String, String> archiveTypes;
    static {
        Map<String, String> m = new HashMap<String, String>();
        m.put("image", "images");
        m.put("maven", "maven");
        m.put("win", "win");
        archiveTypes = Collections.unmodifiableMap(m);
    }

    BrewListener(String xmlrpc) {
        this.xmlrpc = xmlrpc;
    }

    @SuppressWarnings("unchecked")
    public void onMessage(Message message) {
        log.info("BREW MESSAGE = \n" + CIMessage.formatMessage(message));
        try {
            ObjectMapper mapper = new ObjectMapper();
            ObjectNode root = mapper.createObjectNode();
            HashMap<String, Object> props = new HashMap<String, Object>();

            MapMessage mm = (MapMessage) message;

            Enumeration<String> e = mm.getMapNames();
            while (e.hasMoreElements()) {
                String field = e.nextElement();
                root.put(field, mapper.convertValue(mm.getObject(field), JsonNode.class));
            }

            XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
            config.setServerURL(new URL(xmlrpc));
            config.setEnabledForExtensions(true);
            XmlRpcClient client = new XmlRpcClient();
            client.setTypeFactory(new XmlRpcTypeNil(client));
            client.setConfig(config);

            if (mm.getStringProperty("type").equalsIgnoreCase("TaskStateChange")) {
                LinkedHashMap<String, Object> info = (LinkedHashMap<String, Object>)mm.getObject("info");
                Integer id = ((Long) info.get("id")).intValue();
                log.info("Got task id #" + id);

                ArrayList<Object> request = (ArrayList<Object>)info.get("request");
                String method = mm.getStringProperty("method");
                if (request != null) {
                    if (request.size() >= 3 && method.startsWith("build")) {
                        // Determine if it is a scratch build.
                        props.put(PROPERTY_SCRATCH_BUILD, false);

                        Map<String, Object> tinfo = (Map<String, Object>)client.execute("getTaskInfo", new Object[]{id, "True"});
                        if (method.equalsIgnoreCase("build")) {
                            props.put(PROPERTY_SCRATCH_BUILD, getScratchBuild(tinfo));
                            props.put(PROPERTY_OWNER, getOwner(client, tinfo));
                        } else if (method.equalsIgnoreCase("buildArch")) {
                            // Get scratch build value from parent task.
                            Map<String, Object> ptinfo = (Map<String, Object>)client.execute("getTaskInfo", new Object[]{((Long)info.get("parent")).intValue(), "True"});
                            props.put(PROPERTY_SCRATCH_BUILD, getScratchBuild(ptinfo));
                            props.put(PROPERTY_OWNER, getOwner(client, tinfo));
                        }

                        if (props.get(PROPERTY_OWNER) != null) {
                            // Set owner to a real person, then replace info node on the message.
                            info.put(PROPERTY_OWNER, props.get(PROPERTY_OWNER));
                            root.put("info", mapper.convertValue(info, JsonNode.class));
                        }
                    }
                    if (request.size() >= 2) {
                        // Add the target header
                        props.put(PROPERTY_TARGET, request.get(1));
                    }
                }

                LinkedHashMap<String, TreeSet<String>> arches = new LinkedHashMap<String, TreeSet<String>>();
                Object[] tasks = (Object[]) client.execute("getTaskChildren", new Object[]{id});
                for (Object o : tasks) {
                    Map<String, Object> task = (Map<String, Object>) o;
                    log.info(task.toString());
                    if (((String)task.get("method")).equalsIgnoreCase("buildArch")) {
                        id = (Integer)task.get("id");
                        Object[] outputs = (Object[]) client.execute("listTaskOutput", new Object[]{id});
                        for (Object output : outputs) {
                            String file = output.toString();
                            Matcher m = patNVR.matcher(output.toString());
                            if (file.indexOf("-debuginfo") < 0 && m.find()) {
                                props.put("package", m.group(1));
                                props.put("CI_NAME", m.group(1));

                                String arch = (String)task.get("arch");
                                if (!arches.containsKey(arch)) {
                                    arches.put(arch, new TreeSet<String>());
                                }
                                arches.get(arch).add(file);
                            }
                        }
                    }
                }
                root.put("rpms", mapper.convertValue(arches, JsonNode.class));
            } else if (mm.getStringProperty("type").equalsIgnoreCase("Tag")) {
                if (mm.getObject("build") != null) {
                    LinkedHashMap<String, Object> build = (LinkedHashMap<String, Object>)mm.getObject("build");
                    Integer id = ((Long) build.get("id")).intValue();

                    LinkedHashMap<String, TreeSet<String>> arches = new LinkedHashMap<String, TreeSet<String>>();
                    Object[] results = (Object[]) client.execute("listRPMs", new Object[]{id});
                    for (Object result : results) {
                        Map<String, Object> rpm = (Map<String, Object>) result;
                        String name = (String) rpm.get("name");
                        String version = (String) rpm.get("version");
                        String release = (String) rpm.get("release");
                        String arch = (String) rpm.get("arch");
                        if (!arches.containsKey(arch)) {
                            arches.put(arch, new TreeSet<String>());
                        }

                        String rpmname = String.format("%s-%s-%s.%s.rpm", name, version, release, arch);
                        arches.get(arch).add(rpmname);
                    }
                    root.put("rpms", mapper.convertValue(arches, JsonNode.class));

                    TreeSet<String> tags = new TreeSet<String>();
                    results = (Object[]) client.execute("listTags", new Object[]{id});
                    for (Object result : results) {
                        Map<String, Object> tag = (Map<String, Object>) result;
                        tags.add((String)tag.get("name"));
                    }
                    root.put("tags", mapper.convertValue(tags, JsonNode.class));

                    LinkedHashMap<String, TreeSet<String>> archives = new LinkedHashMap<String, TreeSet<String>>();
                    for (String atype : archiveTypes.keySet()) {
                        results = (Object[]) client.execute("listArchives", new Object[]{id, null, null, null, atype});
                        for (Object result : results) {
                            Map<String, Object> archive = (Map<String, Object>) result;
                            String type = (String) archive.get("type_name");
                            if (!archives.containsKey(type)) {
                                archives.put(type, new TreeSet<String>());
                            }

                            archives.get(type).add(getArchivePath(atype, build, archive));
                        }
                    }
                    root.put("archives", mapper.convertValue(archives, JsonNode.class));
                }
            }

            //			root.put("os-to-test", OsToTest(mm.getStringProperty("tag")));

            //			log.info("CI_MESSAGE = \n" + mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));

            // Now put our message out on the ci exchange.
            props.put("CI_TYPE", "brew-" + message.getStringProperty("type").toLowerCase());
            if (message.propertyExists("name")) {
                props.put("CI_NAME", message.getStringProperty("name"));
            }

            // Copy over all the brew message properties.
            Enumeration<String> propNames = message.getPropertyNames();
            while (propNames.hasMoreElements()) {
                String propertyName = propNames.nextElement ();
                props.put(propertyName, message.getObjectProperty (propertyName));
            }

            CIMessage.send(props, mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
        } catch (Exception e) {
            log.log(Level.SEVERE, "Unhandled exception processing message:\n" + message.toString(), e);
        }
    }

    private Boolean getScratchBuild(Map<String, Object> info) {
        Object[] prequest = (Object[])info.get("request");
        if (prequest != null && prequest.length >= 3) {
            @SuppressWarnings("unchecked")
            Map<String, Object> options = (Map<String, Object>)prequest[2];
            return (options != null && options.get("scratch") != null);
        }
        return false;
    }

    private String getOwner(XmlRpcClient client, Map<String, Object> info) {
        try {
            Integer id = (Integer) info.get("owner");
            if (id != null) {
                @SuppressWarnings("unchecked")
                Map<String, Object> user = (Map<String, Object>)client.execute("getUser", new Object[]{id});
                if (user != null) {
                    return (String)user.get("name");
                }
            }
        } catch (XmlRpcException e) {
            log.log(Level.SEVERE, "Unhandled exception getting owner:\n", e);
        }
        return "<unknown>";
    }

    private String getArchivePath(String type, LinkedHashMap<String, Object> build, Map<String, Object> archive) {
        String pkg = (String) build.get("package_name");
        String version = (String) build.get("version");
        String release = (String) build.get("release");
        String filename = (String) archive.get("filename");

        StringBuffer sb = new StringBuffer();
        sb.append(BREW_DOWNLOAD);
        sb.append("/");
        sb.append(pkg);
        sb.append("/");
        sb.append(version);
        sb.append("/");
        sb.append(release);
        sb.append("/");
        sb.append(archiveTypes.get(type));
        sb.append("/");
        if (type.equals("maven")) {
            sb.append(((String)archive.get("group_id")).replace(".",  "/"));
            sb.append("/");
            sb.append(((String)archive.get("artifact_id")));
            sb.append("/");
            sb.append((String)archive.get("version"));
            sb.append("/");
        } else if (type.equals("win")) {
            sb.append((String)archive.get("relpath"));
            sb.append("/");
        }
        sb.append(filename);

        return sb.toString();
    }

    public static String OsToTest(String tag) {
        String os = null;

        HashMap<String, Release> maintained = ProductPages.getReleases(OS_PRODUCT_NAME, ProductPages.Phase.Maintenance);
        HashMap<String, Release> development = ProductPages.getReleases(OS_PRODUCT_NAME, new HashSet<ProductPages.Phase>(Arrays.asList(ProductPages.Phase.Development, ProductPages.Phase.Testing)));
        HashMap<String, Release> latest = ProductPages.getLatestReleaseMap(OS_PRODUCT_NAME);

        Matcher m = patRHEL_X_Y_Z.matcher(tag);
        if (m.find()) {
            os = m.group(0).toUpperCase();
        } else {
            m = patRHEL_X_Y_FASTRACK.matcher(tag);
            if (m.find()) {
                if (maintained.containsKey(m.group(1).toUpperCase())) {
                    os = m.group(1).toUpperCase() + "-Z";
                } else {
                    os = latest.get(m.group(2).toUpperCase()).getRelease() + "-Z";
                }
            } else {
                m = patRHEL_X_FASTRACK.matcher(tag);
                if (m.find()) {
                    os = latest.get(m.group(1).toUpperCase()).getRelease() + "-Z";
                } else {
                    m = patRHEL_X_Y.matcher(tag);
                    if (m.find()) {
                        os = m.group(0).toUpperCase();
                        if (!development.containsKey(os)) {
                            os += "-Z";
                        }
                    } else {
                        m = patRHEL_X.matcher(tag);
                        if (m.find()) {
                            os = latest.get(m.group(0).toUpperCase()).getRelease();
                            if (!development.containsKey(os)) {
                                os += "-Z";
                            }
                        }
                    }
                }
            }
        }

        if (os != null && !maintained.containsKey(os) && !maintained.containsKey(os.replaceFirst("-Z$", "")) && !development.containsKey(os)) {
            // OS is not supported.
            os = null;
        }
        return os;
    }

    public static void main(String[] args) {
        String os = BrewListener.OsToTest("RHEL-6-fastrack-candidate");
        System.out.println("OS => " + os);
    }
}
