# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2020-04-20
### Added
- Iterator utilities: `Range` and `MapList`.
- Stateful process pool: `PoolState` and related stuff.
- `iter` method for `ProgressBarManager.Proxy` to create progress bar wrapping an iterable.
- `map_reduce` example showcasing the stateful pool.

### Changed
- Signature of `chunk` changed from `chunk(iterable, n)` to `chunk(n, iterable)`.
- `FileProgress` renamed to `progress_open`; also redesigned implementation to accurately measure progress, and support
  reading binary files.
- Argument `buf_size` of `reverse_open` renamed to `buffer_size`; default value changed from 8192 to
  `io.DEFAULT_BUFFER_SIZE`.
- Update `mypy` version to 0.770; specify error code for all `# type: ignore` comments.
- All functions that accepts `str` paths now also accepts `pathlib.Path`.
- Support negative indices in `LazyList`; argument `iterator` renamed to `iterable`.
- The dummy pool instance returned by `safe_pool` when `processes == 0` now supports `map_async`, `apply`,
  `apply_async`, `starmap`, and `starmap_async`.
- Arguments `state_class` and `init_args` added to `safe_pool` to accommodate stateful pools.
- The `n` argument of `ProgressBarManager.Proxy.update` now has a default value of 0, useful for only changeing the
  postfix.
- Argument `msg` of `work_in_progress` renamed to `desc`; added default value of `"Work in progress"`.

## [0.1] - 2020-04-14
### Added
- Exception handling utilities: `register_ipython_excepthook`, `log_exception`, `exception_wrapper`.
- File system utilities: `get_folder_size`, `readable_size`, `get_file_lines`, `remove_prefix`, `copy_tree`, `cache`.
- I/O utilities: `shut_up`, `FileProgress`, `reverse_open`.
- Iterator utilities: `chunk`, `drop_until`, `split_by`, `scanl`, `scanr`, `LazyList`.
- Global logging utilities.
- Math functions: `ceil_div`.
- Multi-processing utilities: `get_worker_id`, `safe_pool`, `MultiprocessingFileWriter`, `kill_proc_tree`,
  `ProgressBarManager`.
- Process management utilities: `run_command`, `error_wrapper`.
- Structure transformation & traversal utilities: `reverse_map`, `map_structure`, `map_structure_zip`.
- Timing utilities: `work_in_progress`.
- Convenient types: `MaybeTuple`, `MaybeList`, `MaybeSeq`, `MaybeDict`, `PathType`.

[Unreleased]: https://github.com/huzecong/flutes/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/huzecong/flutes/compare/v0.1...v0.2.0
[0.1]: https://github.com/huzecong/flutes/releases/tag/v0.1
