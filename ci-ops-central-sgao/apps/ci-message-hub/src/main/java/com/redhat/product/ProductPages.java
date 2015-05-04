package com.redhat.product;

import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Properties;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.codehaus.jackson.map.ObjectMapper;

import com.sun.jersey.api.client.Client;
import com.sun.jersey.api.client.ClientResponse;
import com.sun.jersey.api.client.WebResource;
import com.sun.jersey.api.client.config.ClientConfig;
import com.sun.jersey.api.client.config.DefaultClientConfig;
import com.sun.jersey.api.json.JSONConfiguration;

public class ProductPages {
	private static final Logger log = Logger.getLogger(ProductPages.class.getName());

	private static final String PRODUCT_PAGES_PROPERTIES = "product-pages.properties";
	private static final String PROPERTY_URL = "url";
	private static final String PROPERTY_FIELDS = "fields";
	
	private static final String APPLICATION_TYPE = "application/json";
	
	private static final Pattern majorReleasePattern = Pattern.compile("^[^-]+-[^-.]+");
//	private static final Pattern minorReleasePattern = Pattern.compile("^[^-]+-[^-.]+\\.(\\d+)");

	public enum Phase {
		Concept,
		Development,
		Maintenance,
		Planning,
		Testing,
		Unknown
	}

	public static HashMap<String, Release> getReleases(String product) {
		return getReleases(product, (Set<Phase>)null);
	}

	public static HashMap<String, Release> getReleases(String product, Phase type) {
		HashSet<Phase> types = new HashSet<Phase>();
		types.add(type);
		return getReleases(product, types);
	}

	public static HashMap<String, Release> getReleases(String product, Set<Phase> types) {
		HashMap<String, Release> result = new HashMap<String, Release>();
		
		try {
			Properties props = new Properties();
			InputStream in = ProductPages.class.getResourceAsStream(PRODUCT_PAGES_PROPERTIES);
			props.load(in);
			in.close();
			String url = props.getProperty(PROPERTY_URL) + "/releases/?product__shortname=" + 
                         product + "&fields=" + props.getProperty(PROPERTY_FIELDS);

			ClientConfig config = new DefaultClientConfig();
			config.getFeatures().put(JSONConfiguration.FEATURE_POJO_MAPPING, Boolean.TRUE);
			Client client = Client.create(config);
			WebResource web = client.resource(url);
			ClientResponse response = web.accept(APPLICATION_TYPE).type(APPLICATION_TYPE).get(ClientResponse.class);
			if (response.getStatus() != 200) {
				throw new RuntimeException("Failed : HTTP error code : "
						+ response.getStatus());
			}
			ObjectMapper mapper = new ObjectMapper();
			String output = response.getEntity(String.class);
			Release[] releases = mapper.readValue(output, Release[].class);
			for (int i = 0; i < releases.length; i++) {
				Phase phase = Phase.Unknown;
				try {
					phase = Phase.valueOf(releases[i].getPhase_display());
				} catch (IllegalArgumentException e) {
					phase = Phase.Unknown;
				}
				
				if (types == null || types.contains(phase)) {					
					result.put(releases[i].getRelease(), releases[i]);
				}
			}
		} catch (Exception e) {
			log.log(Level.SEVERE, "Unhandle exception in product pages.", e);
		}
		return result;
	}
	
	public static HashMap<String, Release>getLatestReleaseMap(String product) {
		HashMap<String, Release> result = new HashMap<String, Release>();
		
		HashMap<String, Release> supported = getReleases(product, Phase.Maintenance);
		for (String s : supported.keySet()) {
			Release release = supported.get(s);
			Matcher matcher = majorReleasePattern.matcher(release.getRelease());
			if (matcher.find()) {
				String key = matcher.group(0);
				if (result.containsKey(key)) {
					if (release.getGa_date() != null && result.get(key).getGa_date() != null && release.getGa_date().after(result.get(key).getGa_date())) {
						result.put(key,  release);
					}
				} else {
					result.put(key,  release);
				}
			}
		}
		
		return result;
	}

	public static void main(String[] args) {
		HashSet<Phase> phases = new HashSet<Phase>();
		phases.add(Phase.Development);
		HashMap<String, Release> results = getReleases("rhel");
		for (String key : results.keySet()) {
			Release release = results.get(key);
			System.out.println("Release => " + release.getRelease() + " (" + release.getShortname() + ")");
		}
		
		HashMap<String, Release> releases = getLatestReleaseMap("rhel");
		System.out.println("Latest Releases =>");
		for (String key : releases.keySet()) {
			Release release = releases.get(key);
			System.out.println("  Release => " + key + " (" + release.getRelease() + ")");
		}
	}
}
