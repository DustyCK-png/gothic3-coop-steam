# Gothic 3 Co-op over Steam (experimental)

Steam UDP relay and reproducible build instructions for [G3 Together](https://github.com/GGM1k3y23/g3-together), based on Gothic 3 Steam + Community Patch 1.75.14. Includes a Russian-menu QA patch and source-only profile isolation helper.

**Not a finished multiplayer release.** Two real game clients passed bounded local movement tests, including through a mock Steam relay. Real Steam initialization and lobby creation passed. Two-account Internet gameplay, campaign completion, combat, quests and save/rejoin have NOT been verified by this project. Upstream has additional automated test claims; those are not our local results.

See [Russian instructions](README-RU.md) and [recorded test results](tests/). No game assets, saves, credentials, Steam API binaries or SDK binaries are redistributed.

## Build

Windows, Git, CMake, Visual Studio C++ with Windows SDK, x86. Run `./bootstrap.ps1` from PowerShell. It clones pinned G3 Together and Gothic 3 SDK sources and applies the QA patch.

```powershell
cmake -S . -B build -G "Visual Studio 18 2026" -A Win32
cmake --build build --config Release
cmake -S steam -B steam-build -G "Visual Studio 18 2026" -A Win32
cmake --build steam-build --config Release
cmake -S isolation -B isolation-build -G "Visual Studio 18 2026" -A Win32
cmake --build isolation-build --config Release
```

Find `Script_G3Together.dll` under build, `G3Steam.exe` under steam-build/Release, and `g3shell.dll` under isolation-build/Release. The build does not modify the installed game.

## Install and connect

Use your own matching copies of Gothic 3 and Community Patch 1.75.14. Back up saves. Install the built mod DLL into `scripts` in a separate game copy and copy an example configuration to its root as `g3together.ini`. Give every player a different stable `name`.

Create `SteamLink` under that game copy. Put the built `G3Steam.exe` and a legally obtained official x86 `steam_api.dll` there, and create `steam_appid.txt` containing `480`. The mock DLL is for tests only. Copy `steam/Steam-Host.cmd` and `steam/Steam-Join.cmd` into the GAME COPY ROOT.

Run Steam on both PCs using separate accounts that are friends, then run Steam-Host.cmd on the host and Steam-Join.cmd on the friend. Keep the console open. For the first test choose New Game on both PCs. SteamLink updates role, loopback address and port in the INI, preserves other settings and creates a backup. AppID 480 is Spacewar: this is experimental integration, not official Gothic 3 multiplayer. No manual router port forwarding is required. Steam overlay invitations are not verified; prefer the console friend picker.

Gothic 3 normally uses the Windows user save folder EVEN when the game directory is copied. A separate installation alone does not isolate saves. The optional helper below redirects profiles in disposable copies; do not assume saves are isolated without verifying the reported path.

## Disposable profile isolation

Build `g3shell.dll`, install Python package `pefile`, and create an empty `.g3coop-disposable` marker inside a separate copy that contains no valuable saves. Then run:

```powershell
python isolation/prepare.py "D:\G3-Test" isolation-build/Release/g3shell.dll
```

This backs up and modifies imports in four copied engine DLLs and redirects supported profile folders into that copy's isolated-profile. Other builds may have different imports. Never apply it to your main installation. Shader cache initialization may be required on first startup.

## Tests

`python steam/test_relay.py` uses mock Steam, not real Internet. It checks 1/64/1400/16000 byte packets both ways. To use `--games`, first prepare fully isolated disposable copies at test-host and test-client, install the mod and shader cache, disable intro movies only there, and review isolation/pair.py. The in-game bot activates via qa-enable.txt: this must be absent for normal play.

Recorded results in tests/ are from the original local run, not fresh tests on every checkout. Real API checks from SteamLink: `G3Steam.exe check --no-launch` and `G3Steam.exe check-lobby --no-launch`. These create no invites; the latter creates and immediately leaves a friends-only lobby.

## Licensing and credits

G3 Together: GGM1k3y23 and contributors, GPL-3.0-or-later, pinned commit 61b230a0f6b3cd005d47bbf72a9a5cc690c88dd9. QA patch and isolation sources here: GPL-3.0-or-later. Steam relay: MIT, adapted from cranebeaker/deus-ex-coop commit 1a808a5b2d70f71298d31f72bb32f01caf77ac4e; see steam/LICENSE and source attribution. Gothic 3 SDK: georgeto/gothic3sdk commit 90bfd344de4510dda7ac9da7461cc7f1eac911f7; upstream licenses apply. ENet and other upstream components retain their own licenses.
