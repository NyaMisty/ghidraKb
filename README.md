# GhidraKb

## TL;DR

Find the merged kbxml at kbxml_merge/finalKb.kbxml

## Why this tool?

### The Problem

There are multiple existing Ghidra keybinding kbxml tuned to IDA-like shortcut keys:

- https://raw.githubusercontent.com/nullteilerfrei/reversing-class/master/ghIDA.kbxml (20210721)
- https://raw.githubusercontent.com/katechondic/Ghidra-Win-Keybinds/main/keybindings_windows.kbxml (20221121)
- https://raw.githubusercontent.com/enovella/ida2ghidra-kb/master/keybindings.kbxml (20190408)
- https://raw.githubusercontent.com/JeremyBlackthorne/Ghidra-Keybindings/master/Partial%20IDA%20Pro%20Keybindings.csv.kbxml (20190416)

But there are many problems:

- Outdated: Many of them are created at 2019-2021, where Ghidra are still in 9.X - 10.0. Since then Ghidra have evolved a lot.
- Confusing Meta & Ctrl: 
    - Many default Ghidra keybinding are designed to use with Meta key, while on Windows the Java Meta key are Windows key, so these kbxml are replacing lots of Meta into Ctrl
    - Resulting in incompatibility & confusion between Windows and Mac, and lots of extra conflicts when merging these kbxml.

### How This Tool Work

The script will does these things:

1. Parse Java KeyStroke object stored in the kbxml & Convert them into shortcut strings like Ctrl+XXX
2. Filters options that are not present in current Ghidra build.
3. Canonicalize Meta & Ctrl into Meta, avoid useless conflict.
4. Merge all kbxml based on default kbxml, Checking conflict
5. Resolve conflict & Generate final kbxml

## Using This Tool

### 1. Get Default Keybinding

- Default Key Bindings: 
    - Export Key Binding options in Ghidra's Tool Options
    - Copy kbxml to `defaults/ghidra_default_10.X.X.kbxml`

- All Configurable Keys: Many not configured keybinding options are not exported to kbxml, we have to grab them from Ghidra
    - Run ghidra_script/dump_all_kb.py in Ghidra's Script. 
    - Copy output to `defaults/ghidra_default_10.X.X.json`

### 2. Merge KeyBindings

- `cd kbxml_merge` and run `python3 ../kbtool/merge_kb.py`
- Copy contents starting from `Conflicting:` to a text file called conflict
- The script will show the conflicting key bindings defined in different file like this:
    ```
    Conflicting: Bookmarks (Shared)
         nullteilerfrei.kbxml SHIFT_MASK+VK_F9
         katechondic.kbxml CTRL_MASK+VK_B
         default None
    ```
- You can do these actions to resolve conflict:
    - Leave it alone: then the script will simply not clear this keybinding option.
    - Add plus mark `+` before the kbxml file name: Use the corresponding kbxml's keybinding as final one.
        ```
        Conflicting: Bookmarks (Shared)
             +nullteilerfrei.kbxml SHIFT_MASK+VK_F9
             katechondic.kbxml CTRL_MASK+VK_B
             default None
        ```
- After resolving, run command again with conflict resolving file: `python3 ../kbtool/merge_kb.py conflict`
  - The final merged kbxml will be outputted

