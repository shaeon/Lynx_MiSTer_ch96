#!/usr/bin/env python3
# Correcciones a los cores de Kyp (Kyp069/lynx y Kyp069/lynx128), en un solo sitio.
#
# Las mismas correcciones van:
#   - como commits en los forks shaeon/lynx y shaeon/lynx128, para los PR a Kyp:
#         python3 tools/kyp_fixes.py apply <carpeta del repo> lynx|lynx128 [grupo]
#   - como parches que rtl/pre_flow.tcl aplica a los submodulos al generar rtl/gen:
#         python3 tools/kyp_fixes.py tcl      (escribe rtl/kyp_fixes.tcl)
#
# Cada correccion es un par (texto original, texto corregido). Al aplicarla: si el texto
# corregido ya esta (Kyp ha aceptado el PR), no se hace nada; si el original aparece una sola
# vez, se sustituye; en cualquier otro caso es un error. Cuando Kyp acepte un grupo, se puede
# borrar de aqui.
#
# Origen: las correcciones de Lynx48_MiSTer (MiSTer-devel, alanswx, nov-2026), hechas sobre
# este mismo core.
import os, sys

FIXES = [
    # (repo, fichero, grupo, mensaje del commit, [(original, corregido), ...])
    #
    # Vacia: Kyp ha integrado todas las correcciones, con sus nombres, en Kyp069/lynx (dd9bdce)
    # y Kyp069/lynx128 (8e5adad): puerto 58h, 6845 legible en 86h/87h, /CASEN al escribir,
    # bit de cinta con MA13, ROM 48K en 0000-5FFF, salidas blank y motor, entrada break
    # (activa a nivel bajo) y teclas End, Ctrl derecho y Enter del teclado numerico.
]


def fix_text(text, pairs, where):
    for old, new in pairs:
        if new in text:
            continue
        n = text.count(old)
        if n != 1:
            sys.exit('%s: el texto a corregir aparece %d veces:\n%s' % (where, n, old))
        text = text.replace(old, new)
    return text


def tcl_quote(s):
    if s.count('{') != s.count('}') or '\\' in s:
        sys.exit('no se puede poner entre llaves en Tcl: ' + s)
    return '{' + s + '}'


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) >= 2 and sys.argv[1] == 'tcl':
        out = ['# GENERADO por tools/kyp_fixes.py (no editar): correcciones a los cores de Kyp.',
               '# Lista de { repo fichero grupo {original corregido ...} }.',
               'set kyp_fixes {']
        for repo, fname, group, _msg, pairs in FIXES:
            flat = ' '.join(tcl_quote(o) + ' ' + tcl_quote(n) for o, n in pairs)
            out.append('\t{%s %s %s {%s}}' % (repo, fname, group, flat))
        out.append('}')
        path = os.path.join(here, '..', 'rtl', 'kyp_fixes.tcl')
        open(path, 'w', newline='\n').write('\n'.join(out) + '\n')
        print('escrito', os.path.normpath(path))
    elif len(sys.argv) >= 4 and sys.argv[1] == 'apply':
        root, repo = sys.argv[2], sys.argv[3]
        only = sys.argv[4] if len(sys.argv) > 4 else None
        for r, fname, group, msg, pairs in FIXES:
            if r != repo or (only and group != only):
                continue
            p = os.path.join(root, fname)
            text = open(p, newline='').read()
            open(p, 'w', newline='').write(fix_text(text, pairs, '%s/%s (%s)' % (repo, fname, group)))
    elif len(sys.argv) >= 3 and sys.argv[1] == 'groups':
        seen = []
        for r, fname, group, msg, pairs in FIXES:
            if r == sys.argv[2] and group not in [g for g, _ in seen]:
                seen.append((group, msg))
        for g, m in seen:
            print(g + '\t' + m.split('\n')[0])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'msg':
        for r, fname, group, msg, pairs in FIXES:
            if r == sys.argv[2] and group == sys.argv[3]:
                print(msg)
                break
    else:
        sys.exit(__doc__ or 'uso: kyp_fixes.py tcl | apply <dir> <repo> [grupo] | groups <repo> | msg <repo> <grupo>')


if __name__ == '__main__':
    main()
