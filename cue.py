import argparse
import os
import json

parser = argparse.ArgumentParser(description="CUE!")
options = parser.add_argument_group('Options')

options.add_argument('-p', '--project',
                    help="Specify the project to run task with",
                    required=False)

options.add_argument('task',
                    help="specify the task")

args = None
conf = None
cuefile = None


def save_conf():
    f = open(os.path.join(os.getenv("HOME"), ".cueconf"), "w")
    json.dump(conf, f, indent=4)
    f.close()


def get_cueconf():
    cueconf_path = os.path.join(os.getenv('HOME'), ".cueconf")
    if not os.path.isfile(cueconf_path):
        print "~/.cueconf doesn't exist"
        exit()

    try:
        cueconf = json.load(open(cueconf_path))
    except:
        print "~/.cueconf is not valid json"
        exit()

    if "projects" not in cueconf:
        print "~/.cueconf is missing projects section"
        exit()

    if "tasks" not in cueconf:
        print "~/.cueconf is missing tasks section"
        exit()

    return cueconf


def get_cuefile():
    if args["project"]:
        if args["project"] not in conf["projects"]:
            print "Project %s not found" % args["project"]
            exit()

        try:
            cf = json.load(open(args["projects"][args["project"]]))
        except:
            print "%s is not valid json" % args["projects"][args["project"]]
            exit()

    else:
        for slug in conf["projects"]:
            cuefile_path = conf["projects"][slug]
            if cuefile_path[:-8] in os.getcwd():
                if not os.path.isfile(cuefile_path):
                    print "Project found but %s appears to not exist" % cuefile_path
                    exit()

                cf = json.load(open(cuefile_path))
                break
        if cf:
            if "root_path" not in cf:
                print "cuefile missing 'root_path'"
                exit()

            if "slug" not in cf:
                print "cuefile missing 'slug'"
                exit()

            if "name" not in cf:
                print "cuefile missing 'name'"
                exit()

            if "tasks" not in cf:
                print "cuefile missing 'tasks'"
                exit()
            elif "workon" not in cf["tasks"]:
                print "cuefile tasks mising 'workon' task"
                exit()
        else:
            print "cuefile not found"
            exit()

        return cf


def register():
    print "Register!"
    if os.path.isfile(os.path.join(os.getcwd(), ".cuefile")):
        cuefile = json.load(open(os.path.join(os.getcwd(), ".cuefile")))
        if cuefile["slug"] in conf["projects"]:
            print "project slug already exists on the system"
            exit()

        conf["projects"][cuefile["slug"]] = os.path.join(cuefile["root_path"], ".cuefile")
        save_conf()
    else:
        name = raw_input("Name of Project: ")
        slug = raw_input("Project Slug: ")
        root = os.path.join(os.getcwd(), ".cuefile")

        tasks = {"workon": []}

        conf["projects"][slug] = root
        save_conf()

        cuefile_dict = {"name": name, "slug": slug, "root_path": root, "tasks": tasks}

        f = open(os.path.join(os.getcwd(), ".cuefile"), "w+")
        json.dump(cuefile_dict, f, indent=4)
        f.close()


def unregister():
    print "Unregister!"
    if conf["projects"][cuefile["slug"]]:
        del conf["projects"][cuefile["slug"]]
        save_conf()
    else:
        print "Project %s is not registered" % cuefile["slug"]


def run_task(task_name):
    # TODO - actualy run tasks
    # - check for task name defined in local project .cuefile
    # - if not check globally, selecting appropriate group/type
    # - once initial task is found, dig through recursively until complete and/or stopped
    def run_exec(task):
        if type(task) is dict:
            # run task["exec"]
            # error? exec(task["onError"])
            # flow - stop|continue
            pass
        elif type(task) is str:
            if task[0] == ':':
                run_task(task[1:])
            else:
                # shell, ignoring errors
                pass

if __name__ == '__main__':
    args = vars(parser.parse_args())

    conf = get_cueconf()

    if args["task"] == "register":
        register()
    elif args["task"] == "unregister":
        cuefile = get_cuefile()
        unregister()
    else:
        cuefile = get_cuefile()
        run_task(args["task"])
