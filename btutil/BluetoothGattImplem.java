package org.cielak.bluetoothcube;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.BluetoothGattService;

public class BluetoothGattImplem extends BluetoothGattCallback {

      public interface OnBluetoothGattCallback {
         void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic);

         void onConnectionStateChange(BluetoothGatt gatt, int status, int newState);

         void onServicesDiscovered(BluetoothGatt gatt, int status);

         void onCharacteristicRead(BluetoothGatt gatt,BluetoothGattCharacteristic characteristic, int status);
      
    }
    private OnBluetoothGattCallback callback = null;

    public void setCallback(OnBluetoothGattCallback callback) {
        this.callback = callback;
    }
    public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
        if (this.callback != null)
            this.callback.onCharacteristicChanged(gatt, characteristic); 
    }
    public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
        if (this.callback != null)
            this.callback.onConnectionStateChange(gatt, status, newState); 
    }
    public void onServicesDiscovered(BluetoothGatt gatt, int status) {
        if (this.callback != null)
            this.callback.onServicesDiscovered(gatt, status); 
    }
    public void onCharacteristicRead(BluetoothGatt gatt,BluetoothGattCharacteristic characteristic, int status) {
        if (this.callback != null)
            this.callback.onCharacteristicRead(gatt,characteristic,status); 
    }
}
