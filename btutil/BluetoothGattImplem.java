package org.supercube;

import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.BluetoothGattService;
import android.util.Log;

public class BluetoothGattImplem extends BluetoothGattCallback {

      public interface OnBluetoothGattCallback {
       // ... all the methods from BluetoothGattCallback here ...like:
         void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic);

         void onConnectionStateChange(BluetoothGatt gatt, int status, int newState);

         void onServicesDiscovered(BluetoothGatt gatt, int status);

         void onCharacteristicRead(BluetoothGatt gatt,BluetoothGattCharacteristic characteristic, int status);
      
    }
    // private storage for the callback object
    private OnBluetoothGattCallback callback = null;

    // method to set the callback object
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
