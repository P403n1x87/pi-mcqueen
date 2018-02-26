package com.p403n1x87.pi_mcqueen_controller;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

import android.util.Log;

import java.util.List;

import static java.lang.Math.sqrt;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.exceptions.WebsocketNotConnectedException;

class RotationManager {

  private static Sensor          gyroscopeSensor      = null;
  private static SensorManager   contextSensorManager = null;

  private static WebSocketClient webSocketClient      = null;

  private static final SensorEventListener LISTENER = new SensorEventListener() {
    public void onSensorChanged(SensorEvent event) {
      float[] rotationMatrix = new float[16];
      SensorManager.getRotationMatrixFromVector(rotationMatrix, event.values);

      // Convert to orientations
      float[] orientations = new float[3];
      SensorManager.getOrientation(rotationMatrix, orientations);

      try {
        byte[] data = new byte[3];
        for (int i = 0; i < 3; i++) data[i] = new Float(Math.toDegrees(orientations[i]) / 360 * 256).byteValue();
        webSocketClient.send(data);
      } catch (WebsocketNotConnectedException e) {
        Log.w("pi_mcqueen_controller", "Sensor updated but socket not connected");
      }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int a) {
      Log.d("pi_mcqueen_controller", "accuracy changed: " + a);
    }
  };

  public static void init(SensorManager sensorManager) {
    if (contextSensorManager != null) return;

    contextSensorManager = sensorManager;
    gyroscopeSensor = contextSensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
  }

  public static boolean hasSensor() {
    return gyroscopeSensor != null;
  }

  public static void registerWithSocket(WebSocketClient socket) {
    webSocketClient = socket;
    contextSensorManager.registerListener(LISTENER, gyroscopeSensor, SensorManager.SENSOR_DELAY_FASTEST);
  }

  public static void unregister () {
    contextSensorManager.unregisterListener(LISTENER);
  }
}
