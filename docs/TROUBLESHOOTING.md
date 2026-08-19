# Troubleshooting and Developer Checks

## Complete local quality gate

Activate the project environment and run:

```powershell
python scripts/check.py
```

This checks formatting, lint rules, docstrings, static types, all tests, branch
coverage, and the configured coverage threshold. Add the network-backed dependency
audit when internet access is available:

```powershell
python scripts/check.py --audit
```

Run the same command before every commit. GitHub Actions repeats it on Python 3.11
and 3.14 for pushes to `main` and for pull requests.

## PowerShell blocks environment activation

Activation is convenient but optional. Every command can use the interpreter path:

```powershell
.\.venv\Scripts\python.exe scripts/check.py
```

Do not weaken the machine execution policy solely for this project.

## Processed data is not available

From the repository root:

```powershell
babynames-validate
babynames-build
```

If the virtual environment is not activated, use the executables under
`.venv\Scripts\`. Never edit `data/processed/manifest.json` manually; rebuild it.

## Streamlit does not open a browser

Run the application and open the printed local URL manually, normally
`http://localhost:8501`:

```powershell
streamlit run src/babynames/app.py
```

If the port is occupied, Streamlit selects another port and prints it.

## Logging

Set `BABYNAMES_LOG_LEVEL` to `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` before
launching the app. Invalid values safely fall back to `INFO` and produce a warning.
Do not log credentials, tokens, personal information, or complete environment dumps.

## Dependency audit fails

First determine whether the failure is a network/index problem or a reported
vulnerability. Network failures can be retried. A vulnerability must be reviewed,
updated, mitigated, or explicitly documented before release; do not blindly ignore
the advisory.
