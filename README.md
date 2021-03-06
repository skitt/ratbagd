ratbagd
=======

ratbagd is a system daemon to introspect and modify configurable mice.

ratbagd uses libratbag to access mice and exports the features over a DBus
API to unprivileged proceses. ratbagd needs permissions to access device
nodes (primarily /dev/hidraw nodes) and usually needs to run as root.

ratbagd is a relatively thin wrapper arond libratbag. If a device is not
detected or does not function as expected, the issue is usually in
libratbag. libratbag can be found at
   https://github.com/libratbag/libratbag

The DBus-Interface
------------------

Note: **the DBus interface is subject to change**

Interfaces:
-  org.freedesktop.ratbag1.Manager
-  org.freedesktop.ratbag1.Device
-  org.freedesktop.ratbag1.Profile
-  org.freedesktop.ratbag1.Resolution
-  org.freedesktop.ratbag1.Button

The **org.freedesktop.ratbag1.Manager** interface provides:
- Properties:
  - Devices -> array of object paths with interface Device
- Signals:
  - DeviceNew -> new device available, carries object path
  - DeviceRemoved -> device removed, carries object path

The **org.freedesktop.ratbag1.Device** interface provides:
- Properties:
  - Id -> unique ID of this device
  - Capabilities -> array of uints with the capabilities enum from libratbag
  - Description -> device name
  - Svg -> device SVG name (file only)
  - SvgPath -> device SVG name (full absolute path)
  - Profiles -> array of object paths with interface Profile
  - ActiveProfile -> index of the currently active profile in Profiles
- Methods:
  - GetProfileByIndex(uint) -> returns the object path for the given index

The **org.freedesktop.ratbag1.Profile** interface provides:
- Properties:
  - Index -> index of the profile
  - Resolutions -> array of object paths with interface Resolution
  - Buttons -> array of object paths with interface Button
  - ActiveResolution -> index of the currently active resolution in Resolutions
  - DefaultResolution -> index of the default resolution in Resolutions
- Methods:
  - SetActive(void) -> set this profile to be the active profile
  - GetResolutionByIndex(uint) -> returns the object path for the given index

The **org.freedesktop.ratbag1.Resolution** interface provides:
- Properties:
  - Index -> index of the resolution
  - Capabilities -> array of uints with the capabilities enum from libratbag
  - XResolution -> uint for the x resolution assigned to this entry
  - YResolution -> uint for the y resolution assigned to this entry
  - ReportRate -> uint for the report rate in Hz assigned to this entry
- Methods:
  - SetResolution(uint, uint) -> x/y resolution to assign
  - SetReportRate(uint) -> uint for the report rate to assign

The **org.freedesktop.ratbag1.Button** interface provides:
- Properties:
  - Index -> index of the button
  - Type -> string describing the button type
  - ButtonMapping -> uint of the current button mapping (if mapping to button)
  - SpecialMapping -> string of the current special mapping (if mapped to special)
  - KeyMapping -> array of uints, first entry is the keycode, other entries, if any, are modifiers (if mapped to key)
  - ActionType -> string describing the action type of the button ("none", "button", "key", "special", "macro", "unknown"). This decides which *Mapping  property has a value
  - ActionTypes -> array of strings, possible values for ActionType
- Methods:
  - SetButtonMapping(uint) -> set the button mapping to the given button
  - SetSpecialMapping(string) -> set the button mapping to the given special entry
  - SetKeyMapping(uint[]) -> set the key mapping, first entry is the keycode, other entries, if any, are modifier keycodes
  - Disable(void) -> disable this button

For easier debugging, objects paths are constructed from the device. e.g.
`/org/freedesktop/ratbag/button/event5/p0/b10` is the button interface for
button 10 on profile 0 on event5. The naming is subject to change. Do not
rely on a constructed object path in your application.

Running ratbagd
---------------

ratbagd is intended to run as dbus-activated systemd service. This requires
installation of the following files:

    sudo cp dbus/org.freedesktop.ratbag1.conf /etc/dbus-1/system.d/org.freedesktop.ratbag1.conf
    sudo cp dbus/org.freedesktop.ratbag1.service /etc/dbus-1/systemd-services/org.freedesktop.ratbag1.conf
    sudo cp ratbagd.service /etc/systemd/system/ratbagd.service

The files are installed into the prefix by make install, see also the
configure switches ---with-systemd-unit-dir and --with-dbus-root-dir.
Developers are encouraged to simply symlink to the files in the git
repository.

For the files to take effect, you should run
    sudo systemctl daemon-reload
    sudo systemctl reload dbus.service

And finally, to enable the service:
    sudo systemctl enable ratbagd.service

This places the required symlink into the systemd directory so that dbus
activation is possible.

Compiling ratbagd
-----------------

ratbagd needs systemd >= 227. If you are running Fedora 23, you might find the
following instruction valuable:

Download systemd v229 (master caused troubles with gcrypt and gpg-error last
time I tried).

    $ git clone --branch v229 https://github.com/systemd/systemd


Configure it with:

    $ ./autogen.sh && ./configure --prefix=/opt/systemd \
                                  --libdir=/opt/systemd/lib \
                                  --disable-gcrypt \
                                  --without-bashcompletiondir \
                                  --with-rootprefix=/opt/systemd \
                                  --with-sysvinit-path=/opt/systemd/etc \
                                  --with-sysvrcnd-path=/opt/systemd/etc/rc.d

Then run make and make install.

In ratbagd, you will need to add the newly installed libsystemd in the
pkg_config path:

    $ PKG_CONFIG_PATH=/opt/systemd/lib/pkgconfig ./configure

License
-------

ratbagd is licensed under the MIT license.

> Permission is hereby granted, free of charge, to any person obtaining a
> copy of this software and associated documentation files (the "Software"),
> to deal in the Software without restriction, including without limitation
> the rights to use, copy, modify, merge, publish, distribute, sublicense,
> and/or sell copies of the Software, and to permit persons to whom the
> Software is furnished to do so, subject to the following conditions: [...]
