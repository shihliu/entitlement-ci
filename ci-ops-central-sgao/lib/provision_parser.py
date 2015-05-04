import json


def get_json_props(props_file):
    input_file = open(props_file, 'r')
    data = json.load(input_file)
    input_file.close()
    return data


def create_global_defaults(global_data):
    """
        Extract global defaults defined in global_defaults.json
    """
    site_defaults = {}
    resource_defaults = {}
    for options, data in global_data.iteritems():
        if ('default' in data) and ('endpoints' in data):
            site_default = data['default']
            sites = data['endpoints']
            site_defaults['site'] = site_default
            site_defaults[options] = sites[site_default]
        if ('default' in data) and ('sizes' in data):
            flavor_default = data['default']
            flavors = data['sizes']
            resource_defaults[options] = flavors[flavor_default]
        if ('default' in data) and ('images' in data):
            image_default = data['default']
            images = data['images']
            resource_defaults[options] = images[image_default]
    overall_defaults = \
        {'resources': [resource_defaults], 'sites': [site_defaults]}
    return overall_defaults


def extract_proj_data(key, props_file):
    """
        Extract project data from JSON project_defaults.json
    """
    proj_data_props = {}
    for idx, props in props_file.iteritems():
        if key == idx:
            for prop in props:
                proj_data_props = prop
    return (proj_data_props)


def extract_top_data(props_file):
    """
        Extract topology data if it exists
        from JSON aio.json
    """
    keys = ['sites', 'resources']
    get_data = lambda data: \
        [props for key in keys
         for idx, props in data.iteritems()
         if key in idx][0]
    return (get_data(props_file))


def merge_all_props(props_files):
    """
        Merge global_defaults, project_defaults, and topology files
    """
    overall_props = {}
    sites_merged_props = {}
    top_data = props_files.pop()
    for idx, props_file in enumerate(props_files):
        if props_file['sites']:
            sites_merged_props.update(extract_proj_data('sites', props_file))
        if props_file['resources']:
            resources_merged_props = \
                (extract_proj_data('resources', props_file))
    overall_props['sites'] = [sites_merged_props]
    overall_props['resources'] = [resources_merged_props]
    if 'resources' in top_data:
        top_data = extract_top_data(top_data)
        overall_props['resources'] = top_data
    return (overall_props)