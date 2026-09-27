# Installing ToDoList (v9.x) on Ubuntu Linux 

TDL can be run on Linux systems using WINE.
This guide was tested on Kubuntu 25 with Wine 10.0 and ToDoList 9.0.10. It should apply to any Ubuntu-based Linux system.
Use this guide instead of `Install.Linux.txt` of this repository for newer Ubuntu-based Linux systems.

---

## IMPORTANT NOTES

1. Use a dedicated 32-bit WINEPREFIX for ToDoList (see below).  
   Do **NOT** use your default `~/.wine` prefix.

2. Do **NOT** install `comctl32` via winetricks.  
   Wine 5.0+ already includes the required comctl32 v6.0 built-in.  
   Installing it via winetricks will replace it with the older v5.8  
   and cause ToDoList to crash on startup with:  
   `comctl32.dll.HIMAGELIST_QueryInterface, aborting`

3. ToDoList 9.x requires .NET Framework 4.6.2 to open task files.  
   Without it, the application starts but crashes when opening a `.tdl` file.

---

## Step 1 — Install required packages

On Debian/Ubuntu-based systems:

```bash
sudo apt install wine winetricks cabextract
```

## Step 2 — Download ToDoList

Download the latest release zip from GitHub:
https://github.com/abstractspoon/ToDoList_Downloads/releases/latest

Unzip it to a folder of your choice, e.g.:

```bash
mkdir -p ~/WineApps/ToDoList
unzip todolist_exe.zip -d ~/WineApps/ToDoList
```

## Step 3 — Create a dedicated 32-bit Wine prefix

```
WINEPREFIX=~/.wine/todolist WINEARCH=win32 wineboot
```

## Step 4 — Install required Windows libraries

Install `mfc42`:

```bash
WINEPREFIX=~/.wine/todolist winetricks mfc42
```

Install .NET Framework 4.6.2:

```bash
WINEPREFIX=~/.wine/todolist winetricks dotnet462
```

## Step 5 — Run ToDoList

```bash
WINEPREFIX=~/.wine/todolist wine ~/WineApps/ToDoList/ToDoList.exe
```

## Step 6 — Create a desktop/menu launcher (optional)

Create the file `~/.local/share/applications/todolist.desktop` with the following content (replace YOUR_USERNAME with your username):

```desktop
[Desktop Entry]
Name=ToDoList
Exec=env WINEPREFIX=/home/YOUR_USERNAME/.wine/todolist wine /home/YOUR_USERNAME/WineApps/ToDoList/ToDoList.exe
Type=Application
Categories=Office;
Icon=wine
Terminal=false
```

After saving, ToDoList will appear in your application menu.
