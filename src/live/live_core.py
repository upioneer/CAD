#!/usr/bin/env python3
"""
Shared reload engine for the per-project live scripts in this folder.

Do NOT run this file directly. Run the launcher matching your project
(see readme.md in this folder for the registry). Launcher filenames mirror
their target: live_<src-dir-path>.py with separators as underscores.

Each launcher is a small self-contained file carrying its own target path,
so adding a project never touches this engine: copy a launcher, rename it
per the rule above, change its LABEL and candidate paths, done.
"""

import os
import sys
import time

try:
    import FreeCAD
    import FreeCADGui
except ImportError:
    print("Live scripts must be run inside the FreeCAD GUI environment.")
    sys.exit(0)

# Detect PySide version (FreeCAD 1.0+ uses PySide6 or PySide2)
try:
    from PySide6 import QtCore
except ImportError:
    try:
        from PySide2 import QtCore
    except ImportError:
        from PySide import QtCore


class ProjectLiveReloader(QtCore.QObject):
    """
    Robust dual-engine reloader for FreeCAD.
    Combines QFileSystemWatcher with a precision QTimer timestamp polling loop.
    This guarantees zero dropped reload events on Windows even when editors use
    atomic temporary file rename patterns.
    """

    def __init__(self, label, script_path, parent=None):
        super().__init__(parent)
        self.label = label
        self.script_path = os.path.abspath(script_path)
        self.script_dir = os.path.dirname(self.script_path)
        self.last_mtime = self._get_mtime()
        self.last_reload = 0.0
        self.is_reloading = False

        # 1. Qt File System Watcher on both the script and the parent directory
        # (Watching the parent directory captures atomic rename events on Windows)
        self.watcher = QtCore.QFileSystemWatcher(self)
        if os.path.isfile(self.script_path):
            self.watcher.addPath(self.script_path)
        if os.path.isdir(self.script_dir):
            self.watcher.addPath(self.script_dir)

        self.watcher.fileChanged.connect(self._on_notify)
        self.watcher.directoryChanged.connect(self._on_notify)

        # 2. Polling QTimer (runs every 400ms as an immutable fallback)
        self.poll_timer = QtCore.QTimer(self)
        self.poll_timer.setInterval(400)
        self.poll_timer.timeout.connect(self._check_mtime_poll)
        self.poll_timer.start()

        print("==================================================================")
        print(f"Live Watcher ACTIVE: {self.label}")
        print(f"Monitoring Target : {self.script_path}")
        print("Dual Engine       : QFileSystemWatcher + 400ms Polling Timer")
        print("Trigger           : Viewport updates automatically upon file save")
        print(f"Manual Trigger    : FreeCAD._live_watchers['{self.label}'].reload_now()")
        print("==================================================================")

        # Execute initial build
        self.reload_now()

    def _get_mtime(self):
        try:
            return os.path.getmtime(self.script_path)
        except Exception:
            return 0.0

    def _on_notify(self, path=None):
        # Re-attach file path if atomic write momentarily unhooked it
        if os.path.isfile(self.script_path) and self.script_path not in self.watcher.files():
            try:
                self.watcher.addPath(self.script_path)
            except Exception:
                pass
        self._trigger_debounce()

    def _check_mtime_poll(self):
        current_mtime = self._get_mtime()
        if current_mtime > 0 and current_mtime != self.last_mtime:
            self.last_mtime = current_mtime
            self._trigger_debounce()

    def _trigger_debounce(self):
        now = time.time()
        if (now - self.last_reload) < 0.35:
            return
        if self.is_reloading:
            return
        self.last_reload = now
        QtCore.QTimer.singleShot(150, self.reload_now)

    def reload_now(self):
        if self.is_reloading:
            return
        self.is_reloading = True

        try:
            if not os.path.exists(self.script_path):
                print(f"[{self.label} Error] Target script not found on disk: {self.script_path}")
                return

            # Read script content with brief retry for lock release
            code_content = None
            for _ in range(5):
                try:
                    with open(self.script_path, "r", encoding="utf-8") as f:
                        code_content = f.read()
                    break
                except IOError:
                    time.sleep(0.05)

            if code_content is None:
                print(f"[{self.label} Error] Could not open {self.script_path} (file locked).")
                return

            print(f"\n[{self.label} {time.strftime('%H:%M:%S')}] File modified. Rebuilding model...")

            # Execute target script in current FreeCAD context.
            # __file__ points at the TARGET so project-relative assets
            # (vector JSON, exports/) resolve exactly as before.
            # FREECAD_LIVE_ITERATION tells the target this is a live
            # iteration, so it can skip slow production IO (STEP/STL/FCStd
            # writes). Removed right after, so manual macro runs and
            # freecadcmd runs still export normally.
            execution_globals = {
                "__file__": self.script_path,
                "__name__": "__main__",
                "FreeCAD": FreeCAD,
                "FreeCADGui": FreeCADGui,
            }
            os.environ["FREECAD_LIVE_ITERATION"] = "1"
            try:
                exec(code_content, execution_globals)
            finally:
                os.environ.pop("FREECAD_LIVE_ITERATION", None)

            # Refresh FreeCAD 3D Viewport
            try:
                active_gui_doc = FreeCADGui.activeDocument()
                if active_gui_doc:
                    active_view = active_gui_doc.activeView()
                    if active_view:
                        active_view.redraw()
            except Exception:
                pass

            print(f"[{self.label} {time.strftime('%H:%M:%S')}] 3D Viewport refreshed successfully.")

        except Exception as err:
            print(f"[{self.label} Build Error] {err}")
        finally:
            self.is_reloading = False
            self.last_mtime = self._get_mtime()

    def stop(self):
        """Cleanly halts all timers and watcher connections."""
        try:
            self.poll_timer.stop()
            self.watcher.fileChanged.disconnect()
            self.watcher.directoryChanged.disconnect()
        except Exception:
            pass


def _stop_watcher(instance):
    try:
        instance.stop()
    except Exception:
        pass


def watch(label, candidates):
    """
    Starts (or restarts) live watching for one project.

    Only this label's previous watcher is replaced; other projects already
    live in this session keep running. Returns the reloader, or None when
    no candidate target script exists on disk.
    """
    script = next((c for c in candidates if c and os.path.isfile(c)), None)
    if script is None:
        print(f"[LiveWatcher Error] No target script found for '{label}'. Tried:")
        for c in candidates:
            print(f"  - {c}")
        return None

    watchers = getattr(FreeCAD, "_live_watchers", None)
    if not isinstance(watchers, dict):
        watchers = {}
        FreeCAD._live_watchers = watchers

    old = watchers.get(label)
    if old is not None:
        print(f"[LiveWatcher] Restarting '{label}' watcher...")
        _stop_watcher(old)

    # Stop one-shot legacy singletons from the old per-folder watchers so a
    # stale copy never double-reloads alongside this session.
    for legacy_attr in ("_maker_station_live_watcher", "_gta_lightbox_watcher"):
        legacy = getattr(FreeCAD, legacy_attr, None)
        if legacy is not None:
            print(f"[LiveWatcher] Stopping legacy watcher instance ({legacy_attr})...")
            _stop_watcher(legacy)
            setattr(FreeCAD, legacy_attr, None)

    watchers[label] = ProjectLiveReloader(label, script)
    return watchers[label]
