# Camputers Lynx for MiSTer

MiSTer core of the **Camputers Lynx** (1983) that brings together the two
Lynx cores by **Kyp** in a single core. The model is chosen in the OSD:

| Model | Kyp's core |
|---|---|
| Lynx 48K, 96K and 96K with Scorpion ROM | [lynx.poseidon](https://github.com/Kyp069/lynx.poseidon) ([lynx](https://github.com/Kyp069/lynx)) |
| Lynx 128K | [lynx128.poseidon](https://github.com/Kyp069/lynx128.poseidon) ([lynx128](https://github.com/Kyp069/lynx128)) |

MiSTer port: Shaeon (Carlos Palmero). The tape player (TAP, TZX, WAV), the
fast loading, the on-screen tape hints and the block-RAM memory come from the
official [Lynx48_MiSTer](https://github.com/MiSTer-devel/Lynx48_MiSTer) core by
alanswx, which was built on this one.

No SDRAM module is needed.

Documentation in Spanish: [README_es.md](README_es.md).

## Installation

- Copy the `.rbf` to `/media/fat/_Computer/`.
- Copy `roms/boot.rom` (48K/96K) and `roms/boot1.rom` (128K) to
  `/media/fat/games/Lynx/`. Both are loaded automatically when the core starts.
- Tapes (`.tap`, `.tzx`, `.wav`) and disks (`.ldf`) can go in the same folder.

See [roms/README.md](roms/README.md) for what each ROM file contains. They are
built from the MAME ROM sets (`lynx48k`, `lynx96k`, `lynx128k`) and include
the disk ROM (XDOS).

## OSD

| Option | Page | |
|---|---|---|
| Disk | top | `.LDF` disk image for the WD1793 (type `XROM` to start the Lynx DOS) |
| Tape | top | `.TAP` (Lynx), `.TZX` or `.WAV` |
| Model | Machine | Lynx 48K, Lynx 96K, 96K Scorpion, Lynx 128K |
| CAS blanking | Machine | On (default): a colour plane is blanked while its /CASEN bit switches it off (Level 9 adventures need it). 48K/96K only |
| Tape speed | Machine | 4x (default): the CPU and the tape run 4 times faster while the tape plays; Normal |
| Rewind tape | Machine | Back to the start of the tape |
| Aspect ratio, Scale, Scandoubler Fx | Video | |
| Tape overlay | Video | Tape status bar and the next-step hint (On / Off) |
| Swap joysticks | Input | |
| Tape audio, Invert tape in | Audio | Hear the tape; polarity of a `.WAV` or a real cassette on the line-in |

Model and CAS blanking are applied with **Apply and reset** ("Changes pending"
shows that something is waiting). **F9** resets the Lynx.

## Loading software

The Lynx loads by name and has no wildcard:

    LOAD "NAME"        BASIC program, then RUN
    MLOAD "NAME"       machine code

The name on the tape is often not the file name. While the tape is stopped the
bottom-left corner shows what to type, read from the tape itself
(`TYPE LOAD "SNAKE"`, then `TYPE RUN`); while it plays it shows the time and a
progress bar.

- `.TAP` (Jynx / PALE format, most of the software): the core rebuilds the tape
  signal from the bytes, following `TAPE 1` to `TAPE 5` on the 48K/96K.
- `.TZX` (made from recordings): played as recorded; type the `TAPE n` the file
  name says. It starts and stops with the tape motor, or with PgUp / PgDn.
- `.WAV` (8- or 16-bit PCM): played as recorded, like the line-in.
- Real cassettes: MiSTer audio line-in (ADC).

The tape moves while the Lynx switches the motor on. ESC stops a `LOAD` that
is waiting.

**Disk**: `XROM`, then `EXT DIR`, `EXT LOAD "NAME"`, `EXT MLOAD "NAME"`; CP/M
disks start with `EXT BOOT`. As in Kyp's cores, every model has the disk
interface.

**Keyboard**: the PC keys sit where the Lynx keys are. Caps Lock = SHIFT LOCK,
Esc = ESCAPE (also BREAK), Backspace = DELETE, End = the key MAME maps to
End. **Joysticks**: ports 0x7A and 0x7B, one fire button.

## How it works

Both machines are inside the core (`rtl/lynx_core.sv`), and only the selected
one runs; the other is held in reset. They share the memory, the WD1793, the
tape, the keyboard, audio and video. Everything is in block RAM: ROMs (64K +
32K), user RAM (64K + the 128K's bank 4) and video RAM.

| | 48K / 96K | 128K |
|---|---|---|
| CPU | 4 MHz (16 MHz in turbo) | 6 MHz (24 MHz in turbo) |
| Pixel / 6845 | 6 MHz / 0.75 MHz | 12 MHz / 1.5 MHz |
| ROM | `boot.rom`, 64K | `boot1.rom`, 32K |

**Kyp's cores are git submodules and are not modified** (`rtl/lynx` and
`rtl/lynx128`). Before each build, `rtl/pre_flow.tcl` writes to `rtl/gen/`:

- `lynx48.v` and `lynx128.v`: `lynx.v` + `video.v` of each core with the
  modules renamed (both repositories have modules called `lynx` and `video`
  with different contents, which Quartus does not allow);
- `matrix.v`: the keyboard;

applying the fixes in `tools/kyp_fixes.py` (written out to `rtl/kyp_fixes.tcl`):

| Fix | 48K/96K | 128K |
|---|---|---|
| Port 58h written only on write cycles | ✓ | |
| 6845 readable at 86h/87h (as MAME) | ✓ | ✓ |
| Video RAM writes need the bank's /CASEN (schematic IC41) | ✓ | |
| Tape bit of port 80h while the 6845's MA13 is high (Jynx, schematic), not the motor bit: fixes Level 9 | ✓ | |
| 48K: ROM space 0000-5FFF (empty socket reads FF) | ✓ | |
| ESC raises /INT (BREAK, as MAME) | ✓ | ✓ |
| `de` (6845 display enable) and `motor` outputs | ✓ | ✓ |
| Keyboard: `esc` output, End, right Ctrl, keypad Enter | ✓ | ✓ |

They are the fixes found by alanswx in Lynx48_MiSTer. The same changes are
offered to Kyp as pull requests from the forks
[shaeon/lynx](https://github.com/shaeon/lynx) and
[shaeon/lynx128](https://github.com/shaeon/lynx128). A fix that is already in
the submodule is skipped, so they can be removed from `tools/kyp_fixes.py` as
Kyp accepts them; if a change of Kyp's breaks one, the build stops with an
error instead of building something different. After editing
`tools/kyp_fixes.py`, run `python3 tools/kyp_fixes.py tcl`.

Other parts:

- **ROMs**: Main_MiSTer loads `boot1.rom` with index 0x40 and `boot.rom` with
  index 0. The machine stays in reset until a ROM has been loaded.
- **Video RAM**: `rtl/vram.v` replaces Kyp's `dprf`, which Quartus 17 cannot
  map into the Cyclone V M10K blocks.
- **Blanking**: horizontal from the 6845 DE, delayed by one character like the
  pixels in `video.v`; vertical from the lines with DE in the previous frame.
- **Tape**: `rtl/tape_ddr.sv` and `rtl/tzxplayer.vhd` (tape image in DDR3),
  `rtl/lynx_tap.sv` (TAP), `rtl/lynx_wav.sv` (WAV) and
  `rtl/lynx_tape_overlay.sv` (status bar and hints, with the Lynx's own font,
  `rtl/lynx_font.vh`, made by `tools/make_font.py` from the 48K ROM).

## Building

```
git clone --recursive https://github.com/shaeon/Lynx_MiSTer.git
```

(`--recursive` is needed: Kyp's cores bring the T80 as a nested submodule.)
Open `Lynx.qpf` with Quartus 17.0 and compile, or run `build.bat`, which
leaves the RBF in `releases/`.

GitHub Actions (`.github/workflows/build.yml`) compiles the core on every push
with Quartus 17.0 (`raetro/quartus:17.0` Docker image) and keeps the `.rbf`
and the reports as an artifact in the *Actions* tab. Pushing a `v*` tag also
creates a Release with the `.rbf`.

## Credits and thanks

- **Kyp** (Kyp069): the Lynx 48K/96K and 128K cores this port is built on.
- **alanswx** and the [Lynx48_MiSTer](https://github.com/MiSTer-devel/Lynx48_MiSTer)
  contributors (rampa069, Yo_Me, JasonA, JimmyStones, Fernando Mosquera,
  Brendan Saricks, jackyangantelope): the fixes above, the TAP / WAV players,
  the turbo, the tape overlay and the block-RAM machine (`rtl/lynx_core.sv`).
- **RetroWiki** and its FPGA team (RW-FPGA-devel-Team): rampa069 and ron made
  the first Lynx port for MiSTer and
  [lynx2wav](https://github.com/RW-FPGA-devel-Team/lynx2wav); and thanks to
  the whole RetroWiki community for keeping the Lynx alive.
- **Jonathan Markland** ([Jynx](https://github.com/jonathan-markland/Jynx)):
  the tape waveform the TAP player reproduces.
- MAME (camplynx driver: Robbbert, Nigel Barnes), PALE (Peter Todd), the Lynx
  documentation collected by ukscone and the schematics redrawn by Board-Folk.
- T80 (Daniel Wallner, MikeJ and others), UM6845R and WD1793 (Sorgelig and
  other MiSTer developers), tzxplayer (György Szombathelyi), and the MiSTer
  framework (MiSTer-devel).

## Licence

GPL v3, like Kyp's cores (the `sys/` framework is GPL v2 or later). The ROMs
are the property of their authors and are included for preservation.

---

Developed with the help of Claude (Anthropic).
