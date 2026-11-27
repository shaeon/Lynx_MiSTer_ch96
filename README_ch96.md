# Camputers Lynx para Chameleon96

*English summary below.*

Este repositorio es la versión para la **Chameleon96** (Cyclone V SoC
5CSEBA6U19I7, 512 MB de DDR3) del core Lynx de
[shaeon/Lynx_MiSTer](https://github.com/shaeon/Lynx_MiSTer) (Lynx 48K, 96K, 96K
Scorpion y 128K, a partir de los cores de Kyp). La máquina es la misma: este
repositorio lleva todo el de la DE10-Nano más la capa de la placa. Los
`README.md` y `README_es.md` son los del repositorio principal y explican el
core; este fichero solo cubre lo propio de la Chameleon96.

## Ficheros

El RBF se llama `Lynx_AAAAMMDD_ch96.rbf`, con el sufijo al final como los demás
cores de la Chameleon96, y está en `releases/`. En `releases/` solo hay RBF de
la Chameleon96: los de la DE10-Nano se quitan al sincronizar.

Las ROMs (`roms/boot.rom` y `roms/boot1.rom`) van en `games/Lynx/`, igual que
en la DE10-Nano.

## Qué cambia respecto a la DE10-Nano

`sys/` es el framework de MiSTer para la Chameleon96 de Manuel Teira,
[teiram/Template_MiSTer_ch96](https://github.com/teiram/Template_MiSTer_ch96)
(`aacd20d`), copiado tal cual. Sobre el framework de MiSTer de la misma fecha
que usa el repositorio principal (Template_MiSTer `e901a9f`, 3/11/2026),
añade:

- `sys/ch96_top.sv`, que envuelve `sys_top` en los pines de la placa: vídeo
  RGB565 al TDA19988 (HDMI), audio I2S, I2C del HDMI, LEDs, ventilador y las
  dos PSRAM QSPI del bus *loan I/O* del HPS.
- Los 50 MHz salen del HPS (`h2f_user1_clk`), porque la placa no tiene
  oscilador en la FPGA.
- PWM para el ventilador de la placa.
- El búfer del escalador (0x1E800000) cabe en los 512 MB.
- HDMI a 74,25 MHz (720p), OSD en color y sin ALSA (`MISTER_DISABLE_ALSA`).
- Puertos `PSRAM_*`, `PSRAM2_*` y `CLK_100M` para el core (el Lynx no los usa).
- Revisión de Quartus `Lynx_ch96` (`Lynx_ch96.qpf/.qsf/.sdc`), sacada de su
  `Template_ch96`, con `sys/pins_ch96.tcl` y `sys/hps_ch96.tcl`. `sys.qip` no
  incluye `sys_top.sdc`: la Chameleon96 usa `Lynx_ch96.sdc`.

Lo propio del Lynx:

- La cinta (`.tap`, `.tzx`, `.wav`) se guarda en la DDR3. En la DE10-Nano va en
  0x30000000, que en la Chameleon96 no existe; aquí va en 0x1BC00000 (8 MB),
  dentro de la ventana reservada a la FPGA (0x10000000-0x20000000), con las
  macros `TAPE_DDR_BASE` / `TAPE_DDR_SIZE` de `Lynx_ch96.qsf`.
- El Lynx no usa SDRAM (memoria en la FPGA), así que `Lynx.sv` y `rtl/` son los
  mismos que en la DE10-Nano.
- `Lynx_ch96.qsf` pone `rtl/pre_flow.tcl` como PRE_FLOW, que genera `rtl/gen`
  (los cores de Kyp con sus correcciones) y luego ejecuta `sys/build_id.tcl`.
- La placa no tiene entrada de audio: las cintas se cargan solo desde ficheros.

### Actualizar el framework

- Si Manuel actualiza Template_MiSTer_ch96, se copia su `sys/` entero aquí.
- Si MiSTer actualiza su framework, se actualiza `sys/` en el repositorio
  principal; aquí llega con la sincronización, y si choca con los cambios de
  Manuel se resuelve a mano o se espera a que Manuel saque su versión.

## Sincronización con el repositorio principal

`.github/workflows/sync.yml` se ejecuta cada noche (03:23 UTC) y se puede
lanzar a mano desde *Actions > Sync > Run workflow*:

1. Trae `main` de shaeon/Lynx_MiSTer y lo mezcla con `main`. Los conflictos
   en `releases/` se resuelven solos quitando el fichero, y los de un submódulo
   cogiendo el commit de shaeon/Lynx_MiSTer.
2. Sube los submódulos (`rtl/lynx` y `rtl/lynx128`, los cores de Kyp) al
   último commit de su repositorio, y su T80 a lo que fije ese commit.
3. Quita de `releases/` todo RBF que no termine en `_ch96.rbf`.
4. Si ha cambiado algo en 1 o 2, sube el resultado y lanza la compilación
   (`build_ch96.yml`). Si compila bien, el RBF nuevo queda en `releases/` y
   el actualizador de la Chameleon96 lo recoge; si no, no se publica nada y el
   error se ve en *Actions*.

Si hay un conflicto en otro fichero (lo normal sería en `sys/`, si el
framework de MiSTer cambia en el repositorio principal), el workflow para y el
resumen de la ejecución dice qué ficheros son. Se resuelve a mano:

```
git remote add upstream https://github.com/shaeon/Lynx_MiSTer.git
git fetch upstream
git merge upstream/main
# resolver los conflictos manteniendo los cambios de la Chameleon96
git rm releases/Lynx_*[0-9].rbf     # si ha entrado algún RBF de la DE10-Nano
git commit
git push
```

El `build.yml` del repositorio principal viene en la sincronización pero aquí
no se ejecuta (solo corre en shaeon/Lynx_MiSTer), así que no hay que tocarlo.

## Compilación

`.github/workflows/build_ch96.yml` compila `Lynx_ch96` con Quartus 17.0
(`raetro/quartus:17.0`):

- En cada push a `main` (o al lanzarlo a mano o desde la sincronización)
  compila, deja el RBF y los informes en *Actions* y guarda
  `releases/Lynx_AAAAMMDD_ch96.rbf` con un commit.
- Al subir una etiqueta `v*` crea una Release con el RBF.
- En los pull requests solo compila.

En local: `git clone --recursive https://github.com/shaeon/Lynx_MiSTer_ch96.git`
(los cores de Kyp son submódulos) y abre `Lynx_ch96.qpf` en Quartus Prime Lite
17.0.

Sin probar en la placa todavía.

## Créditos

- Core Lynx: Kyp (cores lynx y lynx128), port a MiSTer de Shaeon (Carlos
  Palmero) con lo de alanswx (Lynx48_MiSTer). Ver `README_es.md`.
- Framework de MiSTer para la Chameleon96: Manuel Teira (teiram),
  [Template_MiSTer_ch96](https://github.com/teiram/Template_MiSTer_ch96).
- Primer port a la Chameleon96: Maverick (Maverick-Shark), de su rama `ch96`
  de TS2068_MiSTer.
- Documentación de la placa: Manuel Teira (teiram),
  [chameleon96-workbench](https://github.com/teiram/chameleon96-workbench).

---

## English summary

Chameleon96 build of the Camputers Lynx core from
[shaeon/Lynx_MiSTer](https://github.com/shaeon/Lynx_MiSTer). The machine is
unchanged; `sys/` is Manuel Teira's Chameleon96 MiSTer framework
([Template_MiSTer_ch96](https://github.com/teiram/Template_MiSTer_ch96)),
with the board wrapper, fan PWM and PSRAM, plus the `Lynx_ch96` Quartus
revision. The tape image lives in DDR3 at 0x1BC00000 (8 MB), inside the
512 MB; the board has no audio line-in.

- RBF files: `releases/Lynx_YYYYMMDD_ch96.rbf` (Chameleon96 only).
- `sync.yml` merges the main repository every night, drops non-`_ch96` RBF
  files and starts `build_ch96.yml`. Other conflicts stop the workflow and are
  listed in the run summary.
- `build_ch96.yml` builds with Quartus 17.0, commits the RBF to `releases/` on
  `main` and creates a release for `v*` tags.

Not tested on the board yet.
