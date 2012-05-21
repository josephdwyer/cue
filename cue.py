import argparse
import os
import json
import collections
from subprocess import call

parser = argparse.ArgumentParser(description='CUE!')
options = parser.add_argument_group('Options')


options.add_argument('-p', '--project',
                    help='Specify the target project for the task',
                    required=False)

options.add_argument('-s', '--section',
                    help='Specify the section for the task',
                    required=False)

options.add_argument('task',
                    help='Specify the task')

options.add_argument('assumed_project', nargs='?',
                    help='Specify the project')

global_config_dir_path = os.path.join(os.getenv('HOME'), '.cue')
extension = '.cueconf'

args = None


def get_global_conf():
    cues = get_settings_from_directory(global_config_dir_path)

    if 'projects' not in cues:
        print 'cueconf is missing projects section'
        exit()

    if 'defaultSection' not in cues:
        print 'cueconf is missing defaultSection definition'
        exit()

    return cues

def get_settings_from_directory(directory_path):
    if not os.path.exists(directory_path):
        print 'directory does not exist (%s)' % directory_path
        exit()

    cueconf_file_paths = \
        [os.path.join(directory_path, file)
        for file in os.listdir(directory_path) if file.lower().endswith(extension)]

    cues = {}
    for cueconf_path in cueconf_file_paths:
        if not os.path.isfile(cueconf_path):
            print "cueconf doesn't exist " + cueconf_path
            exit()

        try:
            cueconf_contents = json.load(open(cueconf_path))
        except:
            print '%s is not valid json' % cueconf_path
            exit()
        cues = recursive_update(cues, cueconf_contents)

    return cues

def get_project_conf(global_conf, project_name=None):
    cues = None
    if project_name:
        if project_name not in global_conf['projects']:
            print 'Project %s not found' % project_name
            exit()

        cues = get_settings_from_directory(global_conf['projects'][project_name])

    else:
        for slug in global_conf['projects']:
            project_conf_path = global_conf['projects'][slug]
            if os.path.dirname(project_conf_path) in os.getcwd():
                cues = get_settings_from_directory(project_conf_path)

                if not cues:
                    print 'Project found but no cueconf files appear to not exist'
                    exit()
                break
    if cues:
        if 'root_path' not in cues:
            print "project_conf missing 'root_path'"
            exit()

        if 'slug' not in cues:
            print "project_conf missing 'slug'"
            exit()

        if 'name' not in cues:
            print "project_conf missing 'name'"
            exit()

        if 'defaultSection' in cues and cues['defaultSection'] not in cues:
            print "project_conf missing '%s'" % cues['defaultSection']
            exit()
        elif 'defaultSection' not in cues and global_conf['defaultSection'] not in cues:
            print "project_conf missing '%s'" % global_config['defaultSection']
            exit()
    else:
        print 'project_conf not found'
        exit()

    return cues


def recursive_update(d, u):
    "Recursively updates a dictionary like object."
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        elif k in d and isinstance(d[k], collections.Iterable) \
                and isinstance(v, collections.Iterable):
            d[k] += v
        else:
            d[k] = v
    return d


def register(global_conf, section):
    project_conf_dict = get_settings_from_directory(os.getcwd())

    if project_conf_dict:
        name = project_conf_dict['name']
        slug = project_conf_dict['slug']

    else:
        name = raw_input('Name of Project: ')
        slug = raw_input('Project Slug: ')
        default_section = {}

        project_conf_dict = {'name': name,
                            'slug': slug,
                            'root_path': os.getcwd(),
                            section: default_section}

        proj_cue_path = os.path.join(os.getcwd(), extension)
        f = open(proj_cue_path, 'w+')
        json.dump(project_conf_dict, f, indent=4)
        f.close()

    if slug in global_conf['projects']:
        print 'project slug already exists on the system'
        exit()

    global_conf['projects'][slug] = os.getcwd()

    f = open(os.path.join(global_config_dir_path, slug + extension), 'w+')
    json.dump({'projects': {slug: os.getcwd()}}, f, indent=4)
    f.close()

    return project_conf_dict


def unregister(global_conf, project_conf):
    if project_conf['slug'] not in global_conf['projects']:
        print 'Project %s is not registered' % project_conf['slug']
        exit()

    del global_conf['projects'][project_conf['slug']]
    os.remove(os.path.join(global_config_dir_path, \
            project_conf['slug'] + extension))


def run_task(section, task_name, global_conf, project_conf):
    def exec_task(task):
        print type(task)
        if isinstance(task, collections.Mapping):
            if 'exec' in task:
                call(task['exec'])
                if 'onError' in task:
                    exec_task(task['onError'])

            if 'flow' in task:
                #respect it
                pass

        elif isinstance(task, basestring):
            if task[0] == ':':
                run_task(task[1:])
            else:
                print 'call ' + task
                call(task)

    task = None

    #Local
    if task_name in project_conf[section]:
        task = project_conf[section][task_name]

    #Global
    if not task:
        if 'global' in global_conf[section] and \
                task_name in global_conf[section]['global']:
            task = global_conf[section]['global'][task_name]

    #By Group
    if not task:
        for group in global_conf[section]:
            if group in project_conf:
                task = \
                global_conf[section][group][project_conf[group]][task_name]
            else:
                print 'Project missing setting. ' + \
                        'Please define an entry for %s[%s] = (%s)' % \
                    (section, group, str(global_conf[section][group].keys()))
            if task:
                break

    if not task:
        print '(%s) task not found' % task_name
        exit()

    exec_task(task)


if __name__ == '__main__':
    args = vars(parser.parse_args())

    global_conf = get_global_conf()

    if not args['project'] and args['assumed_project']:
        args['project'] = args['assumed_project']

    is_section_default = False
    if not args['section']:
        args['section'] = global_conf['defaultSection']
        is_section_default = True

    if args['task'] == 'register':
        project_conf = register(global_conf, args['section'])
    else:
        project_conf = get_project_conf(global_conf, args['project'])
        if is_section_default and 'defaultSection' in project_conf:
            args['section'] = project_conf['defaultSection']

        if args['task'] == 'unregister':
            unregister(global_conf, project_conf)
        else:
            run_task(args['section'], args['task'], global_conf, project_conf)
