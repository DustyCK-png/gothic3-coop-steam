#include <Windows.h>
#include <cstdio>
#include <cwchar>

// Only copied engine DLLs import this name. No registry or global profile changes.
extern "C" HRESULT __stdcall IsolatedFolderPathA(HWND, int folder, HANDLE token, DWORD, LPSTR out)
{
    if (!out) return E_INVALIDARG;
    *out = 0;
    if (token) return E_ACCESSDENIED;
    const wchar_t* suffix = nullptr;
    switch (folder & 0xff) {
        case 5: suffix = L"\\isolated-profile\\Documents"; break;
        case 26: suffix = L"\\isolated-profile\\AppData\\Roaming"; break;
        case 28: suffix = L"\\isolated-profile\\AppData\\Local"; break;
        case 40: suffix = L"\\isolated-profile"; break;
        default: return E_ACCESSDENIED;
    }
    wchar_t root[MAX_PATH] = {};
    HMODULE self = nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
            reinterpret_cast<LPCWSTR>(&IsolatedFolderPathA), &self) ||
        !GetModuleFileNameW(self, root, MAX_PATH)) return E_FAIL;
    wchar_t* last = wcsrchr(root, L'\\');
    if (!last) return E_FAIL;
    *last = 0;
    if (wcscat_s(root, suffix)) return E_FAIL;
    BOOL substituted = FALSE;
    if (!WideCharToMultiByte(CP_ACP, WC_NO_BEST_FIT_CHARS, root, -1, out, MAX_PATH, nullptr, &substituted) || substituted) {
        *out = 0;
        return E_FAIL;
    }
    return S_OK;
}
