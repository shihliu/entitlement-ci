package com.redhat.product;

import java.util.Date;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Release {
	private Integer id;
	private Integer bu;
	private String bu_shortname;
	private String bu_name;
	private Integer product;
	private String product_shortname;
	private String product_name;
	private String name;
	private String shortname;
	private Date ga_date;
	private String schedule;
	private String cpe;
	private String description;
	private String eus;
	private String fullName;
	private String security;
	private Date release_date;
	private Integer phase;
	private String phase_display;
	private String platforms;
	private String dist_methods;
	private String bz_product;
	private String bz_version;
	private String bz_nvr_flag;
	private String last_statuses;
	
	private String release;
	
	public Release() {
		
	}
	
	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getBu() {
		return bu;
	}

	public void setBu(Integer bu) {
		this.bu = bu;
	}

	public String getBu_shortname() {
		return bu_shortname;
	}

	public void setBu_shortname(String bu_shortname) {
		this.bu_shortname = bu_shortname;
	}

	public String getBu_name() {
		return bu_name;
	}

	public void setBu_name(String bu_name) {
		this.bu_name = bu_name;
	}

	public Integer getProduct() {
		return product;
	}

	public void setProduct(Integer product) {
		this.product = product;
	}

	public String getProduct_shortname() {
		return product_shortname;
	}

	public void setProduct_shortname(String product_shortname) {
		this.product_shortname = product_shortname;
	}

	public String getProduct_name() {
		return product_name;
	}

	public void setProduct_name(String product_name) {
		this.product_name = product_name;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getShortname() {
		return shortname;
	}


	public void setShortname(String shortname) {
		this.shortname = shortname;
		// Clean up short name to be release. Capitalize and change to NAME-X.Y.
		setRelease(shortname.toUpperCase());
		Pattern p = Pattern.compile("(^[^-]+-[^-]+)-(.*)");
		Matcher m = p.matcher(getRelease());
		if (m.find()) {
			setRelease(m.group(1) + "." + m.group(2));
		}
	}

	public Date getGa_date() {
		return ga_date;
	}

	public void setGa_date(Date ga_date) {
		this.ga_date = ga_date;
	}

	public String getSchedule() {
		return schedule;
	}

	public void setSchedule(String schedule) {
		this.schedule = schedule;
	}

	public String getCpe() {
		return cpe;
	}

	public void setCpe(String cpe) {
		this.cpe = cpe;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getEus() {
		return eus;
	}

	public void setEus(String eus) {
		this.eus = eus;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public String getSecurity() {
		return security;
	}

	public void setSecurity(String security) {
		this.security = security;
	}

	public Date getRelease_date() {
		return release_date;
	}

	public void setRelease_date(Date release_date) {
		this.release_date = release_date;
	}

	public Integer getPhase() {
		return phase;
	}

	public void setPhase(Integer phase) {
		this.phase = phase;
	}

	public String getPhase_display() {
		return phase_display;
	}

	public void setPhase_display(String phase_display) {
		this.phase_display = phase_display;
	}

	public String getPlatforms() {
		return platforms;
	}

	public void setPlatforms(String platforms) {
		this.platforms = platforms;
	}

	public String getDist_methods() {
		return dist_methods;
	}

	public void setDist_methods(String dist_methods) {
		this.dist_methods = dist_methods;
	}

	public String getBz_product() {
		return bz_product;
	}

	public void setBz_product(String bz_product) {
		this.bz_product = bz_product;
	}

	public String getBz_version() {
		return bz_version;
	}

	public void setBz_version(String bz_version) {
		this.bz_version = bz_version;
	}

	public String getBz_nvr_flag() {
		return bz_nvr_flag;
	}

	public void setBz_nvr_flag(String bz_nvr_flag) {
		this.bz_nvr_flag = bz_nvr_flag;
	}

	public String getLast_statuses() {
		return last_statuses;
	}

	public void setLast_statuses(String last_statuses) {
		this.last_statuses = last_statuses;
	}

	public String getRelease() {
		return release;
	}

	public void setRelease(String release) {
		this.release = release;
	}
}
