##Conductor - Project/Task automation for local development

Basically the goal is to create a development workflow automation engine to make core workflow steps consistent and reusable across multiple mixes of scm, platforms, and environments.


###Example Global Tasks File

```json
{
	"editor": {
		"vim": {
			"open": ["vim ."]
		}
	},
	"scm": {
		"git": {
			"update": ["git pull"]
		},
		"hg": {
			"update": ["hg pull"]
		},
		"svn": {
			"update": ["svn update"]
		}
	},
	"type": {
		"php": {
			"start": ["rm ~/.phphome", "ln -s {this.public} ~/.phphome", "/Applications/MAMP/bin/apache2/bin/apachectl restart"],
			"build": ["run through php -l"]
		},
		"rails": {
			"start": ["rails server"]
		}
	}
}
```


###Example Project specific project file (.cue?)

```json
{
	"root_path": "/path/to/project_root",
	"public_path": "/path/to/project_root/public_html",
	"fullname": "Project Name",
	"slug": "project-name",
	"type": "php",
	"scm": "git",
	"editor": "vim",
	"workon": [":scm:update", ":type:start", ":editor:open" ],
	"tasks": [
		{"specific": [ "more", "commands", "to", "run" ]}
	]
}
```

###Tasks


Tasks can either be an array of sequential shell commands or prefixed with ```:``` can be another task global and/or local to the project.

You can also refer to the current "project" object with ```{this.property}``` within your shell commands.


###Commands


A few basic top level commands

```nocolor
cue register {path/to/existing/.cue (optional, uses pwd)}  //register a project (take you through Q/A to setup project)
cue unregister project-name  //unregister a project (make cue unaware of it)
cue workon project-name      //fire up 'workon' task to switch to said project
cue task {task name}         //fire off task (either global and/or overridden local task in a project)
```

You could also potentially run tasks on related (or dependant) projects without having to switch projects

```nocolor
cue task -p project-name {task name}
```
