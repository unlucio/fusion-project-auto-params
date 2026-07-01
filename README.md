# ProjectAutoParams: Fusion 360 Add-In

<a href="https://www.buymeacoffee.com/unlucio" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me a Coffee" style="height: 60px !important;width: 217px !important;" ></a>

A tiny Autodesk Fusion 360 add-in that automatically adds your favorite user
parameters (layer height, nozzle width, wall thickness, etc.) to every new design,
so you don't have to type them in by hand each time.

## What it does

- The moment you activate a document (new or existing), the add-in checks the
  active design's user parameters and adds any that are missing, using the
  values from a small `params.json` file.
- Ships with sensible defaults for FDM 3D printing: layer height, nozzle width,
  wall/top/bottom thickness, and fit clearance. Several are expressions derived
  from the others (e.g. `wall = nozzle_width * 3`), so changing one value
  cascades automatically.
- Adds an **Edit Auto Params** button that opens a dialog for adding, removing,
  and editing parameters in a table, no JSON editing or restart required.
- Never overwrites a parameter that already exists in the design; it only fills
  in what's missing.

## Installation

Download the latest `ProjectAutoParams.zip` from the
[Releases page](../../releases/latest) and unzip it. You'll get a
`ProjectAutoParams` folder (containing `ProjectAutoParams.py`,
`ProjectAutoParams.manifest`, `AddInIcon.svg`, `LICENSE`, `params.json`, the
`resources/` icons, and this `README.md`), already named exactly as Fusion
requires. Then install it with either method below.

### Option A: from Fusion's Scripts and Add-Ins dialog (easiest, no folder-hunting)

If you don't know (or don't want to know) where Fusion keeps its add-ins, let
Fusion copy the folder in for you:

1. In Fusion: **Utilities** tab → **ADD-INS** panel → **Scripts and Add-Ins**
   (or press `Shift+S`).
2. Click the **+** dropdown at the top-left of the dialog → **Script or add-in
   from device**.
3. Browse to and select the `ProjectAutoParams` folder (the one that contains
   the `.manifest` file) and confirm. Fusion copies it into the correct add-ins
   directory automatically.
4. It now shows up in the **Add-Ins** tab of the list. Select
   **ProjectAutoParams** and click **Run**, and tick **Run on Startup** so it's
   always active (the whole point of this add-in is that it runs quietly in the
   background).

### Option B: manual copy

1. Copy the entire `ProjectAutoParams/` folder into your Fusion add-ins
   directory:
   - **macOS:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
   - **Windows:** `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`

   The folder, the `.py`, and the `.manifest` must all share the base name
   `ProjectAutoParams`.

2. In Fusion: **Utilities** tab → **ADD-INS** → **Scripts and Add-Ins**
   (`Shift+S`) → **Add-Ins** tab → select **ProjectAutoParams** → **Run** →
   tick **Run on Startup**.

Either way, an **AUTO PARAMS** panel (with an **Edit Auto Params** button) appears
at the end of the **Utilities** tab's toolbar.

## How to use

1. Just start or open a design. The add-in silently adds any missing parameters
   from `params.json` to the design's user parameters as soon as the document
   becomes active. No dialog, no button press needed for this part.
2. To change which parameters get added, or their values, click
   **Edit Auto Params**. A dialog opens with one row per parameter:
   - Type in any cell (**Name**, **Value**, **Unit**, **Comment**) to edit it.
   - Click **Add** in the dialog's toolbar to append a new blank row.
   - Click the minus icon at the right of a row to delete it.
   - Click **OK** to save. The next document you activate will pick up the new
     values.
3. Existing parameters are never touched: if a design already has a parameter
   with the same name, the add-in leaves it alone. That means you can freely
   override any auto-added value per-design without it getting reset.

## The parameters file

The **Edit Auto Params** dialog is the recommended way to change parameters, but
under the hood it just reads and writes `params.json`, a plain JSON array next
to `ProjectAutoParams.py`. You can also edit it by hand if you prefer. Each
entry becomes one user parameter:

```json
{
  "name": "wall",
  "value": "nozzle_width*3",
  "unit": "mm",
  "comment": "Wall thickness"
}
```

- **name**: the parameter name as it will appear in Fusion's parameters dialog.
- **value**: anything Fusion's expression parser accepts: a plain number, a
  number with a unit, or an expression referencing another parameter (evaluated
  in file order, so a parameter can only reference ones defined earlier in the
  list).
- **unit**: the unit to associate with the parameter (e.g. `mm`).
- **comment**: shown as the parameter's description/comment in Fusion.

Ships with these FDM printing defaults:

| Name | Value | Comment |
|------|-------|---------|
| `layer_height` | `0.2mm` | Slicing layer height |
| `nozzle_width` | `0.4mm` | Nozzle diameter |
| `wall` | `nozzle_width*3` | Wall thickness |
| `top` | `layer_height*5` | Top shell thickness |
| `bottom` | `layer_height*3` | Bottom shell thickness |
| `clearance` | `0.05mm` | Fit tolerance |

If `params.json` is ever missing (first run, or you deleted it), it's recreated
with these same defaults.

## Notes & limits

- Parameters are added on **document activation**: opening a design, switching
  tabs back to it, or creating a new one all count. If you add a brand-new
  parameter to `params.json` while a design is already open and active, switch
  away and back (or reopen the file) to trigger the check again.
- The add-in only ever **adds** parameters. It never deletes or renames ones you
  remove from `params.json`, and it never overwrites a value you've changed by
  hand in an existing design.
- `params.json` lives next to `ProjectAutoParams.py` inside the add-in folder,
  so it's shared across every design on your machine; it's not per-project.

## License

This add-in's own code (`ProjectAutoParams.py`, `ProjectAutoParams.manifest`,
this README) is licensed under the **GNU Affero General Public License v3.0 or
later (AGPL-3.0-or-later)**. The full text is in [`LICENSE`](LICENSE).
