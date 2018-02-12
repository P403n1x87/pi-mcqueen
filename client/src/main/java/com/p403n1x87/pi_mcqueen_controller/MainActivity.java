package com.p403n1x87.pi_mcqueen_controller;

import android.app.Activity;

import android.content.Context;

import android.hardware.SensorManager;

import android.os.Bundle;

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

import com.p403n1x87.pi_mcqueen_controller.GravitySensorManager;

public class MainActivity extends Activity
{
  private Switch          connectSwitch        = null;

  private WebSocketClient webSocketClient      = null;

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    // UI
    setContentView(R.layout.main_layout);
    if (connectSwitch == null) initializeConnectSwitch();

    // Sensors
    GravitySensorManager.init((SensorManager) getSystemService(Context.SENSOR_SERVICE));

    if (!GravitySensorManager.hasSensor()) {
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

    String address = String.valueOf(((EditText) findViewById(R.id.address)).getText());
    String port    = String.valueOf(((EditText) findViewById(R.id.port)).getText());

    try {
      webSocketClient = buildWebSocketClient(new URI("ws://" + address + ":" + port));

      if (webSocketClient == null) {
        Log.e("pi_mcqueen_controller", "Unable to create a WebSocket client.");
        return;
      }

      webSocketClient.connect();

      GravitySensorManager.registerWithSocket(webSocketClient);
    } catch (URISyntaxException e) {
      Log.e("pi_mcqueen_controller", "Invalid URI.");
      return;
    }
  }

  /**
   * Stops listening to the gravity sensor and closes the connection with the
   * WebSocket server
   */
  private void stop() {
    GravitySensorManager.unregister();

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
  // WebSocket
  // ===========================================================================
  private WebSocketClient buildWebSocketClient(URI uri) {
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
}
