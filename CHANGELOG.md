## 7.1.0 (2025-10-21)


### Added

- Add leakage detection config (#41).

## 7.0.0 (2025-10-03)


### Added

- SeleneConfig and SelenePlusConfig.
- `auto` computational backend for MatrixProductState simulator.

## 6.0.0 (2025-09-29)

### Removed

- Projectq support


## 5.1.0 (2025-08-13)


### Added

- Restore noisy sim by default (#35).

## 5.0.0 (2025-08-12)


### Added

- Refactor selene emulator configs, replacing them with BasicEmulatorConfig and StandardEmulatorConfig.


## 4.0.0 (2025-07-08)


### Fixed

- Update ibmqconfig to match new instance format.

## 3.2.6 (2025-06-25)

### Fixed

- Add BaseModel to deal with enums


## 3.2.5 (2025-06-25)


### Fixed

- Add default value for qconfig target_2qb_gate (#28).

## 3.2.4 (2025-06-24)

### Fixed

- Add missing kwargs to various BackendConfig models

## 3.2.3 (2025-06-02)


### Fixed

- Correct the capitalization of CoinFlip to Coinflip for consistency with the selene approach (#24).

## 3.2.2 (2025-05-23)


### Fixed

- Restore `config_name_to_class` function.

## 3.2.1 (2025-05-22)

### Fixed

- Selene BackendConfig deserialization discrimination.

## 3.2.0 (2025-05-16)


### Added

- Selene configurations for Nexus.

## 3.1.1 (2025-05-08)

- Remove unused arguments on QuantinuumConfig


## 3.1.0 (2025-05-06)


### Added

- Add optional `max_cost` field to QuantinuumConfig (#16).

## 3.0.1 (2025-04-10)


### Fixed

- Readd support for python 3.10 (#14).

## 3.0.0 (2025-04-09)


### Added

- Remove pytket dependency and bump to python 3.11 (#12).

## 2.1.0 (2025-03-27)


### Added

- Add configuration models for hypertket compilation options (#10).
- Add Quantinuum Systems result type (#9).

## 2.0.0 (2025-02-05)


### Changed

- `h_series_noise` module renamed to `quantinuum_systems_noise`. 


## 1.1.0 (2024-12-18)


### Added

- Handle unknown optypes in backendinfo (#3).


### Fixed

- Support valid types for compiler options (#4).


## v1.0.0 (2024-10-21)

First release.
