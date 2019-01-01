Bluetooth Cube
===

A GiiKER-compatible cube timer for Android. Requires a bluetooth-enabled cube.

Built with Python3.7.

### Linux

To run locally on a Linux machine, use `python3 -m main`.

### Android

To build for Android an deploy to a device via adb, use `buildozer android debug deploy run`.

Make sure your device is connected with `buildozer android adb -- devices` or `buildozer android adb --  connect [...]`.

`buildozer android logcat` is useful for browsing python logs from the device.
