package com.p403n1x87.pi_mcqueen_controller.controller;

import android.view.InputDevice;
import android.view.InputDevice.MotionRange;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnGenericMotionListener;

import com.p403n1x87.pi_mcqueen_controller.controller.Controller;

import java.util.ArrayList;

import org.java_websocket.client.WebSocketClient;

public class Gamepad implements Controller {

  private final View            view;
  private       WebSocketClient socket   = null;
  private       int             deviceId = -1;

  private static float getCenteredAxis(MotionEvent event, InputDevice device, int axis, int historyPos) {
    final InputDevice.MotionRange range = device.getMotionRange(axis, event.getSource());
    if (range != null) {
      final float flat = range.getFlat();
      final float value = historyPos < 0 ? event.getAxisValue(axis) : event.getHistoricalAxisValue(axis, historyPos);
      if (Math.abs(value) > flat) return value;
    }
    return 0;
  }

  private final OnGenericMotionListener motionListener = new OnGenericMotionListener() {

    private void processJoystickInput(MotionEvent event, int historyPos) {

      InputDevice mInputDevice = event.getDevice();

      float x = getCenteredAxis(event, mInputDevice, MotionEvent.AXIS_X, historyPos);
      float y = getCenteredAxis(event, mInputDevice, MotionEvent.AXIS_RZ, historyPos);

      byte[] data = {new Float(x * 127).byteValue(), new Float(y * 127).byteValue()};

      socket.send(data);
    }

    @Override
    public boolean onGenericMotion(View v, MotionEvent event) {
      if (event.getDeviceId() == deviceId && event.getAction() == MotionEvent.ACTION_MOVE) {
        // Process all historical movement samples in the batch
        final int historySize = event.getHistorySize();
        for (int i = 0; i < historySize; processJoystickInput(event, i++));

        // Process the current movement sample in the batch (position -1)
        processJoystickInput(event, -1);
        return true;
      }
      return v.onGenericMotionEvent(event);
    }
  };


  private static ArrayList getGameControllerIds() {
    ArrayList gameControllerDeviceIds = new ArrayList();
    int[]     deviceIds               = InputDevice.getDeviceIds();

    for (int deviceId : deviceIds) {
      InputDevice dev = InputDevice.getDevice(deviceId);
      int sources     = dev.getSources();

      if (((sources & InputDevice.SOURCE_GAMEPAD)  == InputDevice.SOURCE_GAMEPAD)
       || ((sources & InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK))
      { // This device is a game controller.
        if (!gameControllerDeviceIds.contains(deviceId))
          gameControllerDeviceIds.add(deviceId);
      }
    }
    return gameControllerDeviceIds;
  }

  public Gamepad(View view) {
    try {
      this.deviceId = (int) Gamepad.getGameControllerIds().get(0);
    } catch (IndexOutOfBoundsException e) {
      // No devices connected
      this.deviceId = -1;
    }

    this.view = view;
  }

  public boolean canControl() {
    return deviceId != -1;
  }

  public String getName() {
    return "Generic Dual Gamepad";
  }

  public void registerWithSocket(WebSocketClient socket) {
    this.socket = socket;
    view.setOnGenericMotionListener(motionListener);
  }

  public void unregister() {
    view.setOnGenericMotionListener((OnGenericMotionListener) view);
  }
}
