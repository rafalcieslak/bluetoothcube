from kivy.utils import platform

if platform == 'android':
    from bluetoothcube.btutil.android import (  # noqa: F401
        BluetoothCubeScanner, BluetoothCubeConnection)
elif platform == 'linux':
    from bluetoothcube.btutil.linux import (  # noqa: F401
        BluetoothCubeScanner, BluetoothCubeConnection)

else:
    raise NotImplementedError('Only android and linux platforms are supported')
