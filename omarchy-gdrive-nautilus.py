"""Files integration for omarchy-gdrive.

- Background menu: "Add Google Drive Account…" runs the setup in a terminal.
- Item menu on an account folder (~/GoogleDrive/<email>) or a Google Shared
  drive folder: "Sync Google Drive Now", "Pause"/"Resume Google Drive Sync",
  "Keep Everything on This Device", "Make All Folders Online-Only", and
  "Confirm Deletions and Sync" when a bulk delete paused the sync.
- Item menu on folders directly inside one of those: "Keep on This Device" for
  online-only folders, "Free Up Space (Online Only)" for local ones. Freeing up
  space opens a terminal that shows the real paths and asks before deleting.
- Emblems on everything inside a synced folder: a green check for files kept
  on this device and in sync, a blue cloud for online-only, blue arrows while
  syncing, a red "!" on a drive that has a sync error or is paused for
  safety, and a grey pause badge on a drive whose sync is paused. List view gets a "Google Drive" column with the same state as text.

Installed as /usr/share/nautilus-python/extensions/omarchy-gdrive.py.
"""

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from gi import require_version

require_version("Nautilus", "4.1")

from gi.repository import Gio, GLib, GObject, Nautilus  # noqa: E402

SETUP = "omarchy-gdrive-setup"
MOUNT = "omarchy-gdrive-mount"
LAUNCHER = "omarchy-launch-terminal"


def config_home():
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))


UNIT_PATH = re.compile(
    r'^ExecStart=.*(?:omarchy-gdrive-sync"| mount) "[^"]*" "([^"]*)"', re.MULTILINE
)


def state_home():
    return Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state"))


def mount_units():
    """Map every omarchy-gdrive folder to the systemd unit that owns it."""
    units = {}
    unit_dir = config_home() / "systemd" / "user"
    try:
        unit_files = sorted(unit_dir.glob("rclone-*.service"))
    except OSError:
        return units
    for unit_file in unit_files:
        try:
            text = unit_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = UNIT_PATH.search(text)
        if match:
            units[match.group(1)] = unit_file.stem
    return units


def path_of(file_info):
    """Path as shown in Files. Symlinks are not resolved: an online-only folder
    is a symlink into the on-demand mount and must keep its own path."""
    try:
        location = file_info.get_location()
    except Exception:
        return None
    if location is None:
        return None
    path = location.get_path()
    return os.path.normpath(path) if path else None


def root_unit(units, path):
    """Unit for a sync root, matching the path as given or fully resolved."""
    if path in units:
        return path, units[path]
    real = os.path.realpath(path)
    if real in units:
        return real, units[real]
    return None, None


def children(root):
    try:
        with os.scandir(root) as entries:
            return [e for e in entries if e.is_dir() and not e.name.startswith(".Trash-")]
    except OSError:
        return []


def is_active(unit):
    try:
        return (
            subprocess.run(
                ["systemctl", "--user", "is-active", "--quiet", unit], timeout=2
            ).returncode
            == 0
        )
    except (OSError, subprocess.SubprocessError):
        return False


def state_dir(path):
    """omarchy-gdrive-sync state directory for a synced root."""
    root = state_home() / "omarchy-gdrive" / "sync"
    try:
        dirs = list(root.iterdir())
    except OSError:
        return None
    for directory in dirs:
        try:
            lines = (directory / "target").read_text().splitlines()
        except OSError:
            continue
        if len(lines) >= 2 and lines[1] == path:
            return directory
    return None


def sync_status(path):
    """(state, message) written by omarchy-gdrive-sync for this folder."""
    directory = state_dir(path)
    if directory is None:
        return ("", "")
    try:
        fields = (directory / "status").read_text().rstrip("\n").split("\t")
    except OSError:
        return ("", "")
    return (fields[0], fields[2] if len(fields) > 2 else "")


def drive_mode(path):
    """all, selected, or online (the whole drive is online-only)."""
    directory = state_dir(path)
    try:
        return (directory / "selection").read_text().split("\n", 1)[0] or "all"
    except (OSError, TypeError):
        return "all"


# --- sync state emblems -------------------------------------------------------

EMBLEM = {
    "synced": "omarchy-gdrive-synced",
    "online": "omarchy-gdrive-online",
    "syncing": "omarchy-gdrive-syncing",
    "error": "omarchy-gdrive-error",
    "paused": "omarchy-gdrive-paused",
}
LABEL = {
    "synced": "On this device",
    "online": "Online-only",
    "syncing": "Syncing…",
    "error": "Sync error",
    "paused": "Paused",
    "": "",
}
CACHE_SECONDS = 2.0


class DriveState:
    """Roots, modes and statuses, re-read at most every CACHE_SECONDS so that
    update_file_info stays cheap for folders with thousands of files."""

    def __init__(self):
        self.read_at = 0.0
        self.roots = []  # (root, mode, state), longest root first

    def refresh(self, force=False):
        now = time.monotonic()
        if not force and now - self.read_at < CACHE_SECONDS:
            return
        self.read_at = now
        roots = []
        for root in mount_units():
            directory = state_dir(root)
            mode, state = "all", ""
            if directory is not None:
                try:
                    mode = (directory / "selection").read_text().split("\n", 1)[0] or "all"
                except OSError:
                    pass
                try:
                    state = (directory / "status").read_text().split("\t", 1)[0]
                except OSError:
                    pass
            roots.append((root, mode, state))
        roots.sort(key=lambda item: len(item[0]), reverse=True)
        self.roots = roots

    def root_for(self, path):
        for root, mode, state in self.roots:
            if path == root or path.startswith(root + "/"):
                return root, mode, state
        return None, None, None

    def status(self, path):
        """synced, online, syncing, error, paused, or "" (not ours / unknown)."""
        self.refresh()
        root, mode, state = self.root_for(path)
        if root is None:
            return ""
        if state == "stopped":
            return "paused"
        if mode == "online":
            return "online"
        if path != root:
            top = os.path.join(root, path[len(root) + 1:].split("/", 1)[0])
            if os.path.islink(top):
                return "online"
        if state == "error":
            # Only the drive itself carries the error; its files may or may
            # not be up to date, so they get no check mark.
            return "error" if path == root else ""
        if state == "syncing":
            return "syncing"
        if state == "ok":
            return "synced"
        return ""

    def snapshot(self):
        self.refresh(force=True)
        return {root: (mode, state) for root, mode, state in self.roots}


STATE = DriveState()


class OmarchyGDriveEmblems(GObject.GObject, Nautilus.InfoProvider, Nautilus.ColumnProvider):
    def __init__(self):
        super().__init__()
        # Files whose emblem follows the drive's live state (roots and their
        # top-level entries); refreshed when a drive's status changes.
        self.live = {}
        self.last = STATE.snapshot()
        GLib.timeout_add_seconds(3, self._poll)

    def get_columns(self):
        return [
            Nautilus.Column(
                name="OmarchyGDrive::status",
                attribute="omarchy_gdrive_status",
                label="Google Drive",
                description="Whether the item is on this device, online-only, or syncing",
            )
        ]

    def update_file_info(self, file_info):
        path = path_of(file_info)
        if path is None:
            return
        status = STATE.status(path)
        file_info.add_string_attribute("omarchy_gdrive_status", LABEL.get(status, ""))
        root, _mode, _state = STATE.root_for(path)
        # A paused drive shows the badge on the drive folder only; its files
        # say "Paused" in the Google Drive column.
        if status in EMBLEM and not (status == "paused" and path != root):
            file_info.add_emblem(EMBLEM[status])
        if status:
            if root is not None and (path == root or os.path.dirname(path) == root):
                self.live[path] = file_info

    def _poll(self):
        current = STATE.snapshot()
        changed = {root for root in current if current.get(root) != self.last.get(root)}
        self.last = current
        if changed:
            for path, file_info in list(self.live.items()):
                if any(path == root or path.startswith(root + "/") for root in changed):
                    try:
                        file_info.invalidate_extension_info()
                    except Exception:
                        self.live.pop(path, None)
        # Forget entries for roots that no longer exist.
        if len(self.live) > 2000:
            self.live.clear()
        return True


class OmarchyGDriveMenu(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, *args):
        files = args[-1] if args else []
        if not files:
            return []
        try:
            paths = [path_of(f) for f in files]
        except TypeError:
            return []
        if not paths or any(p is None for p in paths) or shutil.which(MOUNT) is None:
            return []
        units = mount_units()

        if len(paths) == 1:
            root, unit = root_unit(units, paths[0])
            if unit is not None:
                return self._root_items(root, unit)
        return self._folder_items(units, paths)

    def _folder_items(self, units, paths):
        """Pin/unpin for folders directly inside one synced root."""
        roots = set()
        online, local = [], []
        for path in paths:
            root, unit = root_unit(units, os.path.dirname(path))
            if unit is None:
                return []
            roots.add((root, unit))
            if drive_mode(root) == "online" and os.path.isdir(path):
                online.append(os.path.join(root, os.path.basename(path)))
            elif os.path.islink(path) and os.path.isdir(path):
                online.append(os.path.join(root, os.path.basename(path)))
            elif os.path.isdir(path):
                local.append(os.path.join(root, os.path.basename(path)))
            else:
                return []
        if len(roots) != 1 or not is_active(next(iter(roots))[1]):
            return []
        items = []
        if online:
            items.append(self._item("pin", "Keep on This Device",
                                    "folder-download", online, "--pin"))
        if local and shutil.which(LAUNCHER):
            items.append(self._terminal_item("unpin", "Free Up Space (Online Only)",
                                             "edit-clear", local, "--unpin"))
        return items

    def _root_items(self, path, unit):
        items = []
        active = is_active(unit)
        state, message = sync_status(path)
        if active:
            items.append(self._item("sync_now", "Sync Google Drive Now",
                                    "view-refresh", [path], "--sync-now"))
        if state == "error" and "deletion" in message:
            items.append(self._item("force_sync", "Confirm Deletions and Sync",
                                    "edit-delete", [path], "--force-sync"))
        if active:
            entries = children(path)
            whole_drive_online = drive_mode(path) == "online"
            if whole_drive_online or any(e.is_symlink() for e in entries):
                items.append(self._item("pin_all", "Keep Everything on This Device",
                                        "folder-download", [path], "--pin-all"))
            if (not whole_drive_online and any(not e.is_symlink() for e in entries)
                    and shutil.which(LAUNCHER)):
                items.append(self._terminal_item("unpin_all", "Make All Folders Online-Only",
                                                 "edit-clear", [path], "--unpin-all"))
            items.append(self._item("pause", "Pause Google Drive Sync",
                                    "media-playback-pause", [path], "--pause"))
        else:
            items.append(self._item("resume", "Resume Google Drive Sync",
                                    "media-playback-start", [path], "--resume"))
        return items

    def _item(self, name, label, icon, paths, flag):
        item = Nautilus.MenuItem(name="OmarchyGDrive::" + name, label=label, icon=icon)
        item.connect("activate", self._run_helper, paths, flag)
        return item

    def _run_helper(self, _item, paths, flag):
        helper = shutil.which(MOUNT)
        if helper is None:
            return
        # Gio.Subprocess.new does not wait, so Nautilus stays responsive.
        Gio.Subprocess.new([helper, flag] + list(paths), Gio.SubprocessFlags.NONE)

    def _terminal_item(self, name, label, icon, paths, flag):
        item = Nautilus.MenuItem(name="OmarchyGDrive::" + name, label=label, icon=icon)
        item.connect("activate", self._run_in_terminal, paths, flag)
        return item

    def _run_in_terminal(self, _item, paths, flag):
        """Deleting local copies is confirmed in a terminal that shows the real
        paths, sizes, and filesystems first."""
        helper = shutil.which(MOUNT)
        if helper is None:
            return
        Gio.Subprocess.new(
            [
                LAUNCHER,
                "bash",
                "-c",
                '"$0" "$@"; printf "\\nPress Enter to close…"; read -r',
                helper,
                flag,
            ]
            + list(paths),
            Gio.SubprocessFlags.NONE,
        )

    def _background_add_account(self):
        return not shutil.which(SETUP) or not shutil.which(LAUNCHER)

    def get_background_items(self, *args):
        if self._background_add_account():
            return []
        item = Nautilus.MenuItem(
            name="OmarchyGDrive::add_account",
            label="Add Google Drive Account…",
            icon="folder-remote",
        )
        item.connect("activate", self._on_activate)
        return [item]

    def _on_activate(self, _item):
        Gio.Subprocess.new(
            [
                "omarchy-launch-terminal",
                "bash",
                "-lc",
                SETUP
                + " --add-account || { printf '\\nPress Enter to close…'; read -r; }",
            ],
            Gio.SubprocessFlags.NONE,
        )
