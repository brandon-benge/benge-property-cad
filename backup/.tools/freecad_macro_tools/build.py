"""Rebuild the FreeCAD model with automatic module reloading."""
import importlib
import os
import sys
import traceback

import FreeCAD as App

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(TOOLS_DIR)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None


def _doc_name():
    try:
        import config
        importlib.reload(config)
        return getattr(config, "PROJECT_NAME", "FreeCADProject")
    except Exception:
        return "FreeCADProject"


def _collect_descendants(obj):
    names = []
    if hasattr(obj, "Group"):
        for child in obj.Group:
            names.extend(_collect_descendants(child))
    names.append(obj.Name)
    return names


def _clean_generated(doc):
    for obj in list(doc.Objects):
        if obj.Name == "GeneratedModel" or obj.Label == "GeneratedModel":
            for name in _collect_descendants(obj):
                try:
                    doc.removeObject(name)
                except Exception:
                    pass
            return


def _remove_freecad_backups(doc_name):
    removed = []
    for filename in os.listdir(HERE):
        if filename.startswith(f"{doc_name}.") and filename.endswith(".FCBak"):
            path = os.path.join(HERE, filename)
            try:
                os.remove(path)
                removed.append(path)
            except OSError:
                pass
    return removed


def rebuild():
    doc_name = _doc_name()
    try:
        import config
        import model
        from freecad_macro_tools import helpers

        importlib.reload(config)
        importlib.reload(helpers)
        importlib.reload(model)
        doc_name = getattr(config, "PROJECT_NAME", doc_name)

        try:
            doc = App.getDocument(doc_name)
        except NameError:
            doc = App.newDocument(doc_name)

        if Gui:
            try:
                Gui.setActiveDocument(doc)
            except Exception:
                pass

        _clean_generated(doc)

        generated = doc.addObject("App::Part", "GeneratedModel")
        model.build_model(doc, generated)
        doc.recompute()

        output = os.path.join(HERE, f"{doc_name}.FCStd")
        doc.saveAs(output)
        removed_backups = _remove_freecad_backups(doc_name)

        if Gui:
            try:
                view = Gui.getDocument(doc_name).activeView()
                view.viewAxonometric()
                view.fitAll()
                view.redraw()
            except Exception:
                pass

        print(f"{doc_name} rebuild completed.\nSaved: {output}")
        for path in removed_backups:
            print(f"Removed FreeCAD backup: {path}")
        return True

    except Exception:
        print(f"{doc_name} rebuild failed. See traceback above.")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    rebuild()
