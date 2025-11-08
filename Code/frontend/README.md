# Fish Feeder Frontend

## Overview
This is the frontend interface for the Fish Feeder automation system. The interface allows users to manually feed their fish and set up automated feeding schedules.

## Project Structure
```
frontend/
├── index.html              # Main HTML page
├── css/
│   └── styles.css          # Main stylesheet with blue theme
├── js/
│   └── app.js              # JavaScript for functionality and API calls
├── components/
│   ├── header.html         # Header component with logo and title
│   └── footer.html         # Footer component
└── assets/
    └── images/
        └── header.png      # Fish feeder logo (to be added)
```

## Setup Instructions

### 1. Add the Header Image
Save the fish feeder icon (the blue fishbowl with food dropping in) as `header.png` in the `assets/images/` directory.

### 2. Running the Frontend
You can run the frontend using any of these methods:

**Option A: Python HTTP Server**
```bash
cd /home/pi/Desktop/Feeder/Code/frontend
python3 -m http.server 8080
```
Then open http://localhost:8080 in your browser.

**Option B: Node.js HTTP Server**
```bash
npm install -g http-server
cd /home/pi/Desktop/Feeder/Code/frontend
http-server -p 8080
```

**Option C: VS Code Live Server Extension**
- Install the "Live Server" extension in VS Code
- Right-click on `index.html` and select "Open with Live Server"

## Design Features

### Color Scheme
- Primary Blue: `#2c7a9e`
- Dark Blue: `#1e5773`
- Light Blue: `#5ba4c8`
- Background: `#f5f5f5`
- White Cards: `#ffffff`

### Components

#### Header
- Blue gradient background matching the provided design
- Fish feeder logo on the left
- "Keep your Fish full" title
- Responsive design for mobile devices

#### Main Content
- **Manual Feed**: Button to trigger immediate feeding
- **Feeding Schedule**: Form to set up automated feeding times and amounts
- **Current Schedule**: List of all scheduled feeding times
- **System Status**: Shows last fed time, next feed time, and connection status

#### Footer
- Blue gradient background
- Copyright information
- Quick links
- Responsive design

## API Integration

The frontend connects to the backend API with the following endpoints:

- `POST /api/feed` - Trigger manual feeding
- `POST /api/schedule` - Create a new feeding schedule
- `GET /api/schedules` - Get all schedules
- `DELETE /api/schedule/{id}` - Delete a schedule
- `GET /api/status` - Check system status

## Features

1. **Manual Feeding**: Click "Feed Now" to dispense food immediately
2. **Schedule Management**: Set up multiple feeding times with custom amounts
3. **Real-time Status**: Connection status updates every 30 seconds
4. **Responsive Design**: Works on desktop, tablet, and mobile devices
5. **Modern UI**: Clean, professional interface with smooth animations

## Browser Compatibility
- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## Notes
- The frontend uses vanilla JavaScript (no frameworks required)
- Components are loaded dynamically using the Fetch API
- All styling is done with CSS3 (no preprocessors needed)
- The design matches the provided mockup with the blue theme
