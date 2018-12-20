import kivy
import gatt


from kivy.clock import Clock

from bluetoothcube.btutil.const import (
    CUBE_STATE_SERVICE, CUBE_STATE_RESPONSE,
    CUBE_INFO_SERVICE, CUBE_INFO_REQUEST, CUBE_INFO_RESPONSE,
    CLIENT_CHARACTERISTIC_UUID)


# Searches for a bluetooth cube.
class BluetoothCubeScanner(kivy.event.EventDispatcher, gatt.DeviceManager):
    def __init__(self):
        self.register_event_type('on_cube_found')
        super().__init__(adapter_name='hci0')
        self._main_loop = None
        self.devices_found = set()

    def scan(self):
        self.devices_found = set()
        self.start_discovery()
        self.prepare_run()
        self.run()

    def stop_scan(self):
        self.stop_discovery()
        if self._main_loop_schedule:
            Clock.unschedule(self._main_loop_schedule)

    def prepare_run(self):
        """
        Similar to gatt.DeviceManager.run, a custom implementation that does
        not block, but schedules the gobject main_look within kivy's main loop.
        """
        if self._main_loop:
            return  # Already prepared.

        import dbus
        from gi.repository import GObject

        self._interface_added_signal = self._bus.add_signal_receiver(
            self._interfaces_added,
            dbus_interface='org.freedesktop.DBus.ObjectManager',
            signal_name='InterfacesAdded')

        self._properties_changed_signal = self._bus.add_signal_receiver(
            self._properties_changed,
            dbus_interface=dbus.PROPERTIES_IFACE,
            signal_name='PropertiesChanged',
            arg0='org.bluez.Device1',
            path_keyword='path')

        self._main_loop = GObject.MainLoop()
        self._main_loop_context = self._main_loop.get_context()

        # The GObject loop would eat up our keyboard interrupts, so we rebind
        # SIGINT to the default handler.
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def run(self):
        # schedule the iteration each frame
        self._main_loop_schedule = Clock.schedule_interval(
            self._gobject_iteration, 0)

    def _gobject_iteration(self, td):
        loop = 0
        while self._main_loop_context.pending() and loop < 10:
            self._main_loop_context.iteration(False)
            loop += 1

    def device_discovered(self, device):
        # Install extra function for interface compatibility
        device.getName = lambda: device.alias()

        if device.mac_address in self.devices_found:
            return
        self.devices_found.add(device.mac_address)

        name = device.getName()
        if name and (name.startswith("GiC") or name.startswith("GiS")):
            self.dispatch('on_cube_found', device)

    def on_cube_found(self, *args):
        pass


class BluetoothCubeConnection(kivy.event.EventDispatcher):
    def __init__(self):
        self.register_event_type('on_cube_connecting')
        self.register_event_type('on_cube_connecting_failed')
        self.register_event_type('on_cube_connected')
        self.register_event_type('on_cube_disconnected')
        self.register_event_type('on_state_updated')
        super().__init__()

    def connect(self, device):

        self.dispatch('on_cube_connecting',
                      f"Connecting to {device.getName()}...", 20)

    def disconnect(self):
        pass

    def on_cube_connecting(self, *args):
        pass

    def on_cube_connecting_failed(self, *args):
        pass

    def on_cube_connected(self, *args):
        pass

    def on_cube_disconnected(self, *args):
        pass

    def on_state_updated(self, *args):
        pass
