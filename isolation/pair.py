import hashlib
import json
import math
import os
import re
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'local').mkdir(exist_ok=True)
def snapshot():
    dirs=[Path.home()/'Documents/gothic3',Path.home()/'OneDrive/Документы/gothic3']
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for d in dirs for p in d.rglob('*') if p.is_file()}

class Client:
    def __init__(self,tag):
        self.root=ROOT/f'test-{tag}'
        self.tag=tag
        self.seq=1
        self.process=None
    def log(self):
        p=self.root/'qa-engine.log'
        return p.read_text(encoding='mbcs',errors='replace') if p.exists() else ''
    def wait(self,predicate,seconds=30):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if self.process.poll() is not None:raise RuntimeError(f'{self.tag}: exited {self.process.returncode}')
            value=predicate(self.log())
            if value:return value
            time.sleep(.5)
        raise RuntimeError(f'{self.tag}: timeout; '+self.log()[-1600:])
    def send(self,action,expected,seconds=30):
        self.seq+=1
        old=len(self.log())
        for _ in range(30):
            try:(self.root/'qa-command.txt').write_text(f'{self.seq} {action}\n');break
            except PermissionError:time.sleep(.1)
        return self.wait(lambda text:next((line for line in text[old:].splitlines() if line.startswith(expected)),None),seconds)
    def start(self):
        role='host' if self.tag=='host' else 'client'
        if not os.environ.get('G3_STEAM_TEST'):
            (self.root/'g3together.ini').write_text(f'role = {role}\naddress = 127.0.0.1\nport = 34567\nname = {self.tag}\n')
        for name in ('qa-engine.log','g3together.log'):(self.root/name).unlink(missing_ok=True)
        (self.root/'qa-enable.txt').write_text('Disposable bounded two-client test')
        (self.root/'qa-command.txt').write_text('1 state\n')
        self.process=subprocess.Popen([str(self.root/'Gothic3.exe')],cwd=self.root)
        menu=self.wait(lambda text:next((line for line in text.splitlines() if line.startswith('STATE ')),None),90)
        assert str(self.root/'isolated-profile') in menu,menu
        self.send('focusnew','MENU_FOCUS id=20571 focused=1')
        self.send('pressenter','PRESSENTER ')
        time.sleep(2)
        self.send('focusyes','MENU_FOCUS id=20711 focused=1')
        self.send('pressenter','PRESSENTER ')
        self.wait(lambda _: 'world=G3_World_01 running=1 hero=PC_Hero' in (self.root/'g3together.log').read_text(encoding='mbcs',errors='replace'),180)
        state=self.send('state','STATE running=1 ')
        assert str(self.root/'isolated-profile') in state,state
    def remote(self):
        self.send('remotes','REMOTES end')
        lines=[line for line in self.log().splitlines() if line.startswith('REMOTE id=')]
        return lines[-1] if lines else ''

before=snapshot()
(ROOT/'local/profile-before.json').write_text(json.dumps(before),encoding='utf8')
clients=[Client('host'),Client('client')]
report={'test':'two real Gothic 3 clients over '+('Steam API mock relay' if os.environ.get('G3_STEAM_TEST') else 'loopback'),'status':'failed'}
try:
    host,client=clients
    host.start()
    host.send('releaselock','LOCK scan complete')
    client.start()
    for copy in clients:
        end=time.monotonic()+40
        while time.monotonic()<end:
            line=copy.remote()
            if 'same_world=1' in line and 'puppet=1' in line:break
            time.sleep(1)
        else:raise RuntimeError(f'{copy.tag}: remote puppet missing: {line}')
        report[copy.tag+'_remote']=line
    errors=[]
    for i in range(4):
        step=client.send(f'step {i}','STEP ')
        actual=tuple(map(float,re.search(r' pos=([-\d.,]+)',step)[1].split(',')))
        end=time.monotonic()+15
        while time.monotonic()<end:
            line=host.remote()
            match=re.search(r'puppet=1 puppet_pos=([-\d.,]+)',line)
            if match:
                seen=tuple(map(float,match[1].split(',')))
                distance=math.dist(actual,seen)
                if distance<=50:errors.append(round(distance,2));break
            time.sleep(.5)
        else:raise RuntimeError(f'Host puppet did not follow step {i}: {line}')
    report['movement_errors_cm']=errors
    report['status']='passed'
except Exception as error:report['error']=str(error)
finally:
    for copy in reversed(clients):
        if copy.process and copy.process.poll() is None:
            copy.process.terminate()
            try:copy.process.wait(timeout=10)
            except subprocess.TimeoutExpired:copy.process.kill();copy.process.wait()
        (copy.root/'qa-enable.txt').unlink(missing_ok=True)
    after=snapshot()
    (ROOT/'local/profile-after.json').write_text(json.dumps(after),encoding='utf8')
    report['changed_protected_files']=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
    report['protected_saves_unchanged']=after==before
    if not report['protected_saves_unchanged']:report['status']='failed'
    (ROOT/('local/pair-steam-mock.json' if os.environ.get('G3_STEAM_TEST') else 'local/pair.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(report,ensure_ascii=True),flush=True)
