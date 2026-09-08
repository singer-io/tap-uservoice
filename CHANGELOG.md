# Changelog

## 1.1.1
  * Bump requests to 2.34.2 [#18](https://github.com/singer-io/tap-uservoice/pull/18)

## 1.1.0
  * Updated python version. [#15](https://github.com/singer-io/tap-uservoice/pull/15)
  * Added integration tests.
  * Removed `pytz` dependency, replaced with stdlib `datetime.timezone`. [#16](https://github.com/singer-io/tap-uservoice/pull/16)
  * Improved exception handling with structured error hierarchy.
  * Refactored `main()` to use single `singer.utils.parse_args()` pattern.

## 1.0.5
  * Bump dependencies [#14](https://github.com/singer-io/tap-uservoice/pull/14)

## 1.0.4
  * Dependabot update [#8](https://github.com/singer-io/tap-uservoice/pull/8)

## 1.0.3
  * Fix properties on external_users stream

## 1.0.2
  * Update version of `requests` to `2.20.0` in response to CVE 2018-18074

## 1.0.1
  * Adding "null" to acceptable types for `body` field in `suggestions` stream [#3](https://github.com/singer-io/tap-uservoice/pull/3)

## 1.0.0
  * Releasing

## 0.1.1
  * Rename `client_id` to `api_key` and `client_secret` to `api_secret`

## 0.1.0
  * Add features and external_users streams

## 0.0.5
  * Remove features and external_users streams
  * Fix users and suggestions schemas
  * Add circleci
