# Application Architecture

The Streamlit application is intentionally a thin presentation layer over tested
data and analytical services. Page code must not read raw files or redefine metrics.

## Runtime flow

1. `babynames.app` loads `ProjectSettings`.
2. `inspect_processed_artifacts` checks the manifest, Parquet filename, and byte size.
3. Missing or inconsistent artifacts produce user-safe build guidance.
4. `load_analytics` loads the Parquet dataset through Streamlit's resource cache.
5. The dataset path, modification timestamp, and size form the cache key, so a new
   pipeline build invalidates stale analytics.
6. Streamlit navigation runs a page renderer with the loaded domain service.

Unexpected load failures are logged for developers while users receive a concise
recovery message. Credentials and internal exception details are never rendered.
Logging is configured centrally through `logging_config.py`; the optional
`BABYNAMES_LOG_LEVEL` variable controls verbosity without changing application code.

## Module boundaries

| Module | Responsibility |
|---|---|
| `settings.py` | Resolve project and processed-data locations |
| `artifacts.py` | Perform inexpensive startup artifact health checks |
| `data_pipeline.py` | Build traceable processed artifacts from validated raw files |
| `analytics.py` | Own every analytical definition and query |
| `ui/data_access.py` | Cache the analytics service across Streamlit reruns |
| `ui/pages.py` | Render page content using public domain methods |
| `app.py` | Configure Streamlit, handle startup, and define navigation |
| `logging_config.py` | Validate and apply consistent local diagnostic logging |

## Navigation

The application has explicit, stable URL paths:

- `/overview`
- `/names`
- `/compare`
- `/trends`
- `/about`

All routes contain working content. Page renderers obtain calculations through the
analytics service and use shared Altair builders for consistent axes, tooltips,
category labels, and rank direction.

## Configuration

The default processed-data directory is `data/processed/`. Tests and advanced local
setups can override it with `BABYNAMES_PROCESSED_DIR`. This variable changes only the
generated-artifact location; it never changes the committed raw-data boundary.

Visual defaults live in `.streamlit/config.toml`. The application uses a wide layout,
an accessible light palette, and disabled telemetry. Page-specific styling should
prefer Streamlit theme values over fragile HTML selectors.

## Startup recovery

From the repository root, the standard recovery sequence is:

```powershell
babynames-validate
babynames-build
streamlit run src/babynames/app.py
```

The first two commands fail with nonzero exit codes when their contracts are not met.
The application never silently rebuilds data during a page rerun.
