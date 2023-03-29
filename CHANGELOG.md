# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-03-29

### Added
- Added an optional maximum elapsed time for retries.
- Support for custom backoff strategy for the delay between retries.
- Added `resilient_call` alias for `resilient_call`
  
### Changed
- Renamed `conditions` and `conditions_criteria` to `conditions` and `conditions_criteria` for better clarity.
- Updated the wrapper to support both asynchronous and non-asynchronous functions.
- If 2 arguments are passed to the action, the number of tries will be passed as well.

## [0.1.1] - 2023-03-23

### Changed
- Introduced the ability to use `RETRY_EVENT` directly as an exception or conditions value, eliminating the need to create a separate function for this purpose.
- Updated existing usage examples to showcase this new functionality and to align with the latest improvements.
- Added a new example (Example 7) to further demonstrate the flexibility and power of the Resilient Caller module.

## [0.1.0] - 2023-03-22

### Added
- Initial release of the Resilient Caller project.
- Comprehensive documentation, including usage examples and explanations.
- First version of the Resilient Caller module, implementing the `send_requests` functionality.
- A variety of example use cases to demonstrate the module's capabilities.