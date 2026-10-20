#include <Windows.h>
#include <cstdio>
#include <cstring>
#include <initializer_list>
int wmain(int argc, wchar_t** argv) {
    if (argc != 2) return 2;
    HMODULE dll = LoadLibraryW(argv[1]);
    if (!dll) return 3;
    auto fn = reinterpret_cast<HRESULT(__stdcall*)(HWND,int,HANDLE,DWORD,LPSTR)>(GetProcAddress(dll,"SHGetFolderPathA"));
    if (!fn) return 4;
    for (int id : {5,26,28,40}) {
        char path[MAX_PATH] = {};
        if (FAILED(fn(nullptr,id,nullptr,0,path)) || !strstr(path,"\\isolated-profile")) return 5;
        printf("folder=%d path=%s\n",id,path);
    }
    char path[MAX_PATH] = {};
    if (SUCCEEDED(fn(nullptr,0x77,nullptr,0,path)) || *path) return 6;
    puts("PASS: profile folders redirected; unknown folders refused");
    return 0;
}
