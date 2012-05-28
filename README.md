#Cue - A Project/Task automator for local development


Basically the goal is to create a development workflow automation engine to make core workflow steps consistent and reusable across multiple mixes of scm, platforms, environments, or anything else.

## Usage

A few basic top level commands

###```cue register```
Registering a project makes cue aware of its existence. First, register will search of any .cueconf files in the user's current directory. If no .cueconf files are found, a short list of questions will be asked to setup the project.

###```cue deregister```
Deregistering a project makes cue unaware of the projects existence, meaning cue commands can no longer be run on that project. deregister leaves any .cueconf files in the project directory.

###```cue (-s section_name|-p project_name) [taskName (project_name)]```
Search for a task named taskName defined in the global or project configuration files. If the project_name is specified through the -p flag or the second command line parameter, perform the task on that project, if it is not specified, check to see if the user is currently in a sub-directory of a registered project. If -s is specified look for the task in the section specified, otherwise use the section defined in defaultSection.

## Setup and Task Hierarchy
Global .cueconf files are located in ```~/.cue/```, there can be several files which will be combined into the same JSON object. By allowing multiple files, related tasks can be logically grouped and shared. E.G. git.cueconf, hg.cueconf, sv.cueconf.

#### Global (~/.cue/[any-file-name].cueconf)

Example format of the `~/.cue/.cueconf` file at the most basic level

    {
        "defaultSection": "section_name",
        "section_name": {
            "group": {
                "type": {
                    "action1": [task_objs, to, run],
                    "action2": [task_objs, to, run]
                },
                "type2": {
                    "action3": [task_objs, to, run],
                    "action4": [task_objs, to, run]
                }
            }
            "group2": {
                "type": {
                    "action5": [task_objs, to, run],
                    "action6": [task_objs, to, run]
                },
                "type2": {
                    "action7": [task_objs, to, run],
                    "action8": [task_objs, to, run]
                }
            }
        }
    }

These settings define and namespace tasks that can be run within projects and are completely open ended...

A non generic example

    {
        "defaultSection": "tasks",
        "tasks": {
            "editor": {
                "vim": {
                    "open": ["vim"]
                },
                "sublime": {
                    "open": [{"exec": "subl"}],
                },
                "gedit": {
                    "open": {"exec": "gedit", "onError": {"exec": "echo 'ught oh'", "flow": "next"}}               
            },
            "scm": {
                "git": {
                    "update": ["git pull"],
                    "commit": ["git commit -a"]
                },
                "hg": {
                    "update": ["hg pull", "hg merge"],
                    "commit": ["shell", "hg commit"]
                }
            },
           "type": {
                "django": {
                 "start": ["python manage.py runserver"]
            }
            "rails": {
                "start": ["rails server"]
            }
        }

        }
    }


#### Per Project Settings ( /path/to/project/.cuefile )

Per project we will define which set of tasks to use a generic project file might look like this...

    {
        "root_path":"/path/to/root/of/project/",
        "public_path":"/path/to/web/root/",
        "slug":"my-project",
        "name":"My Project",
        "group":"type2",
        "group2":"type",
        "tasks": {
            "workon": [":action2",":action1"],
            "projectSpecificTask": ["shell","commands"]
        }
    }
    
A non generic example using the non-generic example above might look like this.

    {
        "root_path":"/path/to/root/of/project/", <-- required
        "slug":"my-project",                     <-- required
        "name":"My Project",                     <-- required
        "public_path":"/path/to/web/root/",
        "editor":"vim",
        "scm":"git",
        "type":"django"
    }

You could define a workon task which updates the project, and opens the editor. Then when you use ```cue workon my-project``` from anywhere in the system it goes to the root of the project, updates from your scm, and opens your editor based on your settings.

Then to further demonstrate the polymorphic nature of the tool, you could then run ```cue start``` and that would use the start command relevant to your defined type in the project settings.

#### Tasks

A task can be one of 2 things

 - a simple string to either run in the shell or call another task (prefixed with `:`)
 - an object outlined below...

You can refer to the current project properties in your shell strings with `##property##`


    Task
    {
        "exec": "command",
        "onError": {another_task},
        "flow": "[next|previous|stop|#(index of task)]"
    }


The `exec` property is equivalent to the string preveously expected, but providing `onError` will give you the opportunitiy to "clean up" after a failed command and/or continue executing commands on the error.

By default, when there is an error the default value for flow is 'stop'. Meaning halt execution of the rest of the commands. If you do want the system to continue through a failed command, simply define `onError` as `{"flow":"next"}`.


#### Error Handling

Example from above

    ...
    "scm": {
        "git": {
            "update": [{
                "exec":"git pull",
                "onError": { "exec": "shell command to clean up or notify", "flow":"stop" }
            }]
        },
    },
    ...

##ToDo
1. allow reference of properties with ##property_name## in tasks  
1. allow reference of additional command line arguments via $1,$2 syntax, including taking into account project_name may or may not be the second parameter.
1. allow some conditional logic in the exec/flow statements. ```"exec": "$1 == 80 ? sudo python controller.py 80", "flow": "##type## == 'web.py' ? :stop : :next"```

