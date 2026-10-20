import json,os,pathlib,shutil,socket,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
(ROOT/'local').mkdir(exist_ok=True)
test=ROOT/'steam-tests'
processes=[]
logs=[]
report={'status':'failed','transport':'Steam API mock, not real Steam'}
def wait(predicate,seconds=20):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        result=predicate()
        if result:return result
        if any(p.poll() is not None for p in processes):raise RuntimeError('Relay process exited')
        time.sleep(.1)
    raise TimeoutError('Relay startup timeout')
def launch(role,game,port):
    folder=test/role
    folder.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'steam-build/Release/G3Steam.exe',folder)
    shutil.copy2(ROOT/'steam-build/Release/mock_steam_api.dll',folder/'steam_api.dll')
    env=os.environ.copy();env['KFX_MOCK_STEAM_NAME']='Host' if role=='host' else 'Client'
    env['KFX_MOCK_STEAM_PORT_BASE']='48200';env['KFX_MOCK_STEAM_LOG']='1'
    logfile=folder/'relay.log';f=logfile.open('w');logs.append(f)
    p=subprocess.Popen([str(folder/'G3Steam.exe'),'host' if role=='host' else 'join','--game',str(game),'--port',str(port),'--no-launch'],cwd=folder,env=env,stdout=f,stderr=subprocess.STDOUT)
    processes.append(p)
    wait(lambda:'Configured Gothic 3:' in logfile.read_text(errors='replace'))
    return logfile
try:
    game_test='--games' in sys.argv
    port=34567 if game_test else 39567
    host_game=ROOT/'test-host' if game_test else test/'fake-host'
    client_game=ROOT/'test-client' if game_test else test/'fake-client'
    for folder in (host_game,client_game):
        folder.mkdir(parents=True,exist_ok=True)
        if not (folder/'g3together.ini').exists():(folder/'g3together.ini').write_text('name = Test\n')
    hostlog=launch('host',host_game,port)
    clientlog=launch('client',client_game,port)
    if game_test:
        env=os.environ.copy();env['G3_STEAM_TEST']='1'
        run=subprocess.run([sys.executable,str(ROOT/'isolation/pair.py')],env=env,capture_output=True,text=True,timeout=420)
        report['game_test']=json.loads((ROOT/'local/pair-steam-mock.json').read_text(encoding='utf8'))
        assert report['game_test']['status']=='passed',report['game_test']
    else:
        ini=(client_game/'g3together.ini').read_text()
        client_port=int([s.split('=')[1] for s in ini.splitlines() if s.startswith('port =')][-1])
        echo=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);echo.bind(('127.0.0.1',port));echo.settimeout(10)
        player=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);player.settimeout(10)
        report['packet_sizes']=[]
        for size in (1,64,1400,16000):
            data=os.urandom(size);player.sendto(data,('127.0.0.1',client_port))
            incoming,address=echo.recvfrom(65536);assert incoming==data
            echo.sendto(incoming,address);reply,_=player.recvfrom(65536);assert reply==data
            report['packet_sizes'].append(size)
        echo.close();player.close()
    report['status']='passed'
except Exception as error:report['error']=str(error)
finally:
    for p in reversed(processes):
        if p.poll() is None:p.terminate();p.wait(timeout=10)
    for f in logs:f.close()
    target=ROOT/'local'/('steam-game-test.json' if '--games' in sys.argv else 'steam-relay-test.json')
    target.write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report))
    if report['status']!='passed':
        for role in ('host','client'):
            path=test/role/'relay.log'
            if path.exists():print(role,path.read_text(errors='replace')[-2000:])
        sys.exit(1)
