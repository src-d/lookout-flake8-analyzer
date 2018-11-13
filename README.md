# [![Build Status](https://travis-ci.org/src-d/lookout-flake8-analyzer.svg)](https://travis-ci.org/src-d/lookout-flake8-analyzer) lookout analyzer: sonarcheck

A [lookout](https://github.com/src-d/lookout/) analyzer implementation that uses the flake8 meta linter for Python code.

_Disclaimer: this is not an official product, it only serves the purpose of testing lookout._


# Example of utilization

With `lookout-sdk` binary from the latest release of [SDK](https://github.com/src-d/lookout/releases):

```
$ python3 flake8_analyzer.py

$ lookout-sdk review -v ipv4://localhost:2001 \
    --from c99dcdff172f1cb5505603a45d054998cb4dd606 \
    --to 3a9d78bdd1139c929903885ecb8f811931b8aa70
```


# Configuration

| Variable | Default | Description |
| -- | -- | -- |
| `FLAKE8_HOST` | `0.0.0.0` | IP address to bind the gRPC serve |
| `FLAKE8_PORT` | `2002` | Port to bind the gRPC server |
| `FLAKE8_DATA_SERVICE_URL` | `ipv4://localhost:10301` | gRPC URL of the [Data service](https://github.com/src-d/lookout/tree/master/docs#components)
| `FLAKE8_LOG_LEVEL` | `info` | Logging level (info, debug, warning or error) |

# Development
## Release

Main release artifact is a Docker image, so
 
  - `make docker-push`


# License

[AGPLv3](./LICENSE)
