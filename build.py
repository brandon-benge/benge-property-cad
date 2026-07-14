"""Rebuild the BengeBackyard model with automatic module reloading."""
import importlib
import os
import sys
import traceback

import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None

DOC_NAME = "BengeBackyard"

GENERATED_ROOTS = {
    "GeneratedModel",
    # Legacy roots created by earlier macro versions before GeneratedModel existed.
    "Site",
    "House",
    "HouseMass",
    "Decks",
    "Stairs",
    "Railings",
    "Skirting",
    "Features",
    "PoolArea",
}


def _collect_descendants(obj):
    """DFS collecting object names bottom-up (children before parent)."""
    names = []
    if hasattr(obj, "Group"):
        for child in obj.Group:
            names.extend(_collect_descendants(child))
    names.append(obj.Name)
    return names


def _clean_generated(doc):
    """Remove generated model trees from current and earlier macro versions."""
    names_to_remove = []
    for obj in list(doc.Objects):
        if obj.Name in GENERATED_ROOTS or obj.Label in GENERATED_ROOTS:
            names_to_remove.extend(_collect_descendants(obj))

    for name in dict.fromkeys(names_to_remove):
        try:
            doc.removeObject(name)
        except Exception:
            pass


def rebuild():
    try:
        import config
        import helpers
        import model

        importlib.reload(config)
        importlib.reload(helpers)
        importlib.reload(model)

        try:
            doc = App.getDocument(DOC_NAME)
        except NameError:
            doc = App.newDocument(DOC_NAME)

        if Gui:
            try:
                Gui.setActiveDocument(doc)
            except Exception:
                pass

        _clean_generated(doc)

        generated = doc.addObject("App::Part", "GeneratedModel")
        model.build_model(doc, generated)

        doc.recompute()

        output = os.path.join(HERE, f"{DOC_NAME}.FCStd")
        doc.saveAs(output)

        if Gui:
            try:
                gv = Gui.getDocument(DOC_NAME).activeView()
                gv.viewAxonometric()
                gv.fitAll()
                gv.redraw()
            except Exception:
                pass

        print(f"{DOC_NAME} rebuild completed.\nSaved: {output}")

    except Exception:
        print(f"{DOC_NAME} rebuild failed. See traceback above.")
        traceback.print_exc()


if __name__ == "__main__":
    rebuild()
