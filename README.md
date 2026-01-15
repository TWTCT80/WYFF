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

See it in use https://youtu.be/-sdOhxyWYxw
See my presentation: https://miro.com/welcomeonboard/ME9jaXcwSE1VaUpoWVVsUXg2SU84b25EbkorcDQ4cnhuTFZXc0JSWmNpZGJSQ1M4ZTFFM3BMN015dGJic1R3SlBDTGt3RXJXd21YNUNxWU96WDNVdlZXQldkMjYyK1I0ZGRDYkxHRGRnNm90NElIMExud0JwOXAvQnRJMUd2WFhNakdSWkpBejJWRjJhRnhhb1UwcS9BPT0hdjE=?share_link_id=662286781619

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
The logfile (wyff.log) is saved in the directory where the script is run.


## Known limitations

  At the moment, the tool does not verify that the baseline belongs to the same directory that is being checked.

  Large directories can produce a lot of terminal output.

## Future improvements

## Future improvements

- Verify that the baseline root directory matches the directory being checked, to prevent incorrect comparisons.

- Move the baseline file to a fixed or configurable location outside the monitored directory.

- Add stronger protection for the baseline file, such as restricted permissions and integrity verification.

- Introduce scheduled integrity checks for automated monitoring.

- Add notifications when changes are detected (for example via terminal output or log monitoring).

- Improve logging by using a centralized or configurable log file location.

- Add exit codes to support automation and scripting.

- Optional colored terminal output for improved readability.

- Package the tool for easier installation (e.g. via pip).

