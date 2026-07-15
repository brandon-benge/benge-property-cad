"""Shared actions used by FreeCAD macros."""
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import warnings

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(TOOLS_DIR)
VENV_DIR = os.path.join(HERE, ".macro_venvs", "autocommit")
IS_WINDOWS = os.name == "nt"
VENV_BIN = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin")
VENV_PYTHON = os.path.join(VENV_BIN, "python.exe" if IS_WINDOWS else "python")
VENV_AUTOCOMMIT = os.path.join(VENV_BIN, "autocommit.exe" if IS_WINDOWS else "autocommit")

AUTOCOMMIT_REPO = "git+https://github.com/brandon-benge/langchain_autocommit.git"
AUTOCOMMIT_PARAMS_URL = (
    "https://raw.githubusercontent.com/brandon-benge/"
    "langchain_autocommit/main/params.yaml"
)
AUTOCOMMIT_DIR = os.path.join(HERE, ".autocommit")
AUTOCOMMIT_PARAMS_FILE = os.path.join(AUTOCOMMIT_DIR, "params.yaml")
MACRO_ENV_FILE = os.path.join(HERE, ".macro_env")
PROJECT_PARAMS_FILE = os.path.join(HERE, "params.yaml")
TEMPLATE_GITHUB_LOCATION = "brandon-benge/freecad_macro_project_template"
DEFAULT_PROJECT_PARAMS = {
    "project_name": None,
    "github_enabled": False,
    "github_location": None,
    "autocommit": False,
    "autocommit_params": None,
    "autocommit_override": "ask",
}

VERSIONING_PROMPT = (
    "Choose how this project should manage versions and rollback.\n\n"
    "Autocommit: installs git, GitHub CLI, and an isolated autocommit venv. "
    "Build.FCMacro can use autocommit after a successful build.\n\n"
    "Git: installs git and GitHub CLI. Build.FCMacro will commit and push "
    "with a generic build message after approval.\n\n"
    "Nothing: no versioning setup. Build.FCMacro will only rebuild, and "
    "Revert.FCMacro will show an error until git/autocommit is available."
)


def _run(command):
    result = subprocess.run(
        command,
        cwd=HERE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: {' '.join(command)}"
        )
    return result


def _run_or_error(command):
    try:
        return _run(command)
    except Exception as exc:
        show_error("Macro Error", str(exc))
        raise


def _capture(command):
    return subprocess.run(
        command,
        cwd=HERE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _qt_widgets():
    try:
        from PySide import QtGui
        return QtGui
    except ImportError:
        from PySide2 import QtWidgets
        return QtWidgets


def show_error(title, message):
    widgets = _qt_widgets()
    widgets.QMessageBox.critical(None, title, message)


def show_info(title, message):
    widgets = _qt_widgets()
    widgets.QMessageBox.information(None, title, message)


def _prompt_text(title, label, default=""):
    widgets = _qt_widgets()

    value, ok = widgets.QInputDialog.getText(None, title, label, text=default)
    if not ok:
        raise RuntimeError("Canceled.")
    value = str(value).strip()
    if not value:
        raise RuntimeError(f"{label} is required.")
    return value


def _prompt_secret(title, label):
    widgets = _qt_widgets()
    value, ok = widgets.QInputDialog.getText(
        None,
        title,
        label,
        echo=widgets.QLineEdit.Password,
    )
    if not ok:
        return ""
    return str(value).strip()


def _prompt_yes_no(title, message):
    widgets = _qt_widgets()
    answer = widgets.QMessageBox.question(
        None,
        title,
        message,
        widgets.QMessageBox.Yes | widgets.QMessageBox.No,
        widgets.QMessageBox.Yes,
    )
    return answer == widgets.QMessageBox.Yes


def _prompt_choice(title, label, items, default=None):
    widgets = _qt_widgets()
    index = items.index(default) if default in items else 0
    value, ok = widgets.QInputDialog.getItem(
        None,
        title,
        label,
        items,
        index,
        False,
    )
    if not ok:
        raise RuntimeError("Canceled.")
    return str(value).strip()


def prompt_for_versioning_mode():
    widgets = _qt_widgets()
    items = ["Autocommit", "Git", "Nothing"]
    value, ok = widgets.QInputDialog.getItem(
        None,
        "Version Management",
        VERSIONING_PROMPT,
        items,
        0,
        False,
    )
    if not ok:
        raise RuntimeError("Canceled.")
    return str(value).strip().lower()


def _safe_project_name(value):
    value = re.sub(r"\W+", "_", str(value).strip())
    value = value.strip("_")
    if not value:
        raise RuntimeError("Project name is required.")
    if value[0].isdigit():
        value = f"Project_{value}"
    return value


def set_project_name(project_name):
    project_name = _safe_project_name(project_name)
    config_path = os.path.join(HERE, "config.py")
    if not os.path.exists(config_path):
        raise RuntimeError(f"Could not find config.py at {config_path}")

    with open(config_path, "r", encoding="utf-8") as config_file:
        lines = config_file.readlines()

    assignment = f"PROJECT_NAME = {project_name!r}\n"
    for index, line in enumerate(lines):
        if line.lstrip().startswith("PROJECT_NAME"):
            lines[index] = assignment
            break
    else:
        lines.insert(0, assignment)

    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.writelines(lines)
    return project_name


def configure_project_name():
    try:
        import config
        current_name = getattr(config, "PROJECT_NAME", "")
    except Exception:
        current_name = ""

    default_name = current_name
    if not default_name or default_name == "FreeCADProject":
        default_name = os.path.basename(HERE).replace(" ", "_").replace("-", "_")

    project_name = _prompt_text(
        "Project Name",
        "Project name:",
        _safe_project_name(default_name),
    )
    project_name = set_project_name(project_name)
    show_info("Project Name", f"Configured project name:\n{project_name}")
    return project_name


def _parse_project_param_value(value):
    value = value.strip()
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    if value.lower() in ("null", "none", "~", ""):
        return None
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ("'", '"')
    ):
        return value[1:-1]
    return value


def _format_project_param_value(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None or value == "":
        return "null"
    value = str(value)
    if re.match(r"^[A-Za-z0-9_./:@-]+$", value):
        return value
    return repr(value)


def read_project_params():
    values = dict(DEFAULT_PROJECT_PARAMS)
    if not os.path.exists(PROJECT_PARAMS_FILE):
        write_project_params(values)
        return values

    with open(PROJECT_PARAMS_FILE, "r", encoding="utf-8") as params_file:
        for line in params_file:
            line = line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key in values:
                values[key] = _parse_project_param_value(value)
    return normalize_project_params(values)


def write_project_params(values):
    values = normalize_project_params(values)
    with open(PROJECT_PARAMS_FILE, "w", encoding="utf-8") as params_file:
        for key in DEFAULT_PROJECT_PARAMS:
            params_file.write(f"{key}: {_format_project_param_value(values[key])}\n")
    return values


def normalize_project_params(values):
    normalized = dict(DEFAULT_PROJECT_PARAMS)
    normalized.update(values or {})

    override = str(normalized.get("autocommit_override") or "ask").lower()
    if override not in ("ask", "true", "false"):
        override = "ask"
    normalized["autocommit_override"] = override

    location = normalized.get("github_location")
    if location is not None:
        normalized["github_location"] = str(location).strip() or None
    if normalized.get("project_name"):
        normalized["project_name"] = _safe_project_name(normalized["project_name"])

    if not normalized["autocommit"]:
        normalized["autocommit_params"] = None

    return normalized


def _require_boolean(params, key, errors):
    if not isinstance(params.get(key), bool):
        errors.append(f"{key} must be true or false.")


def validate_project_params_for_init():
    if not os.path.exists(PROJECT_PARAMS_FILE):
        raise RuntimeError(
            "Configuration must be done before running InitRepo.FCMacro. "
            "Run ConfigureParams.FCMacro first to create params.yaml."
        )

    params = read_project_params()
    errors = []
    _require_boolean(params, "github_enabled", errors)
    _require_boolean(params, "autocommit", errors)

    if not params.get("project_name"):
        errors.append("project_name is required.")
    if not params.get("github_enabled"):
        errors.append("github_enabled must be true before InitRepo.FCMacro can initialize GitHub.")
    if params.get("github_location"):
        try:
            params["github_location"] = validate_github_location(params["github_location"])
        except RuntimeError as exc:
            errors.append(str(exc))
    else:
        errors.append("github_location is required and must be owner/repository.")

    if params.get("autocommit"):
        if not params.get("autocommit_params"):
            errors.append("autocommit_params is required when autocommit is true.")
        elif not os.path.exists(str(params["autocommit_params"])):
            errors.append(f"autocommit_params file does not exist: {params['autocommit_params']}")
    elif params.get("autocommit_params") is not None:
        errors.append("autocommit_params must be null when autocommit is false.")

    if params.get("autocommit_override") not in ("ask", "true", "false"):
        errors.append("autocommit_override must be ask, true, or false.")

    if errors:
        raise RuntimeError(
            "Configuration must be done before running InitRepo.FCMacro. "
            "Run ConfigureParams.FCMacro and fix params.yaml:\n\n"
            + "\n".join(f"- {error}" for error in errors)
        )
    return params


def validate_github_location(value, allow_empty=False):
    if value is None:
        if allow_empty:
            return None
        raise RuntimeError("GitHub location is required.")
    value = str(value).strip()
    if not value:
        if allow_empty:
            return None
        raise RuntimeError("GitHub location is required.")
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("https://github.com/"):
        value = value[len("https://github.com/"):]
    value = value.strip("/")
    if value == TEMPLATE_GITHUB_LOCATION:
        raise RuntimeError(
            "GitHub location cannot be "
            f"{TEMPLATE_GITHUB_LOCATION}. Use the new project repository."
        )
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", value):
        raise RuntimeError("GitHub location must look like owner/repository.")
    return value


def load_project_params_env():
    params = read_project_params()
    env_values = {
        "PROJECT_NAME": params["project_name"],
        "GITHUB_ENABLED": str(params["github_enabled"]),
        "GITHUB_LOCATION": params["github_location"],
        "AUTOCOMMIT_ENABLED": str(params["autocommit"]),
        "AUTOCOMMIT_PARAMS": params["autocommit_params"],
        "AUTOCOMMIT_OVERRIDE": params["autocommit_override"],
    }
    for key, value in env_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(value)
    return params


def configure_project_params():
    params = read_project_params()

    default_project_name = params.get("project_name")
    if not default_project_name:
        try:
            import config
            default_project_name = getattr(config, "PROJECT_NAME", "")
        except Exception:
            default_project_name = ""
    if not default_project_name or default_project_name == "FreeCADProject":
        default_project_name = os.path.basename(HERE).replace(" ", "_").replace("-", "_")

    params["project_name"] = set_project_name(
        _prompt_text(
            "Project Name",
            "Project name:",
            _safe_project_name(default_project_name),
        )
    )

    params["github_enabled"] = _prompt_yes_no(
        "Project Parameters",
        "Enable GitHub versioning for this project?",
    )
    if params["github_enabled"]:
        default_location = params.get("github_location") or ""
        location = _prompt_text(
            "GitHub Location",
            "GitHub location (owner/repository):",
            default_location,
        )
        params["github_location"] = validate_github_location(location)
    else:
        params["github_location"] = None

    if params["github_enabled"]:
        params["autocommit"] = _prompt_yes_no(
            "Autocommit",
            "Enable autocommit for this project?",
        )
    else:
        params["autocommit"] = False

    if params["autocommit"]:
        if _prompt_yes_no(
            "Autocommit Parameters",
            "Download and use the default langchain_autocommit params.yaml?",
        ):
            os.makedirs(AUTOCOMMIT_DIR, exist_ok=True)
            print(f"Downloading autocommit params from {AUTOCOMMIT_PARAMS_URL}")
            urllib.request.urlretrieve(AUTOCOMMIT_PARAMS_URL, AUTOCOMMIT_PARAMS_FILE)
            params["autocommit_params"] = AUTOCOMMIT_PARAMS_FILE
        else:
            current = params.get("autocommit_params") or ""
            custom = _prompt_text(
                "Autocommit Parameters",
                "AUTOCOMMIT_PARAMS file path:",
                current,
            )
            params["autocommit_params"] = custom

        values = _read_macro_env()
        api_key = _prompt_secret(
            "OpenCode API Key",
            "Enter OPENCODE_API_KEY for autocommit, or leave blank to keep current value:",
        )
        if api_key:
            values["OPENCODE_API_KEY"] = api_key
            _write_macro_env(values)
    else:
        params["autocommit_params"] = None

    params["autocommit_override"] = _prompt_choice(
        "Autocommit Override",
        "Build commit prompt behavior:",
        ["ask", "true", "false"],
        params.get("autocommit_override", "ask"),
    )

    params = write_project_params(params)
    load_project_params_env()
    show_info(
        "Project Parameters",
        "Updated params.yaml.\n\n"
        f"Project Name: {params['project_name']}\n"
        f"GitHub Enabled: {params['github_enabled']}\n"
        f"GitHub Location: {params['github_location'] or 'None'}\n"
        f"Autocommit: {params['autocommit']}\n"
        f"AUTOCOMMIT_PARAMS: {params['autocommit_params'] or 'None'}\n"
        f"Auto Commit Override: {params['autocommit_override']}",
    )
    return params


def _read_macro_env():
    values = {}
    if not os.path.exists(MACRO_ENV_FILE):
        return values
    with open(MACRO_ENV_FILE, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def _write_macro_env(values):
    with open(MACRO_ENV_FILE, "w", encoding="utf-8") as env_file:
        env_file.write("# Local macro environment. Do not commit secrets.\n")
        for key in sorted(values):
            env_file.write(f"{key}={values[key]}\n")


def load_macro_env():
    for key, value in _read_macro_env().items():
        os.environ.setdefault(key, value)


def configure_autocommit_environment():
    """Optionally download params.yaml and persist env vars for autocommit."""
    params = read_project_params()
    values = _read_macro_env()
    changed = False

    if _prompt_yes_no(
        "Autocommit Parameters",
        "Download the default autocommit params.yaml and configure "
        "AUTOCOMMIT_PARAMS for this project?",
    ):
        os.makedirs(AUTOCOMMIT_DIR, exist_ok=True)
        print(f"Downloading autocommit params from {AUTOCOMMIT_PARAMS_URL}")
        urllib.request.urlretrieve(AUTOCOMMIT_PARAMS_URL, AUTOCOMMIT_PARAMS_FILE)

        params["autocommit_params"] = AUTOCOMMIT_PARAMS_FILE
        params["autocommit"] = True
        changed = True

    api_key = _prompt_secret(
        "OpenCode API Key",
        "Enter OPENCODE_API_KEY for autocommit, or leave blank to keep current value:",
    )
    if api_key:
        values["OPENCODE_API_KEY"] = api_key
        changed = True

    if changed:
        write_project_params(params)
        _write_macro_env(values)
    load_project_params_env()
    load_macro_env()

    params_value = params.get("autocommit_params") or os.environ.get("AUTOCOMMIT_PARAMS")
    params_message = params_value or "not configured"
    api_key_message = "configured" if values.get("OPENCODE_API_KEY") or os.environ.get("OPENCODE_API_KEY") else "not configured"
    show_info(
        "Autocommit Environment",
        "AUTOCOMMIT_PARAMS: "
        f"{params_message}\nOPENCODE_API_KEY: {api_key_message}",
    )


def _system_python():
    for executable in ("py", "python3", "python"):
        python = shutil.which(executable)
        if python:
            if executable == "py":
                return [python, "-3"]
            return [python]
    return sys.executable


def _autocommit_executable():
    if os.path.exists(VENV_AUTOCOMMIT):
        return VENV_AUTOCOMMIT
    return shutil.which("autocommit")


def _install_with_winget(executable, package_id):
    winget = shutil.which("winget")
    if winget is None:
        raise RuntimeError(
            f"`{executable}` is required but was not found. Install it manually "
            "or install Windows Package Manager (`winget`), then retry."
        )

    print(f"{executable} not found. Installing {package_id} with winget...")
    _run([
        winget,
        "install",
        "--id",
        package_id,
        "--exact",
        "--source",
        "winget",
        "--accept-package-agreements",
        "--accept-source-agreements",
    ])
    for path in (
        os.path.expandvars(r"%ProgramFiles%\Git\cmd"),
        os.path.expandvars(r"%ProgramFiles%\GitHub CLI"),
    ):
        if os.path.isdir(path) and path not in os.environ.get("PATH", "").split(os.pathsep):
            os.environ["PATH"] = f"{path}{os.pathsep}{os.environ.get('PATH', '')}"
    if shutil.which(executable) is None:
        raise RuntimeError(f"`{executable}` was installed but is still not on PATH.")


def _install_with_homebrew(executable, package):
    brew = shutil.which("brew")
    if brew is None:
        for candidate in ("/opt/homebrew/bin/brew", "/usr/local/bin/brew"):
            if os.path.exists(candidate):
                brew = candidate
                break
    if brew is None:
        raise RuntimeError(
            f"`{executable}` is required but was not found. Install Homebrew "
            f"or install `{package}` manually, then retry."
        )

    brew_bin = os.path.dirname(brew)
    current_path = os.environ.get("PATH", "")
    if brew_bin not in current_path.split(os.pathsep):
        os.environ["PATH"] = f"{brew_bin}{os.pathsep}{current_path}"

    print(f"{executable} not found. Installing {package} with Homebrew...")
    _run([brew, "install", package])
    if shutil.which(executable) is None:
        raise RuntimeError(f"`{executable}` was installed but is still not on PATH.")


def _ensure_tool_installed(executable, brew_package, winget_package):
    if shutil.which(executable) is not None:
        return

    if IS_WINDOWS:
        _install_with_winget(executable, winget_package)
        return

    try:
        _install_with_homebrew(executable, brew_package)
    except RuntimeError as exc:
        raise RuntimeError(
            f"{exc}\n\nOn Windows, install with winget package `{winget_package}`."
        )


def ensure_git_installed():
    _ensure_tool_installed("git", "git", "Git.Git")


def ensure_gh_installed():
    _ensure_tool_installed("gh", "gh", "GitHub.cli")


def ensure_autocommit_installed():
    """Install autocommit into a project-local venv if it is missing."""
    if os.path.exists(VENV_AUTOCOMMIT):
        return

    print(f"autocommit CLI not found. Installing into isolated venv: {VENV_DIR}")
    if os.path.isdir(VENV_DIR):
        shutil.rmtree(VENV_DIR)
    os.makedirs(os.path.dirname(VENV_DIR), exist_ok=True)
    _run(_system_python() + ["-m", "venv", VENV_DIR])
    _run([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip"])
    _run([VENV_PYTHON, "-m", "pip", "install", AUTOCOMMIT_REPO])

    if not os.path.exists(VENV_AUTOCOMMIT):
        raise RuntimeError(
            f"autocommit installed but was not found at {VENV_AUTOCOMMIT}."
        )

    print("autocommit installed successfully in isolated venv.")


def autocommit():
    """Run the configured autocommit command."""
    load_project_params_env()
    load_macro_env()
    if not os.environ.get("AUTOCOMMIT_PARAMS"):
        warnings.warn(
            "AUTOCOMMIT_PARAMS is not set; autocommit will use its own defaults.",
            RuntimeWarning,
        )
    executable = _autocommit_executable()
    if executable is None:
        raise RuntimeError("autocommit is not available.")
    return _run([executable])


def git_commit_and_push(message="Build FreeCAD model"):
    """Commit changed files with git and push if a git repo is configured."""
    if shutil.which("git") is None:
        print("git is not available. Skipping versioning.")
        return False
    if not os.path.isdir(os.path.join(HERE, ".git")):
        print("No git repository found. Skipping versioning.")
        return False

    _run(["git", "add", "-A"])
    staged = _capture(["git", "diff", "--cached", "--quiet"])
    if staged.returncode == 0:
        print("No git changes to commit.")
        return False

    _run(["git", "commit", "-m", message])
    remote = _capture(["git", "remote", "get-url", "origin"])
    if remote.returncode == 0:
        _run(["git", "push"])
    else:
        print("No origin remote configured. Commit created locally only.")
    return True


def _prompt_for_versioning_approval(tool_name):
    override = os.environ.get("AUTOCOMMIT_OVERRIDE", "ask").lower()
    if override == "true":
        return True
    if override == "false":
        return False
    return _prompt_yes_no(
        "Commit Build Changes",
        f"Build completed. Commit the changes with {tool_name}?",
    )


def build_version_if_available():
    """Prefer autocommit, fall back to git, otherwise skip versioning."""
    params = load_project_params_env()
    if not params["github_enabled"]:
        print("GitHub versioning is disabled in params.yaml. Build completed without commit.")
        return None

    if params["autocommit"] and _autocommit_executable() is not None:
        if not _prompt_for_versioning_approval("autocommit"):
            print("Build completed. Versioning skipped by user.")
            return None
        print("Versioning with autocommit.")
        return autocommit()
    if shutil.which("git") is not None:
        if not _prompt_for_versioning_approval("git"):
            print("Build completed. Versioning skipped by user.")
            return None
        print("Versioning with git.")
        return git_commit_and_push()
    print("No versioning tool available. Build completed without commit.")
    return None


def revert_last_commit_and_push():
    """Revert HEAD with a new commit, push it upstream, then return."""
    if shutil.which("git") is None:
        raise RuntimeError("Cannot revert: git is not installed.")
    if not os.path.isdir(os.path.join(HERE, ".git")):
        raise RuntimeError("Cannot revert: this folder is not a git repository.")
    remote = _capture(["git", "remote", "get-url", "origin"])
    if remote.returncode != 0:
        raise RuntimeError("Cannot revert upstream: no origin remote is configured.")
    _run(["git", "diff", "--quiet"])
    _run(["git", "diff", "--cached", "--quiet"])
    _run(["git", "revert", "--no-edit", "HEAD"])
    _run(["git", "push"])


def prompt_for_repo_details():
    default_repo = os.path.basename(HERE).replace(" ", "-")
    params = read_project_params()
    default_location = params.get("github_location")
    if default_location:
        owner, repo = default_location.split("/", 1)
    else:
        owner = _prompt_text("GitHub Owner", "GitHub user or organization:")
        repo = _prompt_text("GitHub Repository", "Repository name:", default_repo)
    location = validate_github_location(f"{owner}/{repo}")
    params["github_enabled"] = True
    params["github_location"] = location
    write_project_params(params)
    return owner, repo


def init_private_github_repo(owner, repo):
    """Create a private GitHub repo, commit all local files, and push to origin."""
    if not os.path.isdir(os.path.join(HERE, ".git")):
        _run(["git", "init"])

    _run(["git", "add", "-A"])
    staged = _capture(["git", "diff", "--cached", "--quiet"])
    if staged.returncode != 0:
        _run(["git", "commit", "-m", "Initial project commit"])

    branch = _capture(["git", "branch", "--show-current"]).stdout.strip()
    if not branch:
        branch = "main"
        _run(["git", "branch", "-M", branch])

    _run(["gh", "repo", "create", f"{owner}/{repo}", "--private"])

    remote = _capture(["git", "remote", "get-url", "origin"])
    if remote.returncode == 0:
        _run(["git", "remote", "remove", "origin"])
    _run(["git", "remote", "add", "origin", f"https://github.com/{owner}/{repo}.git"])
    _run(["git", "push", "-u", "origin", branch])


def install_versioning_from_params(params):
    """Install versioning tools from validated params without prompting."""
    ensure_git_installed()
    ensure_gh_installed()
    if params["autocommit"]:
        ensure_autocommit_installed()


def init_private_github_repo_from_params(params):
    """Create and push the configured GitHub repo without prompting."""
    owner, repo = params["github_location"].split("/", 1)
    return init_private_github_repo(owner, repo)


def init_versioning(mode):
    """Install requested tools and return whether remote repo setup is needed."""
    params = read_project_params()
    if mode == "nothing":
        params["github_enabled"] = False
        params["autocommit"] = False
        params["autocommit_params"] = None
        write_project_params(params)
        load_project_params_env()
        print("No version management selected.")
        return False

    params["github_enabled"] = True
    params["autocommit"] = mode == "autocommit"
    if not params["autocommit"]:
        params["autocommit_params"] = None
    write_project_params(params)
    load_project_params_env()

    ensure_git_installed()
    ensure_gh_installed()

    if mode == "autocommit":
        ensure_autocommit_installed()
        configure_autocommit_environment()
    elif mode != "git":
        raise RuntimeError(f"Unknown versioning mode: {mode}")

    return True
