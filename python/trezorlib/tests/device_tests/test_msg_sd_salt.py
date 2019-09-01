# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

import pytest

from trezorlib import device, messages as proto

from .common import TrezorTest


@pytest.mark.skip_t1
class TestMsgSdsalt(TrezorTest):
    def test_sd_salt(self):
        self.setup_mnemonic_nopin_nopassphrase()
        features = self.client.call_raw(proto.Initialize())

        # Disabling SD salt should fail
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.DISABLE))
        assert isinstance(ret, proto.Failure)

        # Enable SD salt
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.ENABLE))
        assert isinstance(ret, proto.ButtonRequest)

        # Confirm operation
        self.client.debug.press_yes()
        ret = self.client.call_raw(proto.ButtonAck())
        assert isinstance(ret, proto.Success)

        # Enabling SD salt should fail
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.ENABLE))
        assert isinstance(ret, proto.Failure)

        # Wipe
        device.wipe(self.client)
        self.setup_mnemonic_nopin_nopassphrase()
        features = self.client.call_raw(proto.Initialize())

        # Enable SD salt
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.ENABLE))
        assert isinstance(ret, proto.ButtonRequest)

        # Confirm operation
        self.client.debug.press_yes()
        ret = self.client.call_raw(proto.ButtonAck())
        assert isinstance(ret, proto.Success)

        # Regenerate SD salt
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.REGENERATE))
        assert isinstance(ret, proto.ButtonRequest)

        # Confirm operation
        self.client.debug.press_yes()
        ret = self.client.call_raw(proto.ButtonAck())
        assert isinstance(ret, proto.Success)

        # Disable SD salt
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.DISABLE))
        assert isinstance(ret, proto.ButtonRequest)

        # Confirm operation
        self.client.debug.press_yes()
        ret = self.client.call_raw(proto.ButtonAck())
        assert isinstance(ret, proto.Success)

        # Regenerating SD salt should fail
        ret = self.client.call_raw(proto.SdSalt(operation=proto.SdSaltOperationType.REGENERATE))
        assert isinstance(ret, proto.Failure)
