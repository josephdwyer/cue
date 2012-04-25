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


def save_conf():
    f = open(os.path.join(os.getenv("HOME"), ".cueconf"), "w")
    json.dump(conf, f, indent=4)
    f.close()


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
        name = raw_input("Name of Project:")
        slug = raw_input("Project Slug:")
        root = os.getcwd()

        conf["projects"][slug] = root
        save_conf()

        cuefile_dict = {"name": name, "slug": slug, "root_path": root}

        f = open(os.path.join(os.getcwd(), ".cuefile"), "w+")
        json.dump(cuefile_dict, f, indent=4)
        f.close()


def unregister(slug):
    if conf["projects"][slug]:
        del conf["projects"][slug]
        save_conf()
    else:
        print "Project %s is not registered" % slug


def task(task_name):
    pass


if __name__ == '__main__':
    args = vars(parser.parse_args())

    cueconf_path = os.path.join(os.getenv('HOME'), ".cueconf")

    if not os.path.isfile(cueconf_path):
        print "~/.cueconf doesn't exist"
        exit()

    try:
        conf = json.load(open(cueconf_path))
    except:
        print "~/.cueconf is not valid json"
        exit()

    if conf[u"projects"] is None:
        print "~/.cueconf is missing projects section"
        exit()

    if conf["tasks"] is None:
        print "~/.cueconf is missing tasks section"
        exit()

    if args["task"] == "register":
        register()
    elif args["task"] == "unregister":
        if args["project"]:
            slug = args["project"]
        else:
            slug = "???"
        unregister(slug)
    else:
        task(args["task"])
