import kivy
import gatt
from threading import Thread

from kivy.clock import Clock
from kivy.app import App

from bluetoothcube.btutil.const import (
    CUBE_STATE_SERVICE, CUBE_STATE_RESPONSE,
    CUBE_INFO_SERVICE, CUBE_INFO_REQUEST, CUBE_INFO_RESPONSE)


class DeviceInfo:
    def __init__(self, address, name, manager):
        self.address = address
        self.name = name
        self.manager = manager


def sigint_handler(sig, frame):
    print("SIGINT, terminating...")
    App.get_running_app().stop()


# Searches for a bluetooth cube.
class BluetoothCubeScanner(kivy.event.EventDispatcher, gatt.DeviceManager):
    def __init__(self):
        self.register_event_type('on_cube_found')
        self.register_event_type('on_paired_cube_found')
        super().__init__(adapter_name='hci0')
        self._main_loop = None
        self.devices_found = set()

        self.prepare_run()

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
        signal.signal(signal.SIGINT, sigint_handler)

        # schedule the iteration each frame
        self._main_loop_schedule = Clock.schedule_interval(
            self._gobject_iteration, 0)

    def _gobject_iteration(self, td):
        loop = 0
        while self._main_loop_context.pending() and loop < 10:
            self._main_loop_context.iteration(False)
            loop += 1

    def scan(self):
        self.devices_found = set()

        # Check for already known devices.
        for device in self.devices():
            self.device_discovered(device)

        # Await new devices.
        self.start_discovery()

    def stop_scan(self):
        self.stop_discovery()

    def device_discovered(self, device):
        if device.mac_address in self.devices_found:
            return
        self.devices_found.add(device.mac_address)

        name = device.alias()
        print(f"Device found: {name}")
        # TODO: Refactor this condition into a shared file
        if name and (name.startswith("GiC") or name.startswith("GiS")):
            di = DeviceInfo(device.mac_address, name, self)
            if device.is_connected():
                self.dispatch('on_paired_cube_found', di)
            else:
                self.dispatch('on_cube_found', di)

    def on_cube_found(self, deviceinfo):
        pass

    def on_paired_cube_found(self, deviceinfo):
        pass


class BluetoothCubeConnection(gatt.Device, kivy.event.EventDispatcher):
    def __init__(self, deviceinfo):
        self.register_event_type('on_cube_connecting')
        self.register_event_type('on_cube_connecting_failed')
        self.register_event_type('on_cube_connected')
        self.register_event_type('on_cube_disconnected')
        self.register_event_type('on_state_updated')

        kivy.event.EventDispatcher.__init__(self)
        gatt.Device.__init__(self, deviceinfo.address, deviceinfo.manager)

    def connect(self):
        # Again, we customize the connection procedure to make it more
        # UI-friendly by splitting into parts.
        self.dispatch('on_cube_connecting',
                      f"Connecting to {self.alias()}...", 20)

        self._connect_signals()
        device = self  # Used by nested local class
        if not self.is_connected():
            class AsyncConnector(Thread):
                def run(self):
                    device._object.Connect()
            # Request connection in a separate thread no to block UI.
            AsyncConnector().start()
        else:
            self.connect_succeeded()

    def disconnect(self):
        device = self
        if self.is_connected():
            class AsyncDisconnector(Thread):
                def run(self):
                    device._object.Disconnect()
            # Request connection in a separate thread no to block UI.
            AsyncDisconnector().start()

    # Called when connection is successful.
    def connect_succeeded(self):
        super().connect_succeeded()
        self.dispatch('on_cube_connecting',
                      "Initializing cube...", 55)

        # Maybe services were already resolved?
        if not self.services and self.is_services_resolved():
            self.services_resolved()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("Disconnected.")
        self.dispatch('on_cube_disconnected')

    # Called when services get resolved.
    def services_resolved(self):
        super().services_resolved()
        self.dispatch('on_cube_connecting',
                      "Establishing communications...", 85)
        self.enable_notifications()

    def enable_notifications(self):
        # Find services
        self.cube_state_service = None
        self.cube_info_service = None

        for service in self.services:
            if service.uuid == CUBE_STATE_SERVICE:
                self.cube_state_service = service
            if service.uuid == CUBE_INFO_SERVICE:
                self.cube_info_service = service

        if not self.cube_state_service or not self.cube_info_service:
            self.disconnect()
            self.dispatch('on_cube_connecting_failed',
                          "A cube service was not found.")
            return

        # Find characteristics
        self.state_response_characteristic = None
        self.info_request_characteristic = None
        self.info_response_characteristic = None

        for ch in self.cube_state_service.characteristics:
            if ch.uuid == CUBE_STATE_RESPONSE:
                self.state_response_characteristic = ch
        for ch in self.cube_info_service.characteristics:
            if ch.uuid == CUBE_INFO_REQUEST:
                self.info_request_characteristic = ch
            if ch.uuid == CUBE_INFO_RESPONSE:
                self.info_response_characteristic = ch

        if not self.state_response_characteristic or \
           not self.info_request_characteristic or \
           not self.info_response_characteristic:
            self.disconnect()
            self.dispatch('on_cube_connecting_failed',
                          "A characteristic is not available.")
            return

        # Enable notifications
        self.state_response_characteristic.enable_notifications()
        self.info_response_characteristic.enable_notifications()

        self.dispatch('on_cube_connected')

    # Called when characteristic values change.
    def characteristic_value_updated(self, characteristic, value):
        if characteristic.uuid == CUBE_STATE_RESPONSE:
            self.dispatch('on_state_updated', value)
        else:
            print(f"Characteristic {characteristic.uuid} changed!")

    # The usual way of using a gatt.Device is to subclass it and override some
    # methods. However, since this class is an EventDispatcher so that widgets
    # can bind to it even before connection is made, we cannot enable the
    # connection in class' constructor. So we have to hook to the Device using
    # another way.
    def _install_callbacks(self):
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
