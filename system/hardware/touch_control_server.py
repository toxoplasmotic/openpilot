#!/usr/bin/env python3
"""
Simple HTTP server for controlling touch input on Comma 3 devices.
Provides endpoints to enable/disable touch input via the DisableTouchInput parameter.
"""

import argparse
from aiohttp import web
from openpilot.common.params import Params


async def get_touch_status(request: web.Request) -> web.Response:
  """Get current touch input status."""
  try:
    params = Params()
    disabled = params.get_bool("DisableTouchInput")
    return web.json_response({
      "success": True,
      "touch_disabled": disabled,
      "touch_enabled": not disabled
    })
  except Exception as e:
    return web.json_response({"success": False, "error": str(e)}, status=500)


async def set_touch_status(request: web.Request) -> web.Response:
  """Enable or disable touch input."""
  try:
    data = await request.json()
    params = Params()

    if "disable" in data:
      # Set DisableTouchInput to the specified value
      disable_value = bool(data["disable"])
      params.put_bool("DisableTouchInput", disable_value)
      action = "disabled" if disable_value else "enabled"
    elif "enable" in data:
      # Set DisableTouchInput to the opposite of enable
      enable_value = bool(data["enable"])
      params.put_bool("DisableTouchInput", not enable_value)
      action = "enabled" if enable_value else "disabled"
    else:
      return web.json_response({
        "success": False,
        "error": "Must provide 'disable' or 'enable' parameter"
      }, status=400)

    return web.json_response({
      "success": True,
      "message": f"Touch input {action}",
      "touch_disabled": params.get_bool("DisableTouchInput")
    })
  except Exception as e:
    return web.json_response({"success": False, "error": str(e)}, status=500)


async def health_check(request: web.Request) -> web.Response:
  """Simple health check endpoint."""
  return web.json_response({"status": "ok", "service": "touch_control"})


def create_app() -> web.Application:
  """Create the aiohttp application with routes."""
  app = web.Application()
  app.router.add_get("/health", health_check)
  app.router.add_get("/touch/status", get_touch_status)
  app.router.add_post("/touch/set", set_touch_status)
  return app


def main():
  parser = argparse.ArgumentParser(description="Touch Control HTTP Server")
  parser.add_argument("--host", type=str, default="0.0.0.0",
                      help="Host to listen on (default: 0.0.0.0)")
  parser.add_argument("--port", type=int, default=5002,
                      help="Port to listen on (default: 5002)")
  args = parser.parse_args()

  app = create_app()
  print(f"Starting Touch Control Server on {args.host}:{args.port}")
  print("Endpoints:")
  print(f"  GET  http://{args.host}:{args.port}/health - Health check")
  print(f"  GET  http://{args.host}:{args.port}/touch/status - Get touch status")
  print(f"  POST http://{args.host}:{args.port}/touch/set - Enable/disable touch")
  print("\nExample usage:")
  print(f"  curl http://localhost:{args.port}/touch/status")
  print(f"  curl -X POST http://localhost:{args.port}/touch/set -H 'Content-Type: application/json' -d '{{\"disable\": true}}'")
  print(f"  curl -X POST http://localhost:{args.port}/touch/set -H 'Content-Type: application/json' -d '{{\"enable\": true}}'")

  web.run_app(app, host=args.host, port=args.port, access_log=None)


if __name__ == "__main__":
  main()
