##Cue - A Project/Task automator for local development

Basically the goal is to create a development workflow automation engine to make core workflow steps consistent and reusable across multiple mixes of scm, platforms, and environments.

### Usage

A few basic top level commands

```nocolor
cue register                 // register a project (take you through Q/A to setup project)
cue unregister project-name  // unregister a project (make cue unaware of it)
cue workon project-name      // run 'workon' task (switch to project root, and run desired tasks)
cue {task name}              // fire off task (either global and/or overridden local task in a project)
```

You could also potentially run tasks on related (or dependant) projects without having to switch projects

```nocolor
cue -p project-name {task name}
```

### Setup and Task Hierarchy

#### Global (~/.cueconf)

Example format of the `~/.cueconf` file at the most basic level

    {
        "projects" {
            "slug": "/path/to/project/.cuefile"
        },
        "tasks": {
            "group": {
                "type": {
                    "action1": ["shell", "commands", "to", "run"],
                    "action2": ["shell", "commands", "to", "run"]
                },
                "type2": {
                    "action3": ["shell", "commands", "to", "run"],
                    "action4": ["shell", "commands", "to", "run"]
                }
            }
            "group2": {
                "type": {
                    "action5": ["shell", "commands", "to", "run"],
                    "action6": ["shell", "commands", "to", "run"]
                },
                "type2": {
                    "action7": ["shell", "commands", "to", "run"],
                    "action8": ["shell", "commands", "to", "run"]
                }
            }
        }
    }

These settings define and namespace tasks that can be run within projects and are completely open ended...

A non generic example

    {
        "editor": {
            "vim": {
                "open": "vim ."
            },
            "sublime": {
                "open": "subl ."
            }
        },
        "scm": {
            "git": {
                "update": ["git pull"]
            },
            "hg": {
                "update": ["hg pull"]
            }
            "svn": {
                "update": ["svn update"]
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
        "type":"django",
        "tasks": {                               <-- required
            "workon": [":update",":open"]        <-- required
        }
    }

Then when you use ```cue workon my-project``` from anywhere in the system it goes to the root of the project, updates from your scm, and opens your editor based on your settings.

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
        "flow": "[continue|stop]"
    }


The `exec` property is equivilent to the string preveously expected, but providing `onError` will give you the opportunitiy to "clean up" after a failed command and/or stop on the error.

If you do not want the system to continue through a failed command (default), simply define `onError` as `{"flow":"stop"}`.


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
        "hg": {
            "update": [{
                "exec":"hg pull",
                "onError: { "flow":"stop" } // stop executing if a command fails
            }]
        },
        "svn": {
            "update": ["svn update"]  // continues if command does not complete successfully (default behaviour)
        }
    },
    ...
