#!/usr/bin/env python
#
# vim: set expandtab shiftwidth=4 tabstop=4:
#
# This file is part of ratbagd.
#
# Copyright 2016 Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice (including the next
# paragraph) shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import print_function

from ratbagd import *

import sys
import argparse

def list_devices(r, args):
    for d in r.devices:
        print("{:10s} {:32s}".format(d.id + ":", d.name))

def find_device(r, args):
    dev = None
    for d in r.devices:
        if d.id == args.device:
            dev = d
            break;
    if dev is None:
        print("Unable to find device {}".format(args.device))
        sys.exit(1)
    return dev

def find_profile(r, args):
    d = find_device(r, args)
    try:
        p = d.profiles[args.profile]
    except IndexError:
        print("Invalid profile index {}".format(args.profile))
        sys.exit(1)
    return p, d

def find_resolution(r, args):
    p, d = find_profile(r, args)
    try:
        r = p.resolutions[args.resolution]
    except IndexError:
        print("Invalid resolution index {}".format(args.resolution))
        sys.exit(1)
    return r, p, d

def find_button(r, args):
    p, d = find_profile(r, args)
    try:
        b = p.buttons[args.button]
    except IndexError:
        print("Invalid button index {}".format(args.button))
        sys.exit(1)
    return b, p, d

def show_device(r, args):
    d = find_device(r, args)


    caps = { RatbagdDevice.CAP_SWITCHABLE_RESOLUTION : "switchable-resolution",
             RatbagdDevice.CAP_SWITCHABLE_PROFILE : "switchable-profile",
             RatbagdDevice.CAP_BUTTON_KEY : "button-keys",
             RatbagdDevice.CAP_BUTTON_MACROS : "button-macros",
             RatbagdDevice.CAP_DEFAULT_PROFILE : "default-profile" }
    capabilities = [caps[c] for c in d.capabilities]

    print("{} - {}".format(d.id, d.name))
    print("               SVG: {}".format(d.svg))
    print("      Capabilities: {}".format(", ".join(capabilities)))
    print("Number of Profiles: {}".format(len(d.profiles)))
    active = -1
    for i, p in enumerate(d.profiles):
        if p == d.active_profile:
            active = i
            break
    print("    Active Profile: {}".format(active))

def show_profile(r, args):
    p, d = find_profile(r, args)

    print("Profile {} on {} ({})".format(args.profile, d.id, d.name))
    print("    Number of Buttons: {}".format(len(p.buttons)))
    print("Number of Resolutions: {}".format(len(p.resolutions)))
    active, default = -1, -1
    for i, r in enumerate(p.resolutions):
        if p.active_resolution == r:
            active = i
        if p.default_resolution == r:
            default = i

    print("    Active Resolution: {}".format(active))
    print("   Default Resolution: {}".format(default))

def show_resolution(r, args):
    r, p, d = find_resolution(r, args)

    print("Resolution {} on Profile {} on {} ({})".format(args.resolution,
                                                          args.profile,
                                                          d.id,
                                                          d.name))
    print("   Report Rate: {}Hz".format(r.report_rate))
    if RatbagdResolution.CAP_SEPARATE_XY_RESOLUTION in r.capabilities:
        print("    Resolution: {}x{}dpi".format(*r.resolution))
    else:
        print("    Resolution: {}dpi".format(r.resolution[0]))


    caps = { RatbagdResolution.CAP_INDIVIDUAL_REPORT_RATE : "individual-report-rate",
             RatbagdResolution.CAP_SEPARATE_XY_RESOLUTION : "separate-xy-resolution" }
    capabilities = [caps[c] for c in r.capabilities]
    print("  Capabilities: {}".format(", ".join(capabilities)))

def show_button(r, args):
    b, p, d = find_button(r, args)

    print("Button {} on Profile {} on {} ({})".format(args.button,
                                                      args.profile,
                                                      d.id,
                                                      d.name))

    print("           Type: {}".format(b.button_type))
    print("    Action Type: {}".format(b.action_type))

    if b.action_type == "button":
        print(" Button Mapping: {}".format(b.button))
    elif b.action_type == "key":
        print("    Key Mapping: {}".format(b.key))
    elif b.action_type == "special":
        print("Special Mapping: {}".format(b.special))

def make_parser():
    parser = argparse.ArgumentParser(description="Inspect and modify configurable mice")
    parser.add_argument("-V", "--version", action="version", version="__VERSION__")
    subs = parser.add_subparsers(title="COMMANDS", help=None)

    list = subs.add_parser("list-devices", help="List available configurable mice")
    list.set_defaults(func=list_devices)

    show = subs.add_parser("show-device", help="Show device information")
    show.add_argument("device", metavar="event0", help="The device node")
    show.set_defaults(func=show_device)

    profile = subs.add_parser("show-profile", help="Show profile information")
    profile.add_argument("device", metavar="event0", help="The device node")
    profile.add_argument("profile", metavar="0", help="The profile index", type=int)
    profile.set_defaults(func=show_profile)

    resolution = subs.add_parser("show-resolution", help="Show resolution information")
    resolution.add_argument("device", metavar="event0", help="The device node")
    resolution.add_argument("profile", metavar="0", help="The profile index", type=int)
    resolution.add_argument("resolution", metavar="0", help="The resolution index", type=int)
    resolution.set_defaults(func=show_resolution)

    button = subs.add_parser("show-button", help="Show button information")
    button.add_argument("device", metavar="event0", help="The device node")
    button.add_argument("profile", metavar="0", help="The profile index", type=int)
    button.add_argument("button", metavar="0", help="The button index", type=int)
    button.set_defaults(func=show_button)

    return parser

def main(argv):
    cmd = make_parser().parse_args(argv)

    try:
        r = Ratbagd()
        if not r.devices:
            print("No devices available.")
    except RatbagdDBusUnavailable:
        print("Unable to connect to ratbagd over dbus")

    cmd.func(r, cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
