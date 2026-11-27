# Camputers Lynx para MiSTer

Core de MiSTer del **Camputers Lynx** (1983) que junta en uno solo los dos
cores del Lynx de **Kyp**. El modelo se elige en el OSD:

| Modelo | Core de Kyp |
|---|---|
| Lynx 48K, 96K y 96K con ROM Scorpion | [lynx.poseidon](https://github.com/Kyp069/lynx.poseidon) ([lynx](https://github.com/Kyp069/lynx)) |
| Lynx 128K | [lynx128.poseidon](https://github.com/Kyp069/lynx128.poseidon) ([lynx128](https://github.com/Kyp069/lynx128)) |

Port a MiSTer: Shaeon (Carlos Palmero). El reproductor de cinta (TAP, TZX,
WAV), la carga rápida, las pistas en pantalla y la memoria en la FPGA vienen del
core oficial [Lynx48_MiSTer](https://github.com/MiSTer-devel/Lynx48_MiSTer) de
alanswx, que partió de este.

No necesita módulo de SDRAM.

## Instalación

- Copia el `.rbf` a `/media/fat/_Computer/`.
- Copia `roms/boot.rom` (48K/96K) y `roms/boot1.rom` (128K) a
  `/media/fat/games/Lynx/`. Las dos se cargan solas al arrancar el core.
- Las cintas (`.tap`, `.tzx`, `.wav`) y los discos (`.ldf`) pueden ir en la
  misma carpeta.

En [roms/README.md](roms/README.md) está qué lleva cada fichero de ROM. Están
montadas a partir de los juegos de ROMs de MAME (`lynx48k`, `lynx96k`,
`lynx128k`) e incluyen la ROM de la disquetera (XDOS).

## OSD

| Opción | Página | |
|---|---|---|
| Disk | principal | Imagen de disco `.LDF` para la WD1793 (escribe `XROM` para arrancar el DOS) |
| Tape | principal | `.TAP` (Lynx), `.TZX` o `.WAV` |
| Model | Machine | Lynx 48K, Lynx 96K, 96K Scorpion, Lynx 128K |
| CAS blanking | Machine | On (por defecto): un plano de color se apaga mientras su bit /CASEN lo desactiva (lo necesitan las aventuras de Level 9). Solo 48K/96K |
| Tape speed | Machine | 4x (por defecto): la CPU y la cinta van 4 veces más rápido mientras suena la cinta; Normal |
| Rewind tape | Machine | Rebobina la cinta |
| Aspect ratio, Scale, Scandoubler Fx | Video | |
| Tape overlay | Video | Barra de estado de la cinta y pista del siguiente paso (On / Off) |
| Swap joysticks | Input | |
| Tape audio, Invert tape in | Audio | Oír la cinta; polaridad de un `.WAV` o de un casete por la entrada de audio |

El modelo y CAS blanking se aplican con **Apply and reset** ("Changes pending"
avisa de que hay algo pendiente). **F9** hace reset del Lynx.

## Cargar programas

El Lynx carga por nombre y no admite comodín:

    LOAD "NOMBRE"      programa BASIC, luego RUN
    MLOAD "NOMBRE"     código máquina

El nombre de la cinta muchas veces no es el del fichero. Con la cinta parada,
la esquina inferior izquierda muestra qué escribir, leído de la propia cinta
(`TYPE LOAD "SNAKE"`, luego `TYPE RUN`); mientras suena, el tiempo y una barra
de progreso.

- `.TAP` (formato de Jynx / PALE, casi todo el software): el core rehace la
  señal de la cinta a partir de los bytes, siguiendo `TAPE 1` a `TAPE 5` en el
  48K/96K.
- `.TZX` (hechos de grabaciones): suena tal cual; escribe el `TAPE n` que diga
  el nombre del fichero. Arranca y para con el motor, o con RePág / AvPág.
- `.WAV` (PCM de 8 o 16 bits): suena tal cual, como la entrada de audio.
- Casetes de verdad: entrada de audio de MiSTer (ADC).

La cinta se mueve mientras el Lynx tiene el motor encendido. ESC corta un
`LOAD` que se ha quedado esperando.

**Disco**: `XROM`, luego `EXT DIR`, `EXT LOAD "NOMBRE"`, `EXT MLOAD "NOMBRE"`;
los discos CP/M arrancan con `EXT BOOT`. Como en los cores de Kyp, todos los
modelos tienen la disquetera. Valen los dos tamaños de LDF de la lista
`camplynx_flop` de MAME: 200K (40 pistas, una cara) y 800K (80 pistas, dos
caras). CP/M solo salió para el 128K; para CP/M en el 96K, ver
[Lynx96_CPM](https://github.com/shaeon/Lynx96_CPM).

**Teclado**: las teclas del PC están donde las del Lynx. Bloq Mayús = SHIFT
LOCK, Esc = ESCAPE, Bloq Despl = BREAK, Retroceso = DELETE, Fin = la tecla que MAME pone
en Fin. **Joysticks**: puertos 0x7A y 0x7B, un botón de disparo.

## Cómo funciona

Las dos máquinas están dentro del core (`rtl/lynx_core.sv`) y solo funciona la
elegida; la otra se queda en reset. Comparten la memoria, la WD1793, la cinta,
el teclado, el audio y el vídeo. Todo está en la memoria interna de la FPGA:
ROMs (64K + 32K), RAM (64K + el banco 4 del 128K) y memoria de vídeo.

| | 48K / 96K | 128K |
|---|---|---|
| CPU | 4 MHz (16 MHz en turbo) | 6 MHz (24 MHz en turbo) |
| Píxel / 6845 | 6 MHz / 0,75 MHz | 12 MHz / 1,5 MHz |
| ROM | `boot.rom`, 64K | `boot1.rom`, 32K |

**Los cores de Kyp son submódulos y no se tocan** (`rtl/lynx` y
`rtl/lynx128`). Antes de cada compilación, `rtl/pre_flow.tcl` escribe en
`rtl/gen/`:

- `lynx48.v` y `lynx128.v`: `lynx.v` + `video.v` de cada core con los módulos
  renombrados (los dos repositorios tienen módulos `lynx` y `video` distintos
  con el mismo nombre, y Quartus no lo admite);
- `matrix.v`: el teclado (el de `rtl/lynx`);

aplicando las correcciones que haya en `tools/kyp_fixes.py` (que se vuelcan en
`rtl/kyp_fixes.tcl`). Ahora la lista está vacía: Kyp ha metido en sus cores
(Kyp069/lynx dd9bdce, Kyp069/lynx128 55ecc58) las correcciones que encontró
alanswx en Lynx48_MiSTer, que le mandamos como pull requests desde los forks
[shaeon/lynx](https://github.com/shaeon/lynx) y
[shaeon/lynx128](https://github.com/shaeon/lynx128):

| Corrección | 48K/96K | 128K |
|---|---|---|
| El puerto 58h solo se escribe en ciclos de escritura | ✓ | ✓ |
| 6845 legible en 86h/87h (como en MAME) | ✓ | ✓ |
| Escritura en la memoria de vídeo solo con /CASEN del banco (esquema, IC41) | ✓ | |
| Bit de cinta del puerto 80h con MA13 del 6845 (Jynx, esquema) y no con el del motor: arregla los Level 9 | ✓ | |
| 48K: ROM en 0000-5FFF (el zócalo vacío lee FF) | ✓ | |
| Entrada `break`: /INT (BREAK, como en MAME), con Bloq Despl | ✓ | ✓ |
| Salidas `blank` (display enable del 6845) y `motor` | ✓ | ✓ |
| Teclado: Fin, Ctrl derecho y Enter del teclado numérico | ✓ | ✓ |

El mecanismo se queda para correcciones futuras: una que ya esté en el
submódulo se salta, y si un cambio de Kyp rompe alguna, la compilación se para
con un error en vez de generar algo distinto. Después de tocar
`tools/kyp_fixes.py`, ejecuta `python3 tools/kyp_fixes.py tcl`.

Otras piezas:

- **ROMs**: Main_MiSTer carga `boot1.rom` con índice 0x40 y `boot.rom` con
  índice 0. La máquina se queda en reset hasta que se ha cargado una ROM.
- **Memoria de vídeo**: `rtl/vram.v` sustituye al `dprf` de Kyp, que Quartus 17
  no sabe meter en los bloques M10K del Cyclone V.
- **Blanking**: el horizontal sale del DE del 6845, retrasado un carácter como
  los píxeles en `video.v`; el vertical, de las líneas con DE del cuadro
  anterior.
- **Cinta**: `rtl/tape_ddr.sv` y `rtl/tzxplayer.vhd` (cinta en la DDR3),
  `rtl/lynx_tap.sv` (TAP), `rtl/lynx_wav.sv` (WAV) y `rtl/lynx_tape_overlay.sv`
  (barra de estado y pistas, con la letra del propio Lynx, `rtl/lynx_font.vh`,
  que saca `tools/make_font.py` de la ROM del 48K).

## Compilación

```
git clone --recursive https://github.com/shaeon/Lynx_MiSTer.git
```

(Hace falta `--recursive`: los cores de Kyp traen el T80 como submódulo anidado.)
Abre `Lynx.qpf` con Quartus 17.0 y compila, o ejecuta `build.bat`, que deja el
RBF en `releases/`.

GitHub Actions (`.github/workflows/build.yml`) compila el core en cada `push`
con Quartus 17.0 (imagen Docker `raetro/quartus:17.0`) y guarda el `.rbf` y los
informes en la pestaña *Actions*. Al subir una etiqueta `v*` crea además una
Release con el `.rbf`.

## Créditos y agradecimientos

- **Kyp** (Kyp069): los cores del Lynx 48K/96K y 128K sobre los que está hecho
  este port.
- **alanswx** y los colaboradores de
  [Lynx48_MiSTer](https://github.com/MiSTer-devel/Lynx48_MiSTer) (rampa069,
  Yo_Me, JasonA, JimmyStones, Fernando Mosquera, Brendan Saricks,
  jackyangantelope): las correcciones de arriba, los reproductores TAP y WAV,
  el turbo, la barra de la cinta y la máquina en memoria interna
  (`rtl/lynx_core.sv`).
- **RetroWiki** y su equipo FPGA (RW-FPGA-devel-Team): rampa069 y ron hicieron
  el primer port del Lynx a MiSTer y
  [lynx2wav](https://github.com/RW-FPGA-devel-Team/lynx2wav); y gracias a toda
  la comunidad de RetroWiki por mantener vivo el Lynx.
- **Jonathan Markland** ([Jynx](https://github.com/jonathan-markland/Jynx)): la
  forma de la señal de cinta que reproduce el reproductor TAP.
- MAME (driver camplynx: Robbbert, Nigel Barnes), PALE (Peter Todd), la
  documentación del Lynx recopilada por ukscone y los esquemas redibujados por
  Board-Folk.
- T80 (Daniel Wallner, MikeJ y otros), UM6845R y WD1793 (Sorgelig y otros
  desarrolladores de MiSTer), tzxplayer (György Szombathelyi) y el marco de
  MiSTer (MiSTer-devel).

## Licencia

GPL v3, como los cores de Kyp (el marco `sys/` es GPL v2 o posterior). Las ROMs
son propiedad de sus autores y se incluyen con fines de preservación.

---

Desarrollado con la ayuda de Claude (Anthropic).
