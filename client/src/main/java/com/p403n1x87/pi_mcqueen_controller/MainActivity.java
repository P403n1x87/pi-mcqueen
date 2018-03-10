package com.p403n1x87.pi_mcqueen_controller;

import android.app.Activity;

import android.content.Context;

import android.hardware.SensorManager;

import android.os.Bundle;

import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.Switch;
import android.widget.Toast;
import android.view.View;

import android.util.Log;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.ArrayList;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft_17;
import org.java_websocket.handshake.ServerHandshake;

import com.p403n1x87.pi_mcqueen_controller.controller.Controller;
import com.p403n1x87.pi_mcqueen_controller.controller.Gamepad;
import com.p403n1x87.pi_mcqueen_controller.controller.RotationSensor;

public class MainActivity extends Activity
{
  private Switch          connectSwitch        = null;

  private WebSocketClient webSocketClient      = null;
  private Controller      controller           = null;
  private List<Controller> controllerList = new ArrayList<Controller>();

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    Controller rotationSensor = new RotationSensor((SensorManager) getSystemService(Context.SENSOR_SERVICE));
    if (rotationSensor.canControl()) controllerList.add(rotationSensor);

    Controller gamepad = new Gamepad(findViewById(android.R.id.content));
    if (gamepad.canControl()) controllerList.add(gamepad);

    // UI
    setContentView(R.layout.main_layout);
    if (connectSwitch == null) initializeConnectSwitch();

    if (controllerList.size() == 0) {
      Toast.makeText(getApplicationContext(), "No controllers available.", Toast.LENGTH_SHORT).show();
      connectSwitch.setEnabled(false);
      return;
    }

    addControllerList();
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

      controller.registerWithSocket(webSocketClient);
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
    controller.unregister();

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


  private void addControllerList() {
    LinearLayout controllerLayout = (LinearLayout) findViewById(R.id.layout_controllers);

    for (Controller c : controllerList) {
      RadioButton button = new RadioButton(this);
      final Controller internalController = c;
      button.setText(c.getName());
      button.setOnClickListener(new View.OnClickListener() {

        public void onClick(View v) {
          if (controller != null && controller != internalController) controller.unregister();
          controller = internalController;
        }
      });
      controllerLayout.addView(button);
    }
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
