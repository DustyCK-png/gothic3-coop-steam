$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
if((Test-Path vendor/g3-together) -or (Test-Path vendor/gothic3sdk)){throw 'Vendor paths already exist; use a fresh checkout'}
git clone https://github.com/GGM1k3y23/g3-together.git vendor/g3-together
if($LASTEXITCODE){throw 'Mod clone failed'}
git -C vendor/g3-together checkout 61b230a0f6b3cd005d47bbf72a9a5cc690c88dd9
if($LASTEXITCODE){throw 'Mod checkout failed'}
git -C vendor/g3-together apply ../../patches/g3-together-ru-qa.patch
if($LASTEXITCODE){throw 'Patch failed'}
git clone https://github.com/georgeto/gothic3sdk.git vendor/gothic3sdk
if($LASTEXITCODE){throw 'SDK clone failed'}
git -C vendor/gothic3sdk checkout 90bfd344de4510dda7ac9da7461cc7f1eac911f7
if($LASTEXITCODE){throw 'SDK checkout failed'}
