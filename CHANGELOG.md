# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Upcoming changes...

## [0.3.0] - 2025-10-24
### Added
- CLI arguments support: `--api-url`, `--api-key`, `--proxy`, `--pac`, `--ca-cert`, `--output`, `--debug`, `--ignore-cert-errors`, `--rest`
- Support for custom output path for scan results
- Improved logging with configurable debug mode
- Sensitive information sanitization in command logging
- Click library for enhanced CLI experience

### Changed
- Refactored from argparse to click for better CLI argument handling
- Consolidated utility functions into main module (removed utils.py)
- Enhanced error handling and user feedback
- Updated GitHub Actions workflows to use `--help` instead of `--version`

### Fixed
- Pre-commit hook behavior when committing files with no matches
- Release workflow improvements

## [0.2.0] - 2025-03-21
### Added
- Added version details
- Updated documentation
- Added GitHub Actions

## [0.1.0] - 2025-03-19
### Added
- Renamed entry points
- Cleaned up settings detection
- Added makefile shortcuts

[0.1.0]: https://github.com/scanoss/pre-commit-hooks/compare/v0.0.1...v0.1.0
[0.2.0]: https://github.com/scanoss/pre-commit-hooks/compare/v0.1.0...v0.2.0
[0.3.0]: https://github.com/scanoss/pre-commit-hooks/compare/v0.2.0...v0.3.0
