import argparse
import os
import json
import collections
from subprocess import call

parser = argparse.ArgumentParser(description="CUE!")
options = parser.add_argument_group('Options')


options.add_argument('-p', '--project',
                    help="Specify the target project for the task",
                    required=False)

options.add_argument('task',
                    help="Specify the task")

options.add_argument('assumed_project', nargs='?',
                    help="Specify the project")

global_config_dir_path = os.path.join(os.getenv('HOME'), ".cue")
extension = '.cueconf'

args = None


def get_global_conf():

    if not os.path.exists(global_config_dir_path):
        os.makedirs(global_config_dir_path)

    cueconf_file_paths = [os.path.join(global_config_dir_path, file) for file in os.listdir(global_config_dir_path) \
                            if file.lower().endswith(extension)]

    cues = {}
    for cueconf_path in cueconf_file_paths:
        if not os.path.isfile(cueconf_path):
            print "cueconf doesn't exist " + cueconf_path
            exit()

        try:
            cueconf_contents = json.load(open(cueconf_path))
        except:
            print "cueconf is not valid json"
            exit()
        cues = recursive_update(cues, cueconf_contents)

    if "projects" not in cues:
        print "cueconf is missing projects section"
        exit()

    if "tasks" not in cues:
        print "cueconf is missing tasks section"
        exit()

    return cues


def get_project_conf(global_conf, project_name=None):
    cf = None
    if project_name:
        if project_name not in global_conf["projects"]:
            print "Project %s not found" % project_name
            exit()

        try:
            cf = json.load(open(global_conf["projects"][project_name]))
        except:
            print "%s is not valid json" % \
                    global_conf["projects"][project_name]
            exit()

    else:
        for slug in global_conf['projects']:
            project_conf_path = global_conf["projects"][slug]
            if os.path.dirname(project_conf_path) in os.getcwd():
                if not os.path.isfile(project_conf_path):
                    print "Project found but %s appears to not exist" % \
                            project_conf_path
                    exit()

                cf = json.load(open(project_conf_path))
                break
    if cf:
        if "root_path" not in cf:
            print "project_conf missing 'root_path'"
            exit()

        if "slug" not in cf:
            print "project_conf missing 'slug'"
            exit()

        if "name" not in cf:
            print "project_conf missing 'name'"
            exit()

        if "tasks" not in cf:
            print "project_conf missing 'tasks'"
            exit()
        elif "workon" not in cf["tasks"]:
            print "project_conf tasks mising 'workon' task"
            exit()
    else:
        print "project_conf not found"
        exit()

    return cf


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


def register(global_conf):
    print "Register!"

    proj_cue_path = os.path.join(os.getcwd(), extension)

    if os.path.isfile(proj_cue_path):
        project_conf_dict = json.load(open(proj_cue_path))

        name = project_conf_dict['name']
        slug = project_conf_dict['slug']

    else:
        name = raw_input("Name of Project: ")
        slug = raw_input("Project Slug: ")
        tasks = {"workon": []}

        project_conf_dict = {"name": name,
                        "slug": slug,
                        "root_path": proj_cue_path,
                        "tasks": tasks}

        f = open(proj_cue_path, "w+")
        json.dump(project_conf_dict, f, indent=4)
        f.close()

    if slug in global_conf["projects"]:
        print "project slug already exists on the system"
        exit()

    global_conf["projects"][slug] = proj_cue_path

    f = open(os.path.join(global_config_dir_path, slug + extension), "w+")
    json.dump({'projects': {slug: proj_cue_path}}, f, indent=4)
    f.close()

    return project_conf_dict


def unregister(global_conf, project_conf):
    print "Unregister!"
    if project_conf["slug"] not in global_conf["projects"]:
        print "Project %s is not registered" % proj_conf["slug"]
        exit()

    del global_conf["projects"][proj_conf["slug"]]
    os.remove(os.join(global_config_dir_path, name))


def run_task(task_name, global_conf, project_conf):
    def exec_task(task):
        print type(task)
        if isinstance(task, collections.Mapping):
            if "exec" in task:
                call(task["exec"])
                if "onError" in task:
                    exec_task(task["onError"])

            if "flow" in task:
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
    if task_name in project_conf["tasks"]:
        task = project_conf["tasks"][task_name]

    #Global
    if not task:
        if 'global' in global_conf['tasks'] and task_name in global_conf["tasks"]["global"]:
            task = global_conf["tasks"]["global"][task_name]

    #By Group
    if not task:
        for group in global_conf["tasks"]:
            if group in project_conf:
                task = \
                global_conf['tasks'][group][project_conf[group]][task_name]
            if task:
                break

    if not task:
        print "(%s) task not found" % task_name
        exit()

    exec_task(task)


if __name__ == '__main__':
    args = vars(parser.parse_args())

    global_conf = get_global_conf()

    if not args['project'] and args['assumed_project']:
        args['project'] = args['assumed_project']

    if args["task"] == "register":
        project_conf = register(global_conf)
    elif args["task"] == "unregister":
        project_conf = get_project_conf(global_conf, args['project'])
        unregister(global_conf, project_conf)
    else:
        project_conf = get_project_conf(global_conf, args['project'])
        run_task(args["task"], global_conf, project_conf)
