#!/usr/bin/env python3

# This file is part of the Trezor project.
#
# Copyright (C) 2012-2017 Marek Palatinus <slush@satoshilabs.com>
# Copyright (C) 2012-2017 Pavol Rusnak <stick@satoshilabs.com>
# Copyright (C) 2016-2017 Jochen Hoenicke <hoenicke@gmail.com>
# Copyright (C) 2017      mruddy
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

import base64
import json
import os
import re
import sys
from decimal import Decimal

import click
import requests

from trezorlib import (
    btc,
    coins,
    debuglink,
    device,
    exceptions,
    firmware,
    log,
    messages as proto,
    misc,
    protobuf,
    tools,
    ui,
)
from trezorlib.client import TrezorClient
from trezorlib.transport import enumerate_devices, get_transport

from . import (
    binance,
    ripple,
    tezos,
    webauthn,
    stellar,
    cosi,
    monero,
    lisk,
    nem,
    cardano,
    eos,
    ethereum,
)


class ChoiceType(click.Choice):
    def __init__(self, typemap):
        super(ChoiceType, self).__init__(typemap.keys())
        self.typemap = typemap

    def convert(self, value, param, ctx):
        value = super(ChoiceType, self).convert(value, param, ctx)
        return self.typemap[value]


CHOICE_PASSPHRASE_SOURCE_TYPE = ChoiceType(
    {
        "ask": proto.PassphraseSourceType.ASK,
        "device": proto.PassphraseSourceType.DEVICE,
        "host": proto.PassphraseSourceType.HOST,
    }
)


CHOICE_DISPLAY_ROTATION_TYPE = ChoiceType(
    {"north": 0, "east": 90, "south": 180, "west": 270}
)


CHOICE_RECOVERY_DEVICE_TYPE = ChoiceType(
    {
        "scrambled": proto.RecoveryDeviceType.ScrambledWords,
        "matrix": proto.RecoveryDeviceType.Matrix,
    }
)

CHOICE_INPUT_SCRIPT_TYPE = ChoiceType(
    {
        "address": proto.InputScriptType.SPENDADDRESS,
        "segwit": proto.InputScriptType.SPENDWITNESS,
        "p2shsegwit": proto.InputScriptType.SPENDP2SHWITNESS,
    }
)

CHOICE_OUTPUT_SCRIPT_TYPE = ChoiceType(
    {
        "address": proto.OutputScriptType.PAYTOADDRESS,
        "segwit": proto.OutputScriptType.PAYTOWITNESS,
        "p2shsegwit": proto.OutputScriptType.PAYTOP2SHWITNESS,
    }
)

CHOICE_RESET_DEVICE_TYPE = ChoiceType(
    {
        "single": proto.BackupType.Bip39,
        "shamir": proto.BackupType.Slip39_Basic,
        "advanced": proto.BackupType.Slip39_Advanced,
    }
)

CHOICE_SD_PROTECT_OPERATION_TYPE = ChoiceType(
    {
        "enable": proto.SdProtectOperationType.ENABLE,
        "disable": proto.SdProtectOperationType.DISABLE,
        "refresh": proto.SdProtectOperationType.REFRESH,
    }
)


class TrezorctlGroup(click.Group):
    """Command group that handles compatibility for trezorctl.

    The purpose is twofold: convert underscores to dashes, and ensure old-style commands
    still work with new-style groups.

    Click 7.0 silently switched all underscore_commands to dash-commands.
    This implementation of `click.Group` responds to underscore_commands by invoking
    the respective dash-command.

    With trezorctl 0.11.5, we started to convert old-style long commands
    (such as "binance-sign-tx") to command groups ("binance") with subcommands
    ("sign-tx"). The `TrezorctlGroup` can perform subcommand lookup: if a command
    "binance-sign-tx" does not exist in the default group, it tries to find "sign-tx"
    subcommand of "binance" group.
    """

    def get_command(self, ctx, cmd_name):
        dashed_name = cmd_name.replace("_", "-")
        cmd = super().get_command(ctx, cmd_name)
        if cmd is None:
            # Old-style top-level commands looked like this: binance-sign-tx.
            # We are moving to 'binance' command with 'sign-tx' subcommand.
            try:
                command, subcommand = cmd_name.split("-", maxsplit=1)
                cmd = super().get_command(ctx, command)
                return cmd.get_command(ctx, subcommand)
            except Exception:
                return None
        return cmd


def configure_logging(verbose: int):
    if verbose:
        log.enable_debug_output(verbose)
        log.OMITTED_MESSAGES.add(proto.Features)


@click.command(cls=TrezorctlGroup, context_settings={"max_content_width": 400})
@click.option(
    "-p",
    "--path",
    help="Select device by specific path.",
    default=os.environ.get("TREZOR_PATH"),
)
@click.option("-v", "--verbose", count=True, help="Show communication messages.")
@click.option(
    "-j", "--json", "is_json", is_flag=True, help="Print result as JSON object"
)
@click.pass_context
def cli(ctx, path, verbose, is_json):
    configure_logging(verbose)

    def get_device():
        try:
            device = get_transport(path, prefix_search=False)
        except Exception:
            try:
                device = get_transport(path, prefix_search=True)
            except Exception:
                click.echo("Failed to find a Trezor device.")
                if path is not None:
                    click.echo("Using path: {}".format(path))
                sys.exit(1)
        return TrezorClient(transport=device, ui=ui.ClickUI())

    ctx.obj = get_device


@cli.resultcallback()
def print_result(res, path, verbose, is_json):
    if is_json:
        if isinstance(res, protobuf.MessageType):
            click.echo(json.dumps({res.__class__.__name__: res.__dict__}))
        else:
            click.echo(json.dumps(res, sort_keys=True, indent=4))
    else:
        if isinstance(res, list):
            for line in res:
                click.echo(line)
        elif isinstance(res, dict):
            for k, v in res.items():
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        click.echo("%s.%s: %s" % (k, kk, vv))
                else:
                    click.echo("%s: %s" % (k, v))
        elif isinstance(res, protobuf.MessageType):
            click.echo(protobuf.format_message(res))
        else:
            click.echo(res)


#
# Common functions
#


@cli.command(name="list", )
def ls():
    """List connected Trezor devices."""
    return enumerate_devices()


@cli.command()
def version():
    """Show version of trezorctl/trezorlib."""
    from trezorlib import __version__ as VERSION

    return VERSION


#
# Basic device functions
#


@cli.command()
@click.argument("message")
@click.option("-b", "--button-protection", is_flag=True)
@click.option("-p", "--pin-protection", is_flag=True)
@click.option("-r", "--passphrase-protection", is_flag=True)
@click.pass_obj
def ping(connect, message, button_protection, pin_protection, passphrase_protection):
    """Send ping message."""
    return connect().ping(
        message,
        button_protection=button_protection,
        pin_protection=pin_protection,
        passphrase_protection=passphrase_protection,
    )


@cli.command()
@click.pass_obj
def clear_session(connect):
    """Clear session (remove cached PIN, passphrase, etc.)."""
    return connect().clear_session()


@cli.command()
@click.argument("size", type=int)
@click.pass_obj
def get_entropy(connect, size):
    """Get example entropy."""
    return misc.get_entropy(connect(), size).hex()


@cli.command()
@click.pass_obj
def get_features(connect):
    """Retrieve device features and settings."""
    return connect().features


#
# Device management functions
#


@cli.command()
@click.option("-r", "--remove", is_flag=True)
@click.pass_obj
def change_pin(connect, remove):
    """Set, change or remove PIN."""
    return device.change_pin(connect(), remove)


@cli.command()
@click.argument("operation", type=CHOICE_SD_PROTECT_OPERATION_TYPE)
@click.pass_obj
def sd_protect(connect, operation):
    """Secure the device with SD card protection.

    When SD card protection is enabled, a randomly generated secret is stored
    on the SD card. During every PIN checking and unlocking operation this
    secret is combined with the entered PIN value to decrypt data stored on
    the device. The SD card will thus be needed every time you unlock the
    device. The options are:

    \b
    enable - Generate SD card secret and use it to protect the PIN and storage.
    disable - Remove SD card secret protection.
    refresh - Replace the current SD card secret with a new one.
    """
    if connect().features.model == "1":
        raise click.BadUsage("Trezor One does not support SD card protection.")
    return device.sd_protect(connect(), operation)


@cli.command()
@click.pass_obj
def enable_passphrase(connect):
    """Enable passphrase."""
    return device.apply_settings(connect(), use_passphrase=True)


@cli.command()
@click.pass_obj
def disable_passphrase(connect):
    """Disable passphrase."""
    return device.apply_settings(connect(), use_passphrase=False)


@cli.command()
@click.option("-l", "--label")
@click.pass_obj
def set_label(connect, label):
    """Set new device label."""
    return device.apply_settings(connect(), label=label)


@cli.command()
@click.argument("source", type=CHOICE_PASSPHRASE_SOURCE_TYPE)
@click.pass_obj
def set_passphrase_source(connect, source):
    """Set passphrase source.

    Configure how to enter passphrase on Trezor Model T. The options are:

    \b
    ask - always ask where to enter passphrase
    device - always enter passphrase on device
    host - always enter passphrase on host
    """
    return device.apply_settings(connect(), passphrase_source=source)


@cli.command()
@click.argument("rotation", type=CHOICE_DISPLAY_ROTATION_TYPE)
@click.pass_obj
def set_display_rotation(connect, rotation):
    """Set display rotation.

    Configure display rotation for Trezor Model T. The options are
    north, east, south or west.
    """
    return device.apply_settings(connect(), display_rotation=rotation)


@cli.command()
@click.argument("delay", type=str)
@click.pass_obj
def set_auto_lock_delay(connect, delay):
    """Set auto-lock delay (in seconds)."""
    value, unit = delay[:-1], delay[-1:]
    units = {"s": 1, "m": 60, "h": 3600}
    if unit in units:
        seconds = float(value) * units[unit]
    else:
        seconds = float(delay)  # assume seconds if no unit is specified
    return device.apply_settings(connect(), auto_lock_delay_ms=int(seconds * 1000))


@cli.command()
@click.argument("flags")
@click.pass_obj
def set_flags(connect, flags):
    """Set device flags."""
    flags = flags.lower()
    if flags.startswith("0b"):
        flags = int(flags, 2)
    elif flags.startswith("0x"):
        flags = int(flags, 16)
    else:
        flags = int(flags)
    return device.apply_flags(connect(), flags=flags)


@cli.command()
@click.option("-f", "--filename", default=None)
@click.pass_obj
def set_homescreen(connect, filename):
    """Set new homescreen."""
    if filename is None:
        img = b"\x00"
    elif filename.endswith(".toif"):
        img = open(filename, "rb").read()
        if img[:8] != b"TOIf\x90\x00\x90\x00":
            raise tools.CallException(
                proto.FailureType.DataError,
                "File is not a TOIF file with size of 144x144",
            )
    else:
        from PIL import Image

        im = Image.open(filename)
        if im.size != (128, 64):
            raise tools.CallException(
                proto.FailureType.DataError, "Wrong size of the image"
            )
        im = im.convert("1")
        pix = im.load()
        img = bytearray(1024)
        for j in range(64):
            for i in range(128):
                if pix[i, j]:
                    o = i + j * 128
                    img[o // 8] |= 1 << (7 - o % 8)
        img = bytes(img)
    return device.apply_settings(connect(), homescreen=img)


@cli.command()
@click.argument("counter", type=int)
@click.pass_obj
def set_u2f_counter(connect, counter):
    """Set U2F counter."""
    return device.set_u2f_counter(connect(), counter)


@cli.command()
@click.option(
    "-b",
    "--bootloader",
    help="Wipe device in bootloader mode. This also erases the firmware.",
    is_flag=True,
)
@click.pass_obj
def wipe_device(connect, bootloader):
    """Reset device to factory defaults and remove all private data."""
    client = connect()
    if bootloader:
        if not client.features.bootloader_mode:
            click.echo("Please switch your device to bootloader mode.")
            sys.exit(1)
        else:
            click.echo("Wiping user data and firmware!")
    else:
        if client.features.bootloader_mode:
            click.echo(
                "Your device is in bootloader mode. This operation would also erase firmware."
            )
            click.echo(
                'Specify "--bootloader" if that is what you want, or disconnect and reconnect device in normal mode.'
            )
            click.echo("Aborting.")
            sys.exit(1)
        else:
            click.echo("Wiping user data!")

    try:
        return device.wipe(connect())
    except tools.CallException as e:
        click.echo("Action failed: {} {}".format(*e.args))
        sys.exit(3)


@cli.command()
@click.option("-m", "--mnemonic", multiple=True)
@click.option("-e", "--expand", is_flag=True)
@click.option("-x", "--xprv")
@click.option("-p", "--pin", default="")
@click.option("-r", "--passphrase-protection", is_flag=True)
@click.option("-l", "--label", default="")
@click.option("-i", "--ignore-checksum", is_flag=True)
@click.option("-s", "--slip0014", is_flag=True)
@click.pass_obj
def load_device(
    connect,
    mnemonic,
    expand,
    xprv,
    pin,
    passphrase_protection,
    label,
    ignore_checksum,
    slip0014,
):
    """Load custom configuration to the device."""
    n_args = sum(bool(a) for a in (mnemonic, xprv, slip0014))
    if n_args == 0:
        raise click.ClickException("Please provide a mnemonic or xprv")
    if n_args > 1:
        raise click.ClickException("Cannot use mnemonic and xprv together")

    client = connect()

    if xprv:
        return debuglink.load_device_by_xprv(
            client, xprv, pin, passphrase_protection, label, "english"
        )

    if slip0014:
        mnemonic = [" ".join(["all"] * 12)]
        if not label:
            label = "SLIP-0014"

    return debuglink.load_device_by_mnemonic(
        client,
        list(mnemonic),
        pin,
        passphrase_protection,
        label,
        "english",
        ignore_checksum,
    )


@cli.command()
@click.option("-w", "--words", type=click.Choice(["12", "18", "24"]), default="24")
@click.option("-e", "--expand", is_flag=True)
@click.option("-p", "--pin-protection", is_flag=True)
@click.option("-r", "--passphrase-protection", is_flag=True)
@click.option("-l", "--label")
@click.option(
    "-t", "--type", "rec_type", type=CHOICE_RECOVERY_DEVICE_TYPE, default="scrambled"
)
@click.option("-d", "--dry-run", is_flag=True)
@click.pass_obj
def recovery_device(
    connect,
    words,
    expand,
    pin_protection,
    passphrase_protection,
    label,
    rec_type,
    dry_run,
):
    """Start safe recovery workflow."""
    if rec_type == proto.RecoveryDeviceType.ScrambledWords:
        input_callback = ui.mnemonic_words(expand)
    else:
        input_callback = ui.matrix_words
        click.echo(ui.RECOVERY_MATRIX_DESCRIPTION)

    return device.recover(
        connect(),
        word_count=int(words),
        passphrase_protection=passphrase_protection,
        pin_protection=pin_protection,
        label=label,
        language="english",
        input_callback=input_callback,
        type=rec_type,
        dry_run=dry_run,
    )


@cli.command()
@click.option("-e", "--show-entropy", is_flag=True)
@click.option("-t", "--strength", type=click.Choice(["128", "192", "256"]))
@click.option("-r", "--passphrase-protection", is_flag=True)
@click.option("-p", "--pin-protection", is_flag=True)
@click.option("-l", "--label")
@click.option("-u", "--u2f-counter", default=0)
@click.option("-s", "--skip-backup", is_flag=True)
@click.option("-n", "--no-backup", is_flag=True)
@click.option("-b", "--backup-type", type=CHOICE_RESET_DEVICE_TYPE, default="single")
@click.pass_obj
def reset_device(
    connect,
    show_entropy,
    strength,
    passphrase_protection,
    pin_protection,
    label,
    u2f_counter,
    skip_backup,
    no_backup,
    backup_type,
):
    """Perform device setup and generate new seed."""
    if strength:
        strength = int(strength)

    client = connect()
    if (
        backup_type == proto.BackupType.Slip39_Basic
        and proto.Capability.Shamir not in client.features.capabilities
    ) or (
        backup_type == proto.BackupType.Slip39_Advanced
        and proto.Capability.ShamirGroups not in client.features.capabilities
    ):
        click.echo(
            "WARNING: Your Trezor device does not indicate support for the requested\n"
            "backup type. Traditional single-seed backup may be generated instead."
        )

    return device.reset(
        client,
        display_random=show_entropy,
        strength=strength,
        passphrase_protection=passphrase_protection,
        pin_protection=pin_protection,
        label=label,
        language="english",
        u2f_counter=u2f_counter,
        skip_backup=skip_backup,
        no_backup=no_backup,
        backup_type=backup_type,
    )


@cli.command()
@click.pass_obj
def backup_device(connect):
    """Perform device seed backup."""
    return device.backup(connect())


#
# Firmware update
#


ALLOWED_FIRMWARE_FORMATS = {
    1: (firmware.FirmwareFormat.TREZOR_ONE, firmware.FirmwareFormat.TREZOR_ONE_V2),
    2: (firmware.FirmwareFormat.TREZOR_T,),
}


def _print_version(version):
    vstr = "Firmware version {major}.{minor}.{patch} build {build}".format(**version)
    click.echo(vstr)


def validate_firmware(version, fw, expected_fingerprint=None):
    if version == firmware.FirmwareFormat.TREZOR_ONE:
        if fw.embedded_onev2:
            click.echo("Trezor One firmware with embedded v2 image (1.8.0 or later)")
            _print_version(fw.embedded_onev2.firmware_header.version)
        else:
            click.echo("Trezor One firmware image.")
    elif version == firmware.FirmwareFormat.TREZOR_ONE_V2:
        click.echo("Trezor One v2 firmware (1.8.0 or later)")
        _print_version(fw.firmware_header.version)
    elif version == firmware.FirmwareFormat.TREZOR_T:
        click.echo("Trezor T firmware image.")
        vendor = fw.vendor_header.vendor_string
        vendor_version = "{major}.{minor}".format(**fw.vendor_header.version)
        click.echo("Vendor header from {}, version {}".format(vendor, vendor_version))
        _print_version(fw.firmware_header.version)

    try:
        firmware.validate(version, fw, allow_unsigned=False)
        click.echo("Signatures are valid.")
    except firmware.Unsigned:
        if not click.confirm("No signatures found. Continue?", default=False):
            sys.exit(1)
        try:
            firmware.validate(version, fw, allow_unsigned=True)
            click.echo("Unsigned firmware looking OK.")
        except firmware.FirmwareIntegrityError as e:
            click.echo(e)
            click.echo("Firmware validation failed, aborting.")
            sys.exit(4)
    except firmware.FirmwareIntegrityError as e:
        click.echo(e)
        click.echo("Firmware validation failed, aborting.")
        sys.exit(4)

    fingerprint = firmware.digest(version, fw).hex()
    click.echo("Firmware fingerprint: {}".format(fingerprint))
    if expected_fingerprint and fingerprint != expected_fingerprint:
        click.echo("Expected fingerprint: {}".format(expected_fingerprint))
        click.echo("Fingerprints do not match, aborting.")
        sys.exit(5)


def find_best_firmware_version(
    bootloader_version, requested_version=None, beta=False, bitcoin_only=False
):
    if beta:
        url = "https://beta-wallet.trezor.io/data/firmware/{}/releases.json"
    else:
        url = "https://wallet.trezor.io/data/firmware/{}/releases.json"
    releases = requests.get(url.format(bootloader_version[0])).json()
    if not releases:
        raise click.ClickException("Failed to get list of releases")

    if bitcoin_only:
        releases = [r for r in releases if "url_bitcoinonly" in r]
    releases.sort(key=lambda r: r["version"], reverse=True)

    def version_str(version):
        return ".".join(map(str, version))

    want_version = requested_version

    if want_version is None:
        want_version = releases[0]["version"]
        click.echo("Best available version: {}".format(version_str(want_version)))

    confirm_different_version = False
    while True:
        want_version_str = version_str(want_version)
        try:
            release = next(r for r in releases if r["version"] == want_version)
        except StopIteration:
            click.echo("Version {} not found.".format(want_version_str))
            sys.exit(1)

        if (
            "min_bootloader_version" in release
            and release["min_bootloader_version"] > bootloader_version
        ):
            need_version_str = version_str(release["min_firmware_version"])
            click.echo(
                "Version {} is required before upgrading to {}.".format(
                    need_version_str, want_version_str
                )
            )
            want_version = release["min_firmware_version"]
            confirm_different_version = True
        else:
            break

    if confirm_different_version:
        installing_different = "Installing version {} instead.".format(want_version_str)
        if requested_version is None:
            click.echo(installing_different)
        else:
            ok = click.confirm(installing_different + " Continue?", default=True)
            if not ok:
                sys.exit(1)

    if bitcoin_only:
        url = release["url_bitcoinonly"]
        fingerprint = release["fingerprint_bitcoinonly"]
    else:
        url = release["url"]
        fingerprint = release["fingerprint"]
    if beta:
        url = "https://beta-wallet.trezor.io/" + url
    else:
        url = "https://wallet.trezor.io/" + url

    return url, fingerprint


@cli.command()
# fmt: off
@click.option("-f", "--filename")
@click.option("-u", "--url")
@click.option("-v", "--version")
@click.option("-s", "--skip-check", is_flag=True, help="Do not validate firmware integrity")
@click.option("-n", "--dry-run", is_flag=True, help="Perform all steps but do not actually upload the firmware")
@click.option("--beta", is_flag=True, help="Use firmware from BETA wallet")
@click.option("--bitcoin-only", is_flag=True, help="Use bitcoin-only firmware (if possible)")
@click.option("--raw", is_flag=True, help="Push raw data to Trezor")
@click.option("--fingerprint", help="Expected firmware fingerprint in hex")
@click.option("--skip-vendor-header", help="Skip vendor header validation on Trezor T")
# fmt: on
@click.pass_obj
def firmware_update(
    connect,
    filename,
    url,
    version,
    skip_check,
    fingerprint,
    skip_vendor_header,
    raw,
    dry_run,
    beta,
    bitcoin_only,
):
    """Upload new firmware to device.

    Device must be in bootloader mode.

    You can specify a filename or URL from which the firmware can be downloaded.
    You can also explicitly specify a firmware version that you want.
    Otherwise, trezorctl will attempt to find latest available version
    from wallet.trezor.io.

    If you provide a fingerprint via the --fingerprint option, it will be checked
    against downloaded firmware fingerprint. Otherwise fingerprint is checked
    against wallet.trezor.io information, if available.

    If you are customizing Model T bootloader and providing your own vendor header,
    you can use --skip-vendor-header to ignore vendor header signatures.
    """
    if sum(bool(x) for x in (filename, url, version)) > 1:
        click.echo("You can use only one of: filename, url, version.")
        sys.exit(1)

    client = connect()
    if not dry_run and not client.features.bootloader_mode:
        click.echo("Please switch your device to bootloader mode.")
        sys.exit(1)

    f = client.features
    bootloader_onev2 = f.major_version == 1 and f.minor_version >= 8

    if filename:
        data = open(filename, "rb").read()
    else:
        if not url:
            bootloader_version = [f.major_version, f.minor_version, f.patch_version]
            version_list = [int(x) for x in version.split(".")] if version else None
            url, fp = find_best_firmware_version(
                bootloader_version, version_list, beta, bitcoin_only
            )
            if not fingerprint:
                fingerprint = fp

        try:
            click.echo("Downloading from {}".format(url))
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            click.echo("Error downloading file: {}".format(err))
            sys.exit(3)

        data = r.content

    if not raw and not skip_check:
        try:
            version, fw = firmware.parse(data)
        except Exception as e:
            click.echo(e)
            sys.exit(2)

        validate_firmware(version, fw, fingerprint)
        if (
            bootloader_onev2
            and version == firmware.FirmwareFormat.TREZOR_ONE
            and not fw.embedded_onev2
        ):
            click.echo("Firmware is too old for your device. Aborting.")
            sys.exit(3)
        elif not bootloader_onev2 and version == firmware.FirmwareFormat.TREZOR_ONE_V2:
            click.echo("You need to upgrade to bootloader 1.8.0 first.")
            sys.exit(3)

        if f.major_version not in ALLOWED_FIRMWARE_FORMATS:
            click.echo("trezorctl doesn't know your device version. Aborting.")
            sys.exit(3)
        elif version not in ALLOWED_FIRMWARE_FORMATS[f.major_version]:
            click.echo("Firmware does not match your device, aborting.")
            sys.exit(3)

    if not raw:
        # special handling for embedded-OneV2 format:
        # for bootloader < 1.8, keep the embedding
        # for bootloader 1.8.0 and up, strip the old OneV1 header
        if bootloader_onev2 and data[:4] == b"TRZR" and data[256 : 256 + 4] == b"TRZF":
            click.echo("Extracting embedded firmware image (fingerprint may change).")
            data = data[256:]

    if dry_run:
        click.echo("Dry run. Not uploading firmware to device.")
    else:
        try:
            if f.major_version == 1 and f.firmware_present is not False:
                # Trezor One does not send ButtonRequest
                click.echo("Please confirm the action on your Trezor device")
            return firmware.update(client, data)
        except exceptions.Cancelled:
            click.echo("Update aborted on device.")
        except exceptions.TrezorException as e:
            click.echo("Update failed: {}".format(e))
            sys.exit(3)


@cli.command()
@click.pass_obj
def self_test(connect):
    """Perform a self-test."""
    return debuglink.self_test(connect())


@cli.command()
def usb_reset():
    """Perform USB reset on a stuck device.

    This can fix LIBUSB_ERROR_PIPE and similar errors when connecting to a device
    in a messed state.
    """
    from trezorlib.transport.webusb import WebUsbTransport

    WebUsbTransport.enumerate(usb_reset=True)


#
# Basic coin functions
#


@cli.command()
@click.option("-c", "--coin", default="Bitcoin")
@click.option(
    "-n", "--address", required=True, help="BIP-32 path, e.g. m/44'/0'/0'/0/0"
)
@click.option("-t", "--script-type", type=CHOICE_INPUT_SCRIPT_TYPE, default="address")
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_address(connect, coin, address, script_type, show_display):
    """Get address for specified path."""
    client = connect()
    address_n = tools.parse_path(address)
    return btc.get_address(
        client, coin, address_n, show_display, script_type=script_type
    )


@cli.command()
@click.option("-c", "--coin", default="Bitcoin")
@click.option("-n", "--address", required=True, help="BIP-32 path, e.g. m/44'/0'/0'")
@click.option("-e", "--curve")
@click.option("-t", "--script-type", type=CHOICE_INPUT_SCRIPT_TYPE, default="address")
@click.option("-d", "--show-display", is_flag=True)
@click.pass_obj
def get_public_node(connect, coin, address, curve, script_type, show_display):
    """Get public node of given path."""
    client = connect()
    address_n = tools.parse_path(address)
    result = btc.get_public_node(
        client,
        address_n,
        ecdsa_curve_name=curve,
        show_display=show_display,
        coin_name=coin,
        script_type=script_type,
    )
    return {
        "node": {
            "depth": result.node.depth,
            "fingerprint": "%08x" % result.node.fingerprint,
            "child_num": result.node.child_num,
            "chain_code": result.node.chain_code.hex(),
            "public_key": result.node.public_key.hex(),
        },
        "xpub": result.xpub,
    }


#
# Signing options
#


@cli.command()
@click.option("-c", "--coin", default="Bitcoin")
@click.argument("json_file", type=click.File(), required=False)
@click.pass_obj
def sign_tx(connect, coin, json_file):
    client = connect()

    # XXX this is the future code of this function
    if json_file is not None:
        data = json.load(json_file)
        coin = data["coin_name"]
        details = protobuf.dict_to_proto(proto.SignTx, data["details"])
        inputs = [protobuf.dict_to_proto(proto.TxInputType, i) for i in data["inputs"]]
        outputs = [
            protobuf.dict_to_proto(proto.TxOutputType, output)
            for output in data["outputs"]
        ]
        prev_txes = {
            bytes.fromhex(txid): protobuf.dict_to_proto(proto.TransactionType, tx)
            for txid, tx in data["prev_txes"].items()
        }

        _, serialized_tx = btc.sign_tx(
            client, coin, inputs, outputs, details, prev_txes
        )

        client.close()

        click.echo()
        click.echo("Signed Transaction:")
        click.echo(serialized_tx.hex())
        return

    # XXX ALL THE REST is legacy code and will be dropped
    click.echo("Warning: interactive sign-tx mode is deprecated.", err=True)
    click.echo(
        "Instead, you should format your transaction data as JSON and "
        "supply the file as an argument to sign-tx"
    )
    if coin in coins.tx_api:
        coin_data = coins.by_name[coin]
        txapi = coins.tx_api[coin]
    else:
        click.echo('Coin "%s" is not recognized.' % coin, err=True)
        click.echo(
            "Supported coin types: %s" % ", ".join(coins.tx_api.keys()), err=True
        )
        sys.exit(1)

    def default_script_type(address_n):
        """Sign transaction."""
        script_type = "address"

        if address_n is None:
            pass
        elif address_n[0] == tools.H_(49):
            script_type = "p2shsegwit"

        return script_type

    def outpoint(s):
        txid, vout = s.split(":")
        return bytes.fromhex(txid), int(vout)

    inputs = []
    txes = {}
    while True:
        click.echo()
        prev = click.prompt(
            "Previous output to spend (txid:vout)", type=outpoint, default=""
        )
        if not prev:
            break
        prev_hash, prev_index = prev
        address_n = click.prompt("BIP-32 path to derive the key", type=tools.parse_path)
        try:
            tx = txapi[prev_hash]
            txes[prev_hash] = tx
            amount = tx.bin_outputs[prev_index].amount
            click.echo("Prefilling input amount: {}".format(amount))
        except Exception as e:
            print(e)
            click.echo("Failed to fetch transation. This might bite you later.")
            amount = click.prompt("Input amount (satoshis)", type=int, default=0)
        sequence = click.prompt(
            "Sequence Number to use (RBF opt-in enabled by default)",
            type=int,
            default=0xFFFFFFFD,
        )
        script_type = click.prompt(
            "Input type",
            type=CHOICE_INPUT_SCRIPT_TYPE,
            default=default_script_type(address_n),
        )
        script_type = (
            script_type
            if isinstance(script_type, int)
            else CHOICE_INPUT_SCRIPT_TYPE.typemap[script_type]
        )

        new_input = proto.TxInputType(
            address_n=address_n,
            prev_hash=prev_hash,
            prev_index=prev_index,
            amount=amount,
            script_type=script_type,
            sequence=sequence,
        )
        if coin_data["bip115"]:
            prev_output = txapi.get_tx(prev_hash.hex()).bin_outputs[prev_index]
            new_input.prev_block_hash_bip115 = prev_output.block_hash
            new_input.prev_block_height_bip115 = prev_output.block_height

        inputs.append(new_input)

    if coin_data["bip115"]:
        current_block_height = txapi.current_height()
        # Zencash recommendation for the better protection
        block_height = current_block_height - 300
        block_hash = txapi.get_block_hash(block_height)
        # Blockhash passed in reverse order
        block_hash = block_hash[::-1]
    else:
        block_height = None
        block_hash = None

    outputs = []
    while True:
        click.echo()
        address = click.prompt("Output address (for non-change output)", default="")
        if address:
            address_n = None
        else:
            address = None
            address_n = click.prompt(
                "BIP-32 path (for change output)", type=tools.parse_path, default=""
            )
            if not address_n:
                break
        amount = click.prompt("Amount to spend (satoshis)", type=int)
        script_type = click.prompt(
            "Output type",
            type=CHOICE_OUTPUT_SCRIPT_TYPE,
            default=default_script_type(address_n),
        )
        script_type = (
            script_type
            if isinstance(script_type, int)
            else CHOICE_OUTPUT_SCRIPT_TYPE.typemap[script_type]
        )
        outputs.append(
            proto.TxOutputType(
                address_n=address_n,
                address=address,
                amount=amount,
                script_type=script_type,
                block_hash_bip115=block_hash,
                block_height_bip115=block_height,
            )
        )

    signtx = proto.SignTx()
    signtx.version = click.prompt("Transaction version", type=int, default=2)
    signtx.lock_time = click.prompt("Transaction locktime", type=int, default=0)
    if coin == "Capricoin":
        signtx.timestamp = click.prompt("Transaction timestamp", type=int)

    _, serialized_tx = btc.sign_tx(
        client, coin, inputs, outputs, details=signtx, prev_txes=txes
    )

    client.close()

    click.echo()
    click.echo("Signed Transaction:")
    click.echo(serialized_tx.hex())
    click.echo()
    click.echo("Use the following form to broadcast it to the network:")
    click.echo(txapi.pushtx_url)


#
# Message functions
#


@cli.command()
@click.option("-c", "--coin", default="Bitcoin")
@click.option(
    "-n", "--address", required=True, help="BIP-32 path, e.g. m/44'/0'/0'/0/0"
)
@click.option(
    "-t",
    "--script-type",
    type=click.Choice(["address", "segwit", "p2shsegwit"]),
    default="address",
)
@click.argument("message")
@click.pass_obj
def sign_message(connect, coin, address, message, script_type):
    """Sign message using address of given path."""
    client = connect()
    address_n = tools.parse_path(address)
    typemap = {
        "address": proto.InputScriptType.SPENDADDRESS,
        "segwit": proto.InputScriptType.SPENDWITNESS,
        "p2shsegwit": proto.InputScriptType.SPENDP2SHWITNESS,
    }
    script_type = typemap[script_type]
    res = btc.sign_message(client, coin, address_n, message, script_type)
    return {
        "message": message,
        "address": res.address,
        "signature": base64.b64encode(res.signature),
    }


@cli.command()
@click.option("-c", "--coin", default="Bitcoin")
@click.argument("address")
@click.argument("signature")
@click.argument("message")
@click.pass_obj
def verify_message(connect, coin, address, signature, message):
    """Verify message."""
    signature = base64.b64decode(signature)
    return btc.verify_message(connect(), coin, address, signature, message)



@cli.command()
@click.option("-n", "--address", required=True, help="BIP-32 path, e.g. m/10016'/0")
@click.argument("key")
@click.argument("value")
@click.pass_obj
def encrypt_keyvalue(connect, address, key, value):
    """Encrypt value by given key and path."""
    client = connect()
    address_n = tools.parse_path(address)
    res = misc.encrypt_keyvalue(client, address_n, key, value.encode())
    return res.hex()


@cli.command()
@click.option("-n", "--address", required=True, help="BIP-32 path, e.g. m/10016'/0")
@click.argument("key")
@click.argument("value")
@click.pass_obj
def decrypt_keyvalue(connect, address, key, value):
    """Decrypt value by given key and path."""
    client = connect()
    address_n = tools.parse_path(address)
    return misc.decrypt_keyvalue(client, address_n, key, bytes.fromhex(value))


cli.add_command(binance.cli)
cli.add_command(cardano.cli)
cli.add_command(cosi.cli)
cli.add_command(eos.cli)
cli.add_command(ethereum.cli)
cli.add_command(lisk.cli)
cli.add_command(monero.cli)
cli.add_command(nem.cli)
cli.add_command(ripple.cli)
cli.add_command(stellar.cli)
cli.add_command(tezos.cli)
cli.add_command(webauthn.cli)


#
# Main
#


if __name__ == "__main__":
    cli()  # pylint: disable=E1120
