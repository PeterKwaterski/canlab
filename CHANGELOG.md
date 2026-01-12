# Changelog

All notable changes to this project will be documented in this file.

## [0.1.3] - 2026-01-12

### Added
- Support for Multiplexed Siganls
- Decoding and Encoding multiplexed signals
- Decoding and Encoding for entire messages
- Support for encoding frames with LSB AND MSB signals

### Bug Fixes
- Issues importing from PyPi
- Failing to parse signals with multiplex signatures

### Documentation
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

## [0.1.0] - 2026-01-11

### Added
- Initial beta release
- DBC file loading and parsing
- CAN frame encoding (LSB and MSB formats)
- CAN frame decoding (LSB and MSB formats)
- ASC log file parsing
- ID conversion utilities (DBC ID ↔ Bus ID)
- Basic test suite
