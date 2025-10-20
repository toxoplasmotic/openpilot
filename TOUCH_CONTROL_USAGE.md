# Touch Input Control for Comma 3

This solution allows you to enable/disable touch input on your Comma 3 device via HTTP endpoints. This is useful when you have a damaged touchscreen that registers phantom touches.

## How It Works

1. **Modified hardwared.py**: The touch event thread now checks the `DisableTouchInput` parameter before publishing touch events
2. **HTTP Server**: A simple aiohttp server (`touch_control_server.py`) provides REST endpoints to toggle this parameter

## Setup

### Starting the Touch Control Server

On your Comma 3 device, run:

```bash
cd /data/openpilot
python3 system/hardware/touch_control_server.py
```

The server will start on port 5002 by default. You can customize the port:

```bash
python3 system/hardware/touch_control_server.py --port 8080
```

### Make it Persistent (Optional)

To have the server start automatically, you could add it as a systemd service or run it in the background:

```bash
nohup python3 system/hardware/touch_control_server.py > /tmp/touch_control.log 2>&1 &
```

## Usage

Once the server is running, you can control touch input from any device on the same network as your Comma 3.

### Check Touch Status

```bash
curl http://<comma3-ip>:5002/touch/status
```

Response:
```json
{
  "success": true,
  "touch_disabled": false,
  "touch_enabled": true
}
```

### Disable Touch Input

```bash
curl -X POST http://<comma3-ip>:5002/touch/set \
  -H 'Content-Type: application/json' \
  -d '{"disable": true}'
```

Response:
```json
{
  "success": true,
  "message": "Touch input disabled",
  "touch_disabled": true
}
```

### Enable Touch Input

```bash
curl -X POST http://<comma3-ip>:5002/touch/set \
  -H 'Content-Type: application/json' \
  -d '{"enable": true}'
```

Response:
```json
{
  "success": true,
  "message": "Touch input enabled",
  "touch_disabled": false
}
```

### Health Check

```bash
curl http://<comma3-ip>:5002/health
```

Response:
```json
{
  "status": "ok",
  "service": "touch_control"
}
```

## Finding Your Comma 3 IP Address

On your Comma 3, you can find the IP address by:

1. Go to Settings > Network
2. Or via SSH: `ifconfig wlan0 | grep inet`

## Alternative: Direct Parameter Control

If you have SSH access, you can also toggle touch input directly using the params command:

```bash
# Disable touch
echo -n "1" | /data/params/d/DisableTouchInput

# Enable touch
rm /data/params/d/DisableTouchInput
```

Or using the Params API in Python:

```python
from openpilot.common.params import Params
params = Params()

# Disable touch
params.put_bool("DisableTouchInput", True)

# Enable touch
params.put_bool("DisableTouchInput", False)
```

## Important Notes

- The touch input state change takes effect immediately (within ~50ms)
- Touch events are still read from the hardware but are simply not published when disabled
- This does not affect the display or any other functionality
- Restarting `hardwared` service will reset to the current parameter value
- The parameter persists across reboots

## Troubleshooting

**Touch is still registering after disabling:**
- Verify the parameter is set: `cat /data/params/d/DisableTouchInput` should show `1`
- Restart hardwared: `sudo systemctl restart hardwared`

**Server won't start:**
- Check if port 5002 is already in use: `netstat -tuln | grep 5002`
- Try a different port: `python3 system/hardware/touch_control_server.py --port 8080`

**Can't reach the server:**
- Ensure your device is on the same network as the Comma 3
- Check firewall settings if using a custom port
- Verify the server is running: `ps aux | grep touch_control_server`
