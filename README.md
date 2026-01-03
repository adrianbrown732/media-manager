Portable Media Manager

A local media management tool for preparing and syncing a personal music
library to portable audio players that do not require proprietary software.

Overview

Many portable audio players function as simple storage devices. Audio files
are copied onto internal storage or an SD card, and the device performs a
library scan. When no vendor-provided management software exists,
organization, metadata quality, and playlist correctness become the user’s
responsibility.

This project implements a reproducible, filesystem- and metadata-driven
workflow for managing and syncing a personal music library to such devices.

The focus is on correctness, determinism, and inspectability rather than UI
or streaming integration.

Motivation

Personal music libraries often contain:

inconsistent or missing metadata

duplicate files across folders

naming conventions that sort incorrectly on devices

playlists that break when directory layouts change

Without proprietary tooling, these issues must be handled manually. This
project treats audio files as structured data and applies an
Extract–Transform–Load (ETL) approach to make the process reliable and
repeatable.

Design Principles

User-defined conventions
The device does not impose any required directory structure. All layout
decisions are explicit and configurable.

Read-only source library
Source files are never modified during scanning or validation.

Idempotent syncing
Re-running the tool should not duplicate files or corrupt device state.

Explicit contracts
Paths, assumptions, and behaviors are documented and enforced.

CLI-first
Designed for automation, scripting, and inspection.

System Model

Source music library:

/mnt/e/

Treated as read-only

May contain arbitrary directory layouts

Device access:

/mnt/d

Device mounted by Windows as D:

Accessed in WSL2 via drvfs

Managed device library root:

/mnt/d/music/

User-defined convention

Created manually on first use

All synced content lives under this directory

The device itself does not require or enforce any folder structure.

Architecture

Extract:

Recursively scan the source directory

Identify supported audio formats

Read core metadata fields (artist, album, title, track number, disc number)

Transform:

Validate required metadata

Normalize naming and directory structure

Detect duplicates using content hashes

Generate a device-compatible file layout

Load:

Sync files into the managed device library

Copy only new or changed files

Preserve relative paths for playlist compatibility

Scope

MVP (v0.1):

Library scanning

Metadata validation

Directory normalization

Idempotent device sync

Dry-run support

Out of scope (v1):

Streaming services

Graphical UI

Cover art rewriting

Recommendation systems

Planned CLI Usage

Examples (subject to change):

media scan --source /mnt/e
media validate --source /mnt/e --report report.json
media sync --source /mnt/e --device-root /mnt/d --library-root music --dry-run

All paths and conventions are configurable via CLI flags or a config file.

Project Structure

portable-media-manager/
media/
scan.py
validate.py
normalize.py
hash.py
sync/
diff.py
copy.py
tests/
cli.py
config.yaml
README.md

Roadmap

v0.1
scan -> validate -> sync

v0.2
playlist generation (.m3u / .m3u8)

v0.3
library quality reports and metrics

Suggested initial commit message:

Initialize project with documented storage model and design scope
