# Google Drive for Omarchy Files

## Quick install (Omarchy)

1. Open a terminal: press **Super + Enter**.
2. Copy this whole block, paste it into the terminal (**Ctrl + Shift + V**),
   and press **Enter**. Type your password if asked.

   ```bash
   grep -q '^\[omarchy-pkgs\]' /etc/pacman.conf || sudo tee -a /etc/pacman.conf >/dev/null <<'EOF'

   [omarchy-pkgs]
   SigLevel = Optional TrustAll
   Server = https://skystone-studio.github.io/omarchy-pkgs/x86_64
   EOF
   sudo pacman -Syu --noconfirm omarchy-gdrive
   nautilus --quit
   ```

3. Connect your Google account: type `omarchy-gdrive-setup` and press **Enter**.
   A browser window opens so you can sign in to Google.
4. Open **Files**. Your Google Drive is in the sidebar.

To update later, run `sudo pacman -Syu`.

Keeps every Google Drive account's My Drive synced to an ordinary local folder,
and shows every Shared drive online-only until you choose to keep it on this
device, the way Google Drive for desktop ("Mirror files") and
OneDrive ("Always keep on this device") work on other systems. Files open
instantly because they are already on disk. Saves upload to Google Drive
automatically, and Google Drive remains the source of truth. Sync runs on
[rclone bisync](https://rclone.org/bisync/), one systemd user service per
folder, started at login.

## Features

- My Drive syncs to `~/GoogleDrive/<email>` and every Google Shared drive
  appears at `~/GoogleDrive/Shared drives/<email>/<drive>`, each with its own
  systemd user service.
- **Shared drives start online-only**: they are browsable and editable at once,
  and nothing is downloaded until you right-click the drive in Files and choose
  **Keep Everything on This Device**, or **Keep on This Device** on a folder in
  it (`GDRIVE_SHARED_DEFAULT=sync` downloads them all instead).
- **Stored locally**: every file is on disk, so opening, previewing, and
  searching never wait for a download, and files stay available offline.
- **Auto-save to Google Drive**: a file watcher (`inotifywait`) uploads a save a
  few seconds after it is written; a burst of writes is batched, and nothing
  waits more than 30 seconds.
- **Google Drive is the source of truth**: Drive is checked for changes every
  60 seconds (`GDRIVE_SYNC_INTERVAL`). If a file changed both locally and in
  Drive, the Drive version wins and the local edit is kept beside it as
  `<name>.conflict1.<ext>` (also uploaded), with a desktop notification.
- **Google Docs, Sheets, and Slides** appear as `<name>.link.html`. Opening one
  opens the document in the browser, as `.gdoc` files do in Google Drive for
  desktop.
- Deletions sync both ways. Files deleted locally go to the Google Drive trash,
  so they can be restored from drive.google.com.
- Safety stops: if more than half of a folder's files would be deleted at once
  (for example, the folder was wiped), sync pauses and notifies you instead of
  emptying Drive. Folders with 10 files or fewer are exempt.
- **Choose what is kept on this device**: right-click a folder inside an
  account or shared drive and choose **Free Up Space (Online Only)** or **Keep
  on This Device**. Online-only folders stay in place and open on demand. See
  [Choose what is kept on this device](#choose-what-is-kept-on-this-device).
- One **Google Drive** sidebar entry; accounts and shared drives are folders
  inside it.
- Right-click an account or shared-drive folder in Files for **Sync Google Drive
  Now**, **Pause/Resume Google Drive Sync**, and, after a safety stop,
  **Confirm Deletions and Sync**.
- **Add Google Drive Account…** in the Files background right-click menu
  authorizes one more account and creates its folder, service, and sidebar
  entry.
- Editor lock and temporary files (`.~lock.*#`, `~$*`, `.goutputstream-*`,
  `*.part`, `*.swp`, …) never reach Drive.
- Setup handles OAuth, the folder, the service, and the bookmark. It is safe to
  re-run, and it migrates the FUSE mounts from 0.4 and earlier in place.

Only **My Drive** and Shared drives are synced by default. "Shared with me" is
opt-in (`GDRIVE_SHARED_WITH_ME=1`).

## Requirements

- Omarchy (Arch Linux) with Nautilus and a systemd user session
- `rclone`, `inotify-tools`, `libnotify`, `python`, `nautilus`, and
  `nautilus-python` (installed as package dependencies; `fuse3` is kept only to
  clear old mounts)
- Enough disk space for a full copy of your Drive and Shared drives
- A Google account

## Install

Add the public `omarchy-pkgs` pacman repository, then install:

```bash
sudo tee -a /etc/pacman.conf >/dev/null <<'EOF'

[omarchy-pkgs]
SigLevel = Optional TrustAll
Server = https://skystone-studio.github.io/omarchy-pkgs/x86_64
EOF
sudo pacman -Syu omarchy-gdrive
```

The database is unsigned (`Optional TrustAll`); the site is HTTPS-only. If you
would rather not add a repository, build from source:

```bash
git clone https://github.com/SSS-Marcelo/omarchy-gdrive.git
cd omarchy-gdrive
makepkg -si
```

Files loads extensions at startup, so reopen it once after installing:

```bash
nautilus --quit
```

## First run

```bash
omarchy-gdrive-setup
```

You can also launch **Google Drive Setup** from the Omarchy launcher, or
right-click an empty area in Files and choose **Add Google Drive Account…** -
the same command adds the first account.

The run opens the default browser for Google authorization. After approval it
creates:

- `~/GoogleDrive/<email>` - the synced copy of My Drive
- `~/.config/systemd/user/rclone-<remote>.service` - the sync service for that
  account
- `~/.local/state/omarchy-gdrive/sync/<id>/` - sync state for each folder
  (bisync listings, status, last run log)
- a **Google Drive** bookmark for `~/GoogleDrive` in
  `~/.config/gtk-3.0/bookmarks`
- `~/.config/omarchy-gdrive/accounts.tsv` - the `email <TAB> remote` mapping
- `~/.local/state/omarchy-gdrive/setup.log` - setup diagnostics

The first sync downloads everything in the background. Large drives take a
while; follow progress with `journalctl --user -f -u 'rclone-*'`. Files may
need to be reopened once after the first sync starts:

```bash
nautilus --quit
```

Then open **Files** again.

## Shared drives

Google Shared drives (formerly Team drives) are separate Drive roots, so each
one gets its own folder beside the account's My Drive folder. A newly added
Shared drive starts **online-only**: the folder is a link to an on-demand
mount, files download when opened, and saves upload about 5 seconds after
the file is closed. To sync it, right-click the drive folder in Files and
choose **Keep Everything on This Device**, or right-click one of its folders
and choose **Keep on This Device** to download only that folder.

```text
~/GoogleDrive/marcelo@example.com                     My Drive
~/GoogleDrive/Shared drives/marcelo@example.com/Clients
~/GoogleDrive/Shared drives/marcelo@example.com/Corporate
```

`omarchy-gdrive-setup` lists the drives with `rclone backend drives` on every
run and writes one `rclone-<remote>-shared-<drive>.service` per drive. When a
drive disappears from the account its service is removed and syncing stops;
the local copy is left on disk for you to delete.

| Variable | Default | Effect |
|---|---|---|
| `GDRIVE_SHARED_DRIVES` | `on` | `off` removes every shared drive |
| `GDRIVE_SHARED_DEFAULT` | `online` | How a **newly added** Shared drive starts: `online` (nothing downloaded) or `sync` (download everything). Drives that already synced keep their setting |
| `GDRIVE_SHARED_WITH_ME` | `off` | `1` adds `~/GoogleDrive/Shared with me/<email>` using `--drive-shared-with-me` (mostly read-only: uploads into files you don't own fail) |

Each synced folder lists its Drive root once per check (every 60 s by default).
With rclone's shared OAuth client a check can take 15-30 s and many folders
can hit its quota; a user OAuth client makes it fast.

## Sync settings

Set these when running `omarchy-gdrive-setup`. They are written into every
service unit, so re-run setup to change them:

| Variable | Default | Effect |
|---|---|---|
| `GDRIVE_SYNC_INTERVAL` | `60` | Seconds between Google Drive checks (minimum 15) |
| `GDRIVE_GDOCS` | `link` | Google Docs as `link` (`.link.html`, opens in the browser), `office` (`.docx`/`.xlsx`/`.pptx` exports), or `skip` |

```bash
GDRIVE_SYNC_INTERVAL=120 omarchy-gdrive-setup
```

With `GDRIVE_GDOCS=office`, saving an exported `.docx` locally converts it
back into the Google Doc. That conversion is lossy, which is why `link` is the
default. Edit Google Docs in the browser, and rename or move them on
drive.google.com: a local rename is synced as delete + create.

## Sync status in Files

Everything inside a Google Drive folder carries a badge:

| Badge | Meaning |
|---|---|
| Green check | Stored on this device and in sync with Google Drive |
| Blue cloud | Online-only: opens on demand, takes no space |
| Amber arrows | Syncing now (on the drive folder and its top-level items) |
| Red "!" | The drive has a sync error, or a safety stop is waiting for **Confirm Deletions and Sync** |
| Grey pause | Sync is paused for this drive (**Resume Google Drive Sync**) |

Badges update within a few seconds of a change. In list view, right-click the
column header and enable **Google Drive** for the same state as text ("On this
device", "Online-only", "Syncing…", "Sync error", "Paused"). Online-only
folders also show Files' own link arrow, because they are links into the
on-demand mount.

## Choose what is kept on this device

By default everything in My Drive is kept on this device, and Shared drives
are entirely online-only. Any **top-level folder** of My Drive or of a Shared
drive can be switched either way. For example, a client
folder directly inside the `Clients` shared drive can be online-only, but a
folder nested deeper cannot.

Right-click one or more of those folders in Files:

- **Free Up Space (Online Only)** opens a terminal that lists every local copy
  that would be deleted, with its **real path** (fully resolved), filesystem,
  size, and file count, and asks before doing anything. The sync service then
  compares every file with Google Drive (`rclone check`). It deletes the local
  copy only when everything matches; otherwise it keeps the folder and notifies
  you. Before deleting, it resolves the path again and refuses anything that is
  not a plain folder directly inside the synced folder on the same local disk
  (a symlink, a FUSE mount, or another filesystem).
- **Keep on This Device** downloads an online-only folder and syncs it again.

On the account or shared-drive folder itself:

- **Make All Folders Online-Only** does the same for every top-level folder
  (files directly in the root stay local).
- **Keep Everything on This Device** downloads everything, including a Shared
  drive that is still online-only.

An online-only folder is a symlink into an on-demand rclone mount of the same
Drive (under `~/.local/state/omarchy-gdrive/sync/<id>/online`), so it appears in
the same place in Files. Files inside it download when opened (cached for 72 h,
up to 5 GiB per drive, `GDRIVE_ONLINE_CACHE`), and saves upload about 5 seconds
after the file is closed. Online-only folders need a connection.

Rules:

- Every real folder at the top level is kept on this device, including folders
  you create locally. New folders created in Google Drive become online-only
  once any folder in that drive is online-only.
- Renaming a kept folder in Google Drive syncs as a deletion; the new name
  appears online-only. Pin it again.
- Deleting an online-only folder's symlink only removes the placeholder, which
  comes back on the next check. Delete the folder on drive.google.com or from
  inside it.

Command line:

```bash
omarchy-gdrive-mount --unpin     ~/GoogleDrive/<email>/<folder>...   # asks first; --yes skips the prompt
omarchy-gdrive-mount --pin       ~/GoogleDrive/<email>/<folder>...
omarchy-gdrive-mount --unpin-all ~/GoogleDrive/<email>
omarchy-gdrive-mount --pin-all   ~/GoogleDrive/<email>
omarchy-gdrive-mount --status    ~/GoogleDrive/<email>               # lists online-only folders
```

## Sync now, pause, and resume

Right-click an account or shared-drive folder inside **Google Drive** in Files:

- **Sync Google Drive Now**: check Drive and upload immediately.
- **Pause Google Drive Sync** / **Resume Google Drive Sync**: stop or restart
  the service. Files stay on disk while paused; changes made meanwhile sync
  on resume.
- **Confirm Deletions and Sync**: shown after a safety stop; applies the bulk
  delete.

The same helper is available on the command line:

```bash
omarchy-gdrive-mount --status     ~/GoogleDrive/<email>
omarchy-gdrive-mount --sync-now   ~/GoogleDrive/<email>
omarchy-gdrive-mount --pause      ~/GoogleDrive/<email>
omarchy-gdrive-mount --resume     ~/GoogleDrive/<email>
omarchy-gdrive-mount --force-sync ~/GoogleDrive/<email>
```

`--disconnect` and `--connect` still work as aliases for `--pause` and
`--resume`. A pause disables the systemd unit, so it stays paused across
logins; a full `omarchy-gdrive-setup` run resumes it.

## Add an account

Right-click an empty area in Files and choose **Add Google Drive Account…**. A
terminal opens and runs:

```bash
omarchy-gdrive-setup --add-account
```

Authorize the additional Google account in the browser. Its email address
becomes the folder name and the sidebar label, so two accounts never collide.
Re-running it for an account that is already configured only refreshes its
token:

```
Account name@example.com is already configured; token updated.
```

New rclone remotes are named `gdrive-<slug>-<hash8>`, where the slug comes from
the email's local part and `hash8` is the first eight hex characters of
`sha256(email)`. The very first account keeps the plain `gdrive` remote name.

## Upgrade from 0.5

0.6.0 only changes how **new** Shared drives start. Shared drives that already
synced under 0.5 stay synced, even after `omarchy-gdrive-setup` adds the new
default to their services. To free them up, use **Make All Folders
Online-Only**.

## Upgrade from 0.4 or earlier (FUSE mounts)

0.5.0 replaces the on-demand rclone mounts with synced local folders at the
same paths. After upgrading the package, run:

```bash
omarchy-gdrive-setup
nautilus --quit
```

Each service is rewritten and restarted: the old mount is unmounted and the
first sync downloads every file into the now-local folder. Nothing is uploaded
or deleted in Drive during that first sync. If a file already exists on both
sides and differs, the Drive copy wins. The old VFS cache in
`~/.cache/rclone/vfs` is no longer used and can be deleted.

## Upgrade from 0.1.0

0.1.0 mounted a single account at `~/GoogleDrive` and labelled it
`Google Drive`. After upgrading, run:

```bash
omarchy-gdrive-setup
```

It stops the old service, unmounts `~/GoogleDrive`, creates the mount at
`~/GoogleDrive/<email>`, and rewrites the bookmark and the systemd unit. It
also adopts `gdrive` and `gdrive-*` remotes that are not yet recorded in
`accounts.tsv`.

If you previously used `GDRIVE_REMOTE`/`GDRIVE_MOUNT`/`GDRIVE_LABEL` for extra
accounts, those variables are gone. Drop them from your shell configuration and
run the default mode instead: every `gdrive-*` Drive remote is discovered and
mounted at `~/GoogleDrive/<email>`.

## Reauthorize

```bash
omarchy-gdrive-setup --reauth                     # only account, or the legacy gdrive remote
omarchy-gdrive-setup --reauth name@example.com
omarchy-gdrive-setup --reauth gdrive-name-1a2b3c4d
```

With several accounts configured, pass an email address or an rclone remote
name. The script refuses to bind a remote to a different Google account than
the one it already belongs to.

## Manage

```bash
rclone listremotes                                # configured remotes
systemctl --user status rclone-<remote>.service
journalctl --user -u rclone-<remote>.service -n 50 --no-pager
systemctl --user restart rclone-<remote>.service
omarchy-gdrive-mount --status ~/GoogleDrive/<email>
```

`~/GoogleDrive` itself is only a container for the per-account folders.
`GDRIVE_ROOT` overrides that container if you want the accounts elsewhere:

```bash
GDRIVE_ROOT="$HOME/Drive" omarchy-gdrive-setup
```

## OAuth client: recommended for reliable use

Without your own OAuth client, the script uses rclone's shared Google client.
That client is heavily rate-limited and rclone is retiring it during 2026.
Browsing can stall or fail with `RATE_LIMIT_EXCEEDED`.

Create your own Desktop OAuth client once:

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project and enable the
   [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com).
3. Configure the OAuth consent screen:
   - **Internal** for a Google Workspace account, or
   - **External** for a personal account. External apps in **Testing** issue
     refresh tokens that expire after 7 days; publish the app or use Internal
     for a long-lived token.
4. Go to **Credentials** -> **Create credentials** -> **OAuth client ID** ->
   **Desktop app**, then copy the client ID and client secret.
5. Add them to the first account's remote and re-authorize:

```bash
rclone config update gdrive client_id "<CLIENT_ID>" client_secret "<CLIENT_SECRET>"
omarchy-gdrive-setup --reauth
```

Later accounts reuse that client automatically: the setup script passes it to
`rclone authorize` and writes it into the new remote section, because refreshing
a token requires the client that issued it. Tokens are written to
`~/.config/rclone/rclone.conf` (mode `0600`) and are never printed by the setup
script.

## Troubleshooting

- **No "Add Google Drive Account…" item in Files**: `nautilus-python` must be
  installed and Files must be restarted (`nautilus --quit`). The item is hidden
  when `omarchy-gdrive-setup` is not on `PATH`.
- **No Sync Now / Pause entry when right-clicking a drive folder**: the items
  only appear on the account or shared-drive folder itself, single selection,
  and when `omarchy-gdrive-mount` is on `PATH`. Restart Files after upgrading.
- **A folder is empty right after setup**: the first sync is still running.
  `journalctl --user -f -u 'rclone-*'` shows progress.
- **A save did not reach Drive**: `omarchy-gdrive-mount --status <folder>`
  shows the last sync result; the full log of the last run is
  `~/.local/state/omarchy-gdrive/sync/<id>/last-run.log`.
- **"Sync paused for safety" notification**: more than half of the folder's
  files were deleted or changed at once. If that was intended, choose
  **Confirm Deletions and Sync**; if not, restore the files (or pause sync and
  check what happened) before confirming.
- **`<name>.conflict1.<ext>` files**: the file changed in Drive and locally
  between two syncs. The Drive version kept the name; the `.conflict` copy is
  your local edit. Merge and delete whichever you don't need.
- **"Duplicate object found" in the log**: Google Drive allows two files with
  the same name in one folder; only one can exist locally. Rename one in Drive
  or run `rclone dedupe <remote>:<folder>`.
- **`inotifywait` errors about watches**: very large trees can exhaust
  `fs.inotify.max_user_watches`; raise it with sysctl. Sync keeps working,
  checking for local changes on each Drive check instead.
- **`RATE_LIMIT_EXCEEDED`, 403, or long stalls**: switch to your own OAuth
  client as described above.
- **A shared drive is missing**: `systemctl --user status
  rclone-<remote>-shared-<drive>.service`. A drive you were removed from is
  dropped on the next `omarchy-gdrive-setup`; a newly granted drive appears on the
  next run.
- **Leftover FUSE mount from 0.4** (`Transport endpoint is not connected`):
  the sync service unmounts it before syncing. Manually:
  `fusermount3 -uz ~/GoogleDrive/<email>`, then rerun `omarchy-gdrive-setup`.
- **Token expired or revoked**: `omarchy-gdrive-setup --reauth <email>`.
- **The setup says an account email could not be resolved**: the token is
  unusable. Reauthorize that account with `--reauth`.
- **Offline or rate-limited**: failed checks back off (up to 10 x the interval)
  and retry on their own; local edits are uploaded once Drive is reachable.

## Security

- OAuth tokens remain only in `~/.config/rclone/rclone.conf`, which is mode
  `0600`. The setup script never prints them, and the log does not contain
  them.
- `~/.config/omarchy-gdrive/accounts.tsv` (mode `0600`, parent directory `0700`)
  contains email addresses and rclone remote names only.
- Revoke access at <https://myaccount.google.com/permissions>.
- Do not share `~/.config/rclone/rclone.conf`.

## Uninstall

```bash
for unit in ~/.config/systemd/user/rclone-*.service; do
  systemctl --user disable --now "$(basename "$unit")"
done
rm ~/.config/systemd/user/rclone-*.service
systemctl --user daemon-reload
sudo pacman -R omarchy-gdrive
```

The package does not own per-user data, so it leaves these behind:

- `~/GoogleDrive/<email>` folders (one per account) - these are full local
  copies
- `~/GoogleDrive/Shared drives/` and `~/GoogleDrive/Shared with me/` folders
- `~/.config/omarchy-gdrive/` (`accounts.tsv`, `setup.lock`)
- `~/.config/rclone/rclone.conf` (remove only the `gdrive*` sections if you use
  other rclone remotes)
- the **Google Drive** line in `~/.config/gtk-3.0/bookmarks`
- `~/.local/state/omarchy-gdrive/` (setup log and sync state)

Delete them by hand after stopping the services. Deleting the local folders
while a service runs would be synced to Drive as deletions (or stopped by the
safety check), so stop the services first.

## How it works

The package installs a setup script, the sync daemon, a Nautilus extension, a
launcher entry, and documentation. For every account and shared drive the
setup writes a systemd user unit that runs:

```bash
omarchy-gdrive-sync gdrive-<slug>-<hash>: ~/GoogleDrive/<email> [--drive-team-drive <id>]
```

`omarchy-gdrive-sync` loops `rclone bisync <drive> <local folder>` with Drive as
Path1:

- First run: `--resync-mode path1`, which copies everything down, uploads
  local-only files, and never deletes.
- After that, each run applies changes both ways with
  `--conflict-resolve path1 --conflict-loser num` (Drive wins, the local loser
  is renamed `.conflict<N>`), plus `--resilient --recover --max-lock 2m`, so an
  interrupted run recovers without manual work. Unusable listings trigger a
  non-destructive `--resync-mode newer`.
- Runs start when `inotifywait` reports a local change (after 3 quiet seconds,
  at most 30), every `GDRIVE_SYNC_INTERVAL` seconds, or on `SIGUSR1`
  (**Sync Now**).
- `SIGTERM` is passed to rclone as `SIGINT` (bisync graceful shutdown), so
  logging out or pausing never leaves broken listings.
- A Shared drive with no sync history starts in `online` mode
  (`GDRIVE_INITIAL_MODE=online` in its unit): the drive folder is a symlink to
  the on-demand mount and no bisync runs. Keeping a folder, or everything, on
  this device turns it back into a real folder and runs the first sync.
- When a drive has online-only folders, the folders kept locally are written
  into the bisync filter (`+ /<folder>/**`, `+ /*`, `- **`). Any change to that
  set triggers a `--resync-mode newer`, which downloads newly kept folders and
  never deletes. The same service runs `rclone mount` for the online-only
  folders and keeps their symlinks in step with Drive.
- Status is written to `~/.local/state/omarchy-gdrive/sync/<id>/status`.
  Conflicts and stops send desktop notifications with `notify-send`.

The Files sidebar entry is a GTK bookmark pointing at `~/GoogleDrive`.

## Development

```bash
bash -n omarchy-gdrive-setup
bash -n omarchy-gdrive-sync
bash -n omarchy-gdrive-mount
python3 -c 'compile(open("omarchy-gdrive-nautilus.py").read(), "x", "exec")'
updpkgsums
makepkg --printsrcinfo > .SRCINFO
makepkg -f
```

The `PKGBUILD` downloads the tagged source tarball
(`archive/v<pkgver>.tar.gz`) from this repository, so a release is: bump
`pkgver`, commit, push a `v<pkgver>` tag, then run `updpkgsums` and
`makepkg --printsrcinfo > .SRCINFO`. Do not commit `dist/`, `pkg/`, `repo/`,
or `src/`.

`./make-repo.sh` builds the package and refreshes a pacman repository under
`repo/x86_64` with `repo-add`; `--sign` / `--key KEY` sign the database. Serve
that directory over HTTPS and add it to `/etc/pacman.conf` with
`Server = https://<host>/x86_64`. The public copy is the
[`omarchy-pkgs`](https://github.com/SkyStone-Studio/omarchy-pkgs) repository,
which builds the package in an `archlinux:base-devel` container and publishes
it with GitHub Pages.

## License

MIT. See `LICENSE`.
