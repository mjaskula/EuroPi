# Config Menu
A menu which allows the user to edit configuration parameters for both participating scripts and 
global parameters. The menu will include the ``EuroPiScripts`` included in the ``CONFIG_CLASSES`` 
List.

    In the menu:

    * **Button 1:** go back
    * **Button 2:** choose the selected menu item, save the current config value
    * **Knob 1:** unused
    * **Knob 2:** change the current selection
    * **ain/din:** unsed
    * **cv outs:** unused

The intention of these configuration points is to allow for in-module (rather than in code) user editing parameters that
aren't expected to change very often. These are 'set and forget' type options that the user would not expect to be able
to change while the script is running. This allows the script itself to forgo the UI complexities of making these options
editable.

## Script requirements

A ``EuroPiScript`` which wishes to have configuration parameters editable in the config menu needs 
to implement one additional method beyond those required for menu participation. (See the 
[menu documentation](/software/contrib/menu.md) for details on menu participation.) An example is 
shown below:

``config_example.py``
```Python
from europi_script import EuroPiScript
from config_points import ConfigPointsBuilder  # 1

class ConfigExample(EuroPiScript):
    
    def __init__(self):
        super().__init__()
        self.cv_output = self.config["cv_output"] == "on"  # 4
        self.max_cv = self.config["max_cv"]

    # other methods removed for simplicity

    @classmethod
    def config_points(cls, config_builder: ConfigPointsBuilder):  # 2
        return config_builder.with_choice(
            name="cv_output", choices=["on", "off"], default="on"  # 3
        ).with_int(
            name="max_cv", start=5, stop=11, default=5
        )

```

1. **Import ``ConfigPointsBuilder``:** Import the ``ConfigPointsBuilder`` class so that we can use it below.
2. **Implement `config_points()`:** This method defines the config points that the script uses. It takes a `ConfigPointsBuilder` as a parameter, adds config points to it, and returns it.
3. **Define config points:** ``ConfigPointsBuilder`` provides `with_` methods that provide the details of the config points including their name, range, and default value. Various types of config points are available, see `ConfigPointsBuilder` for details.
4. **Read config points:** The value of the configuration points is provided to the script via the `config` member variable. `config` is a dict whose key is the config point name and whose value is the config point value. Any point that has not been set by the user via the app will use the default value.

## Menu Inclusion

Once you have a script that conforms to the above requirements, you can add it to the list of scripts that are included
in the confg menu. This list is in [config.py](/software/contrib/config.py) in the contrib folder. You will need to add
two lines, one to import your class and one to add the class to the list. Use the existing scripts as examples.

Note that the scripts are sorted before being displayed, so order in this file doesn't matter.

