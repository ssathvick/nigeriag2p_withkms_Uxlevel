"""Drain due synthetic callbacks. Invoked by the systemd timer."""
import registration_app as r
r.simulation_tick()
