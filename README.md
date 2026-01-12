```
          
█████   ███   █████ █████ █████ ███████████ ███████████
░░███   ░███  ░░███ ░░███ ░░███ ░░███░░░░░░█░░███░░░░░░█
 ░███   ░███   ░███  ░░███ ███   ░███   █ ░  ░███   █ ░ 
 ░███   ░███   ░███   ░░█████    ░███████    ░███████   
 ░░███  █████  ███     ░░███     ░███░░░█    ░███░░░█   
  ░░░█████░█████░       ░███     ░███  ░     ░███  ░    
    ░░███ ░░███         █████    █████       █████      
     ░░░   ░░░         ░░░░░    ░░░░░       ░░░░░           
          
            ** Watch Your Files Fool **
```

# WYFF – Watch Your Files Fool

WYFF is a small Python-based file integrity monitoring tool.  
It creates a baseline of a directory and later checks if files have been added, removed, or modified.

This project was created as part of a programming assignment with focus on cybersecurity. 

## Usage

Create a baseline:
```text
wyff baseline /path/to/directory
```

Check the directory against the baseline:
```text 
wyff check /path/to/directory
```

Use a custom baseline file:
```text
wyff baseline /path/to/directory --baseline-file mybaseline.json
wyff check /path/to/directory --baseline-file mybaseline.json
```
## How it works

[1] WYFF walks through the target directory recursively.

[2] Each file is hashed using SHA-256.

[3] File paths (relative to the root directory) are stored together with their hash values.

[4] When running check, the current state is compared to the stored baseline.

[5] The result shows added, removed, and changed files.

## Design decisions

[*] Relative paths are used so baselines can be moved between systems.

[*] Files are read in chunks to handle large files efficiently.

[*] The tool is intentionally simple and focused on one task.

[*] Output is text-based to keep dependencies minimal.

## Pre-flight checks

Before the main logic is executed, WYFF performs a number of basic checks to ensure that the environment is valid.  
If any of these checks fail, the program exits gracefully with an error message.

The following checks are performed:

[*] WYFF verifies that it is running on a Linux system.

[*] The script checks that the user has read permission for the target directory.

[*] The target path is verified to be an existing directory.

All failures are logged and handled without crashing the program.


## Known limitations

  At the moment, the tool does not verify that the baseline belongs to the same directory that is being checked.

  Large directories can produce a lot of terminal output.

## Future improvements

[*] Verify that the baseline root matches the directory being checked.

[*] Change default baseline location to a fixed directory in the user’s home folder.

[*] Add exit codes for easier automation.

[*] Optional colored output for better readability.

[*] Package the tool for pip installation.
