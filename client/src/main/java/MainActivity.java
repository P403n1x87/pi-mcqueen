package com.p403n1x87.pi_mcqueen_controller;

import android.app.Activity;

import android.os.Bundle;

import android.content.Context;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.Toast;

import android.util.Log;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft_17;
import org.java_websocket.handshake.ServerHandshake;
import org.java_websocket.exceptions.WebsocketNotConnectedException;

import static java.lang.Math.sqrt;

public class MainActivity extends Activity implements SensorEventListener
{
  private Switch          connectSwitch        = null;

  private Sensor          gravitySensor        = null;
  private SensorManager   contextSensorManager = null;

  private WebSocketClient webSocketClient      = null;

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    // UI
    setContentView(R.layout.main_layout);
    if (connectSwitch == null) initializeConnectSwitch();

    // Sensors
    if (contextSensorManager == null) gravitySensor = getSensor();

    if (contextSensorManager != null && gravitySensor == null) {
      // No gravity sensors
      Toast.makeText(getApplicationContext(), "No gravity sensors detected.", Toast.LENGTH_SHORT).show();
      connectSwitch.setEnabled(false);
      return;
    }
  }

  /**
   * Starts listening to the gravity sensor and connects to the WebSocket
   * server
   */
  private void start() {
    if (webSocketClient != null) webSocketClient.close();

    webSocketClient = buildWebSocketClient();

    if (webSocketClient == null) {
      Log.e("pi_mcqueen_controller", "Unable to create a WebSocket client.");
      return;
    }

    webSocketClient.connect();

    registerSensorListener();
  }

  /**
   * Stops listening to the gravity sensor and closes the connection with the
   * WebSocket server
   */
  private void stop() {
    contextSensorManager.unregisterListener(this);

    if (webSocketClient == null) {
      Log.e("pi_mcqueen_controller", "Attempt to close a null WebSocket client.");
      return;
    }

    webSocketClient.close();
  }


  // ===========================================================================
  // UI
  // ===========================================================================
  private void initializeConnectSwitch() {
    connectSwitch = (Switch) findViewById(R.id.connect_switch);

    connectSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
      public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
        if (isChecked) start(); else stop();
      }
    });
  }


  // ===========================================================================
  // WebSocketClient
  // ===========================================================================
  private WebSocketClient buildWebSocketClient () {
    String address = String.valueOf(((EditText) findViewById(R.id.address)).getText());
    String port    = String.valueOf(((EditText) findViewById(R.id.port)).getText());

    URI uri;
    try {
      uri = new URI("ws://" + address + ":" + port);
    } catch (URISyntaxException e) {
      Log.e("pi_mcqueen_controller", "Invalid URI.");
      return null;
    }

    return new WebSocketClient(uri, new Draft_17()) {
      @Override
      public void onOpen(ServerHandshake serverHandshake) {
        Log.i("pi_mcqueen_controller", "Opened");
      }

      @Override
      public void onMessage(String message) {

      }

      @Override
      public void onClose(int i, String s, boolean b) {
        runOnUiThread(new Runnable() {
          @Override
          public void run() {
            connectSwitch.setChecked(false);
          }
        });
      }

      @Override
      public void onError(Exception e) {
        Log.e("pi_mcqueen_controller", "Error " + e.getMessage());
        runOnUiThread(new Runnable() {
          @Override
          public void run() {
            Toast.makeText(getApplicationContext(), "Connection attempt failed.", Toast.LENGTH_SHORT).show();
          }
        });

      }
    };
  }


  // ===========================================================================
  // Sensor
  // ===========================================================================
  private Sensor getSensor() {
    contextSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
    if (contextSensorManager.getDefaultSensor(Sensor.TYPE_GRAVITY) != null) {
      List<Sensor> gravitySensors = contextSensorManager.getSensorList(Sensor.TYPE_GRAVITY);

      // Get first available gravity sensor
      return gravitySensors.get(0);
    }

    return null;
  }

  private void registerSensorListener() {
    contextSensorManager.registerListener(this, gravitySensor, SensorManager.SENSOR_DELAY_FASTEST);
  }

  @Override
  public void onSensorChanged(final SensorEvent event) {
    float x = event.values[0];
    float y = event.values[1];
    float z = event.values[2];
    float g = (float) sqrt(x*x + y*y + z*z);
    try {
      webSocketClient.send(Float.toString(x/g*100) + " " + Float.toString(y/g*100) + " " + Float.toString(z/g*100));
    } catch (WebsocketNotConnectedException e) {
      Log.w("pi_mcqueen_controller", "Sensor updated but socket not connected");
    }
  }

  @Override
  public void onAccuracyChanged(Sensor sensor, int a) {}
}
