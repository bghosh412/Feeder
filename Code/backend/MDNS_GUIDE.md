# mDNS Configuration Guide

## What is mDNS?

mDNS (Multicast DNS) allows you to access your Fish Feeder using a friendly hostname like `fishfeeder.local` instead of remembering the IP address.

## Configuration

The hostname is configured in `config.py`:

```python
# mDNS/Hostname Configuration
MDNS_HOSTNAME = "fishfeeder"  # Access via http://fishfeeder.local
MDNS_SERVICE_NAME = "Fish Feeder Device"
```

You can change `MDNS_HOSTNAME` to any name you prefer (use lowercase, no spaces).

## How It Works

### ESP32 (Full mDNS Support)
- ESP32 has built-in mDNS library
- Automatically advertises the service on the network
- Access your feeder at: `http://fishfeeder.local`

### ESP8266 (DHCP Hostname)
- ESP8266 doesn't have native mDNS in MicroPython
- Uses DHCP hostname registration instead
- Most modern routers will resolve: `http://fishfeeder.local`
- May not work on all networks/routers

## Accessing Your Fish Feeder

Once deployed and connected to WiFi, you can access the web interface using:

1. **By hostname (recommended):**
   ```
   http://fishfeeder.local
   ```

2. **By IP address (fallback):**
   ```
   http://192.168.1.XXX
   ```
   (Check serial console for the actual IP address)

## Troubleshooting

### Hostname Not Resolving

If `fishfeeder.local` doesn't work:

1. **Check your device supports mDNS:**
   - Windows: Install [Bonjour Print Services](https://support.apple.com/kb/DL999) or use iTunes
   - macOS: Built-in support ✅
   - Linux: Install `avahi-daemon` (usually pre-installed)
   - iOS/Android: Built-in support ✅

2. **Use IP address instead:**
   - Check serial console output after boot
   - Look for: `Connected to WiFi. IP: 192.168.1.XXX`
   - Access via: `http://192.168.1.XXX`

3. **Check same network:**
   - Your device must be on the same WiFi network as the ESP32/ESP8266

4. **Restart the device:**
   - Power cycle the ESP32/ESP8266
   - Wait 10-15 seconds for WiFi connection and mDNS to start

### Multiple Devices

If you have multiple fish feeders, give each one a unique hostname:

```python
# Device 1: fishfeeder.local
MDNS_HOSTNAME = "fishfeeder"

# Device 2: fishfeeder2.local
MDNS_HOSTNAME = "fishfeeder2"

# Device 3: aquarium1.local
MDNS_HOSTNAME = "aquarium1"
```

## Network Compatibility

### Works Well:
- ✅ Most home routers
- ✅ Modern WiFi access points
- ✅ Local networks without strict firewall rules

### May Not Work:
- ❌ Corporate/Enterprise networks with mDNS filtering
- ❌ Public WiFi networks
- ❌ Networks with client isolation enabled
- ❌ Very old routers (pre-2010)

### Fallback Strategy:
Always use IP address if hostname doesn't resolve. The IP is printed on boot and can be found on your router's DHCP client list.

## Port Number

The API server runs on port **80** (standard HTTP port). No need to specify the port in your URL:
- ✅ `http://fishfeeder.local`
- ✅ `http://192.168.1.XXX`

## Benefits of mDNS

1. **Easy to remember:** No need to memorize IP addresses
2. **Dynamic IP friendly:** Works even if your router assigns a new IP
3. **Multiple devices:** Easy to manage multiple feeders with different names
4. **Mobile friendly:** Works great on phones and tablets
5. **Bookmark-able:** Save the hostname in browser bookmarks

## Technical Details

- Protocol: mDNS (Multicast DNS)
- Service Type: `_http._tcp`
- Port: 80 (standard HTTP)
- Domain: `.local`
- Multicast Address: 224.0.0.251 (IPv4)
