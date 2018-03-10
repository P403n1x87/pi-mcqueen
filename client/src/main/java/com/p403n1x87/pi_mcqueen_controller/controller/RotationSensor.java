package com.p403n1x87.pi_mcqueen_controller.controller;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

import android.util.Log;

import java.util.List;

import static java.lang.Math.sqrt;

import com.p403n1x87.pi_mcqueen_controller.controller.Controller;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.exceptions.WebsocketNotConnectedException;

public class RotationSensor implements Controller{

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
        float x = (float) Math.toDegrees(orientations[1]) * (float) (-127. / 45.);
        if (x < -127) x = -127;
        if (x >  127) x =  127;
        float y = (float) Math.toDegrees(orientations[2]) + 90;
        y *= (float) (-127. / 90.);
        if (y < -127) y = (float) 127.;

        byte[] data = {new Float(x).byteValue(), new Float(y).byteValue()};

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

  public RotationSensor(SensorManager sensorManager) {
    if (contextSensorManager != null) return;

    contextSensorManager = sensorManager;
    gyroscopeSensor = contextSensorManager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
  }

  public boolean canControl() {
    return gyroscopeSensor != null;
  }

  public String getName() {
    return "Built-in Rotation Sensor";
  }

  public void registerWithSocket(WebSocketClient socket) {
    webSocketClient = socket;
    contextSensorManager.registerListener(LISTENER, gyroscopeSensor, SensorManager.SENSOR_DELAY_NORMAL);
  }

  public void unregister () {
    contextSensorManager.unregisterListener(LISTENER);
  }
}
