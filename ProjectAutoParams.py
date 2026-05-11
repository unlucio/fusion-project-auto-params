import adsk.core, adsk.fusion, traceback, json, os, subprocess

# Global references to prevent garbage collection
handlers = []
app = adsk.core.Application.get()
ui = app.userInterface

json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'params.json')

default_fdm_data = [
    {"name": "layer_height", "value": "0.2mm", "unit": "mm", "comment": "Slicing layer height"},
    {"name": "nozzle_width", "value": "0.4mm", "unit": "mm", "comment": "Nozzle diameter"},
    {"name": "wall", "value": "nozzle_width*3", "unit": "mm", "comment": "Wall thickness"},
    {"name": "top", "value": "layer_height*5", "unit": "mm", "comment": "Top shell thickness"},
    {"name": "bottom", "value": "layer_height*3", "unit": "mm", "comment": "Bottom shell thickness"},
    {"name": "clearance", "value": "0.05mm", "unit": "mm", "comment": "Fit tolerance"}
]

def get_params():
    if not os.path.exists(json_path):
        with open(json_path, 'w') as params_file:
            json.dump(default_fdm_data, params_file, indent=4)
        return default_fdm_data
    with open(json_path, 'r') as params_file:
        return json.load(params_file)

def inject_parameters():
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return

        user_parameters = design.userParameters
        parameter_list = get_params()

        for parameter_data in parameter_list:
            name = parameter_data['name']
            if not user_parameters.itemByName(name):
                user_parameters.add(
                    name, 
                    adsk.core.ValueInput.createByString(parameter_data['value']), 
                    parameter_data['unit'], 
                    parameter_data['comment']
                )
    except:
        app.log(traceback.format_exc())

class DocumentActivatedHandler(adsk.core.DocumentEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        inject_parameters()

class EditParamsCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            if os.name == 'nt':
                os.startfile(json_path)
            else:
                subprocess.run(['open', json_path])
        except:
            ui.messageBox(f'Failed to open JSON:\n{traceback.format_exc()}')

class EditParamsCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        command = args.command
        on_execute = EditParamsCommandExecuteHandler()
        command.execute.add(on_execute)
        handlers.append(on_execute)

def run(context):
    try:
        on_activated = DocumentActivatedHandler()
        app.documentActivated.add(on_activated)
        handlers.append(on_activated)
        command_id = 'EditAutoParamsCommand'

        existing_def = ui.commandDefinitions.itemById(command_id)
        if existing_def:
            existing_def.deleteControl()

        edit_command_def = ui.commandDefinitions.addButtonDefinition(
            command_id, 
            'Edit Auto Params', 
            'Modify default parameters in JSON'
        )

        on_created = EditParamsCommandCreatedHandler()
        edit_command_def.commandCreated.add(on_created)
        handlers.append(on_created)

        tools_tab = ui.allToolbarTabs.itemById('ToolsTab')
        addins_panel = tools_tab.toolbarPanels.itemById('SolidScriptsAddinsPanel')
        addins_panel.controls.addCommand(edit_command_def)

        inject_parameters()

    except:
        ui.messageBox(f'Startup Failed:\n{traceback.format_exc()}')

def stop(context):
    try:
        for handler in handlers:
            if isinstance(handler, DocumentActivatedHandler):
                app.documentActivated.remove(handler)

        command_id = 'EditAutoParamsCommand'
        edit_command_def = ui.commandDefinitions.itemById(command_id)
        if edit_command_def:
            edit_command_def.deleteControl()

        handlers.clear()
    except:
        pass