# CTF Writeup: 奪取_白俄羅斯 - Locky Door

## Challenge Information
- **Category:** Binary (Pwn / Reverse)
- **Target File:** `bof_0e2a1d3bb4b79e55d35940334526cd39.exe`
- **Objective:** Obtain the flag to unlock the door.

## Analysis Process

Given the `bof_` prefix, the initial assumption was a Buffer Overflow vulnerability requiring exploit development. However, before launching into reverse engineering or setting up a Windows debugging environment, standard static analysis routines were executed within the WSL2 environment.

The first step was to extract printable character sequences from the executable to look for hardcoded strings, error messages, or internal function names.

```
```text?code_stdout&code_event_index=2
File created at: /mnt/data/Locky_Door_Writeup.md

```bash
strings bof_0e2a1d3bb4b79e55d35940334526cd39.exe | less
```

### Extracted Strings (Snippet)
```text
Give me the key :
Flag{Catch_Me_if_U_Can}
pause
Oh no, plz try again!!
Try me?
```

## Solution

The binary stored the flag in plaintext. By simply reading the strings embedded in the file, the flag was immediately exposed alongside the prompt messages, bypassing the need to trigger any memory corruption or craft a payload.

- **Flag:** `Flag{Catch_Me_if_U_Can}`

## Takeaway
This serves as a classic reminder of the "first rule" of binary analysis: **Always run `strings` and `file` first.** Securing the low-hanging fruit quickly preserves time and mental energy for the more complex challenges ahead.
"""

file_path = "/mnt/data/Locky_Door_Writeup.md"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"File created at: {file_path}")