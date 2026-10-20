"""Redirect save/profile imports ONLY in a marked disposable game copy. Requires pefile."""
import argparse,shutil
from pathlib import Path
import pefile
parser=argparse.ArgumentParser()
parser.add_argument('game_copy',type=Path)
parser.add_argument('g3shell_dll',type=Path)
args=parser.parse_args()
game=args.game_copy.resolve()
if not (game/'.g3coop-disposable').is_file():raise SystemExit('Refusing: create .g3coop-disposable only inside a separate disposable game copy')
if not args.g3shell_dll.is_file():raise SystemExit('Build g3shell.dll first')
# Only these copied engine DLLs were required by the verified install.
for name in ('Dialogs.dll','Engine.dll','Game.dll','SharedBase.dll'):
 file=game/name
 data=bytearray(file.read_bytes())
 pe=pefile.PE(data=bytes(data))
 for entry in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
  if entry.dll.lower()!=b'shell32.dll':continue
  if not all(item.name==b'SHGetFolderPathA' for item in entry.imports):raise SystemExit('Unexpected imports: '+name)
  offset=pe.get_offset_from_rva(entry.struct.Name)
  if data[offset:offset+11].lower()!=b'shell32.dll':raise SystemExit('Unexpected import bytes')
  backup=file.with_name(file.name+'.before-isolation')
  if not backup.exists():shutil.copy2(file,backup)
  data[offset:offset+11]=b'g3shell.dll'
 pe.close()
 file.write_bytes(data)
shutil.copy2(args.g3shell_dll,game/'g3shell.dll')
for suffix in ('Documents/gothic3','AppData/Roaming','AppData/Local'):(game/'isolated-profile'/suffix).mkdir(parents=True,exist_ok=True)
print('Profile imports redirected in disposable copy:',game)
