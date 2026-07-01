# ProjectAutoParams -- automatically sets default user parameters in every new Fusion 360 project.
#
# Copyright (c) 2026 unLucio -- GNU Affero General Public License v3.0 or later (see LICENSE).
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
# It is distributed WITHOUT ANY WARRANTY; see the GNU AGPL for details.

import adsk.core, adsk.fusion, traceback, json, os

# Global references to prevent garbage collection
handlers = []
app = adsk.core.Application.get()
ui = app.userInterface

json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'params.json')
icon_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
remove_icon_folder = os.path.join(icon_folder, 'remove')

COMMAND_ID = 'EditAutoParamsCommand'
WORKSPACE_ID = 'FusionSolidEnvironment'  # Design workspace.
TAB_ID = 'ToolsTab'  # The UTILITIES tab (internal id predates the "Utilities" rename).
PANEL_ID = 'projectAutoParamsPanel'  # Our own dedicated panel, at the end of the UTILITIES tab.
PANEL_NAME = 'AUTO PARAMS'

TABLE_ID = 'paramsTable'
ADD_ROW_ID = 'addRowBtn'
REMOVE_ROW_PREFIX = 'removeRow_'
COLUMN_NAMES = ['name', 'value', 'unit', 'comment']

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

def add_table_row(table_input, param=None):
    param = param or {'name': '', 'value': '', 'unit': '', 'comment': ''}
    row = table_input.rowCount
    cell_inputs = table_input.commandInputs
    name_input = cell_inputs.addStringValueInput(f'name_{row}', 'Name', param['name'])
    value_input = cell_inputs.addStringValueInput(f'value_{row}', 'Value', param['value'])
    unit_input = cell_inputs.addStringValueInput(f'unit_{row}', 'Unit', param['unit'])
    comment_input = cell_inputs.addStringValueInput(f'comment_{row}', 'Comment', param['comment'])
    remove_input = cell_inputs.addBoolValueInput(
        f'{REMOVE_ROW_PREFIX}{row}', 'Remove parameter', False, remove_icon_folder, True
    )
    table_input.addCommandInput(name_input, row, 0)
    table_input.addCommandInput(value_input, row, 1)
    table_input.addCommandInput(unit_input, row, 2)
    table_input.addCommandInput(comment_input, row, 3)
    table_input.addCommandInput(remove_input, row, 4)

class EditParamsInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, table_input):
        super().__init__()
        self.table_input = table_input
    def notify(self, args):
        changed_input = args.input
        if changed_input.id == ADD_ROW_ID:
            add_table_row(self.table_input)
        elif changed_input.id.startswith(REMOVE_ROW_PREFIX):
            found, row, column, row_span, column_span = self.table_input.getPosition(changed_input)
            if found:
                self.table_input.deleteRow(row)

class EditParamsCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, table_input):
        super().__init__()
        self.table_input = table_input
    def notify(self, args):
        try:
            params = []
            for row in range(self.table_input.rowCount):
                cells = {
                    column_name: adsk.core.StringValueCommandInput.cast(
                        self.table_input.getInputAtPosition(row, column)
                    ).value.strip()
                    for column, column_name in enumerate(COLUMN_NAMES)
                }
                if cells['name']:
                    params.append(cells)
            with open(json_path, 'w') as params_file:
                json.dump(params, params_file, indent=4)
        except:
            ui.messageBox(f'Failed to save parameters:\n{traceback.format_exc()}')

class EditParamsCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        command = args.command
        command.setDialogInitialSize(500, 400)
        command.setDialogMinimumSize(500, 300)

        inputs = command.commandInputs
        table_input = inputs.addTableCommandInput(TABLE_ID, 'Parameters', 5, '3:3:2:4:1')
        table_input.maximumVisibleRows = 8
        table_input.minimumVisibleRows = 3

        add_row_input = inputs.addBoolValueInput(ADD_ROW_ID, 'Add', False, '', True)
        table_input.addToolbarCommandInput(add_row_input)

        for param in get_params():
            add_table_row(table_input, param)

        on_input_changed = EditParamsInputChangedHandler(table_input)
        command.inputChanged.add(on_input_changed)
        handlers.append(on_input_changed)

        on_execute = EditParamsCommandExecuteHandler(table_input)
        command.execute.add(on_execute)
        handlers.append(on_execute)

def run(context):
    try:
        on_activated = DocumentActivatedHandler()
        app.documentActivated.add(on_activated)
        handlers.append(on_activated)

        existing_def = ui.commandDefinitions.itemById(COMMAND_ID)
        if existing_def:
            existing_def.deleteMe()

        edit_command_def = ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID,
            'Edit Auto Params',
            'Add, remove, or edit the default parameters',
            icon_folder
        )

        on_created = EditParamsCommandCreatedHandler()
        edit_command_def.commandCreated.add(on_created)
        handlers.append(on_created)

        tab = ui.workspaces.itemById(WORKSPACE_ID).toolbarTabs.itemById(TAB_ID)
        panel = tab.toolbarPanels.itemById(PANEL_ID)
        if not panel:
            panel = tab.toolbarPanels.add(PANEL_ID, PANEL_NAME)
        elif panel.name != PANEL_NAME:
            panel.name = PANEL_NAME

        existing_control = panel.controls.itemById(COMMAND_ID)
        if existing_control:
            existing_control.deleteMe()
        control = panel.controls.addCommand(edit_command_def)
        control.isPromoted = True
        control.isPromotedByDefault = True

        inject_parameters()

    except:
        ui.messageBox(f'Startup Failed:\n{traceback.format_exc()}')

def stop(context):
    try:
        for handler in handlers:
            if isinstance(handler, DocumentActivatedHandler):
                app.documentActivated.remove(handler)

        tab = ui.workspaces.itemById(WORKSPACE_ID).toolbarTabs.itemById(TAB_ID)
        panel = tab.toolbarPanels.itemById(PANEL_ID)
        if panel:
            control = panel.controls.itemById(COMMAND_ID)
            if control:
                control.deleteMe()
            if panel.controls.count == 0:
                panel.deleteMe()

        edit_command_def = ui.commandDefinitions.itemById(COMMAND_ID)
        if edit_command_def:
            edit_command_def.deleteMe()

        handlers.clear()
    except:
        pass