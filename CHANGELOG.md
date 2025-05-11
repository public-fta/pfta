# Changelog


## [Unreleased]

- Fixed AND/OR gate corner imperfection due to SVG paths not being closed
- Fixed minor coding style violations (including W605 invalid escape sequence `\#`)
- Fixed typos in maths
- Fixed typos in docs and improved clarity


## [v0.3.0] Proper NULL gates (2025-05-11)

- Implemented actual `NULL` gate (rather than have them be a visual form of a single-input OR/AND gate)
- Removed unused import `Iterable` in `common.py`
- Changed `<int>` to `<integer>` in documentation for consistency


## [v0.2.0] First reasonable (2025-05-10)

- Implemented VOTE gates
- Removed model type `Undeveloped`
- Added model types `True` and `False` (which trigger cut set simplification)
- Added event property `appearance: Basic | Undeveloped | House`
- Changed `E[q]`, `E[ω]` to sample size tooltip
- Made single-input gates show as null gates
- Improved graphics sizes


## [v0.1.0] First unstable (2025-05-09)

- First reasonably working version. Vote gates yet to be implemented.


[Unreleased]: https://github.com/public-fta/pfta/compare/v0.3.0...HEAD
[v0.3.0]: https://github.com/public-fta/pfta/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/public-fta/pfta/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/public-fta/pfta/releases/tag/v0.1.0
