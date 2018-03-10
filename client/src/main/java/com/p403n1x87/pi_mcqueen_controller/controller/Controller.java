package com.p403n1x87.pi_mcqueen_controller.controller;

import org.java_websocket.client.WebSocketClient;

public interface Controller {

  /**
   * Whether the controller instance is able to send control data.
   * @return {@code true} if the {@link Controller} can control; {@code false}
   *         otherwise.
   */
  public boolean canControl();

  /**
   * Return a descriptive name for the controller.
   * @return A descriptive name for the controller.
   */
  public String getName();

  /**
   * Register the {@link Controller} with a {@link WebSocketClient}. This is
   * when any necessary callback is expected to be registered with a listener.
   * @param socket The {@link WebSocketClient} instance the controller is to
   *               send control data to.
   */
  public void registerWithSocket(WebSocketClient socket);

  /**
   * Unregister the controller from the socket.
   */
  public void unregister();

}
