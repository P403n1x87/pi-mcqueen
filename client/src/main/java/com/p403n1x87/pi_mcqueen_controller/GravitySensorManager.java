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

class GravitySensorManager {

  private static Sensor          gravitySensor        = null;
  private static SensorManager   contextSensorManager = null;

  private static WebSocketClient webSocketClient = null;

  private static final SensorEventListener LISTENER = new SensorEventListener() {
    @Override
    public void onSensorChanged(final SensorEvent event) {
      float x = event.values[0];
      float y = event.values[1];
      float z = event.values[2];
      float g = (float) sqrt(x*x + y*y + z*z);
      try {
        byte[] data = new byte[3];
        for (int i = 0; i < 3; i++) data[i] = new Float(event.values[i] / g * 127).byteValue();
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

    if (contextSensorManager.getDefaultSensor(Sensor.TYPE_GRAVITY) != null) {
      List<Sensor> gravitySensors = contextSensorManager.getSensorList(Sensor.TYPE_GRAVITY);
      // Get first available gravity sensor
      gravitySensor = gravitySensors.get(0);
    }
  }

  public static boolean hasSensor() {
    return gravitySensor != null;
  }

  public static void registerWithSocket(WebSocketClient socket) {
    webSocketClient = socket;
    contextSensorManager.registerListener(LISTENER, gravitySensor, SensorManager.SENSOR_DELAY_FASTEST);
  }

  public static void unregister () {
    contextSensorManager.unregisterListener(LISTENER);
  }
}
