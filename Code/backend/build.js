// -----------------------------------------------------------------------------
// To refresh Microdot files from upstream, run the following commands:
//
// curl -o microdot.py https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot.py
// curl -o microdot_asyncio.py https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot_asyncio.py
// curl -o microdot_utils.py https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot_utils.py
// curl -o microdot_websocket.py https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot_websocket.py
// curl -o microdot_utemplate.py https://raw.githubusercontent.com/miguelgrinberg/microdot-utemplate/main/src/microdot_utemplate.py
// -----------------------------------------------------------------------------
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Determine build mode from command line argument
const mode = process.argv[2] || 'api'; // 'battery' or 'api' (default)

const distDir = path.join(__dirname, 'dist');
const frontendDir = path.join(__dirname, '..', 'frontend');
const frontendDistDir = path.join(frontendDir, 'dist');


// Data files (empty templates for API mode)
const dataFiles = [
  { name: 'data/schedule.txt', content: 'times=\ndays=' },
  { name: 'data/last_fed.txt', content: '' },
  { name: 'data/next_feed.txt', content: 'Not scheduled' },
  { name: 'data/quantity.txt', content: '10' }
];

// UI directory (copy as is for API mode)
const uiDir = 'UI';

function createDirectory(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
}

function copyFile(src, dest) {
  try {
    const destDir = path.dirname(dest);
    createDirectory(destDir);
    
    fs.copyFileSync(src, dest);
    console.log(`Copied: ${src} -> ${dest}`);
  } catch (error) {
    console.error(`Error copying ${src}: ${error.message}`);
  }
}

function copyDirectory(src, dest) {
  createDirectory(dest);
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      copyFile(srcPath, destPath);
    }
  }
}

function createDataFile(filePath, content) {
  const fullPath = path.join(distDir, filePath);
  const dir = path.dirname(fullPath);
  
  createDirectory(dir);
  fs.writeFileSync(fullPath, content);
  console.log(`Created: ${filePath}`);
}

function buildFrontend() {
  console.log('\n📦 Building frontend project...\n');
  
  // Check if frontend directory exists
  if (!fs.existsSync(frontendDir)) {
    console.warn('⚠️  Warning: Frontend directory not found, skipping frontend build');
    return false;
  }
  
  try {
    // Build frontend
    execSync('npm run build', { cwd: frontendDir, stdio: 'inherit' });
    console.log('\n✅ Frontend build complete\n');
    return true;
  } catch (error) {
    console.error('❌ Frontend build failed:', error.message);
    return false;
  }
}

function copyFrontendToUI() {
  console.log('📁 Copying frontend dist to backend UI...\n');
  
  const uiDir = path.join(__dirname, 'UI');
  
  // Remove existing UI directory
  if (fs.existsSync(uiDir)) {
    fs.rmSync(uiDir, { recursive: true, force: true });
  }
  
  // Copy frontend dist to UI
  if (fs.existsSync(frontendDistDir)) {
    copyDirectory(frontendDistDir, uiDir);
    console.log('✅ Frontend copied to UI directory\n');
    return true;
  } else {
    console.warn('⚠️  Warning: Frontend dist not found, skipping copy');
    return false;
  }
}

function build() {
  console.log(`\n🚀 Building Fish Feeder - ${mode.toUpperCase()} mode...\n`);
  
  // Step 1: Build frontend (for API mode only)
  if (mode === 'api') {
    const frontendBuilt = buildFrontend();
    if (frontendBuilt) {
      copyFrontendToUI();
    }
  }
  
  console.log('\n🔧 Building backend...\n');
  
  // Clean dist directory
  if (fs.existsSync(distDir)) {
    fs.rmSync(distDir, { recursive: true, force: true });
    console.log('Cleaned dist directory\n');
  }
  
  createDirectory(distDir);
  




  // Copy all .py files from backend and subfolders to dist, preserving structure
  // Exclude microdot files and dist folder itself
  const excludeFiles = ['api_old.py', 'test_gpio.py', 'test_servo.py', 'test_scheduler.py'];
  const excludeDirs = ['dist', 'node_modules', '__pycache__'];

  function copyAllPyFiles(srcDir, destDir, relPath = '') {
    const entries = fs.readdirSync(srcDir, { withFileTypes: true });
    for (const entry of entries) {
      const srcPath = path.join(srcDir, entry.name);
      const destPath = path.join(destDir, relPath, entry.name);

      if (entry.isDirectory()) {
        // Skip excluded directories
        if (excludeDirs.includes(entry.name)) {
          continue;
        }
        copyAllPyFiles(srcPath, destDir, path.join(relPath, entry.name));
      } else if (entry.name.endsWith('.py')) {
        // Skip excluded files
        if (excludeFiles.includes(entry.name)) {
          continue;
        }
        copyFile(srcPath, destPath);
      } else if (relPath === 'ota' && (entry.name.endsWith('.json') || entry.name.endsWith('.md'))) {
        // Copy JSON and MD files from ota directory
        copyFile(srcPath, destPath);
      }
    }
  }
  copyAllPyFiles(__dirname, distDir);

  // Explicitly copy all microdot*.py files from backend root to dist
  const microdotFiles = fs.readdirSync(__dirname).filter(f => f.startsWith('microdot') && f.endsWith('.py'));
  for (const f of microdotFiles) {
    copyFile(path.join(__dirname, f), path.join(distDir, f));
  }
  
  // Ensure wifi.dat is always copied if it exists
  const wifiDatSrc = path.join(__dirname, 'wifi.dat');
  const wifiDatDest = path.join(distDir, 'wifi.dat');
  if (fs.existsSync(wifiDatSrc)) {
    copyFile(wifiDatSrc, wifiDatDest);
  }

  // For API mode, copy UI directory and create/copy data files into dist
  if (mode === 'api') {
    console.log('\n📁 Copying UI directory...\n');
    const uiSrc = path.join(__dirname, uiDir);
    const uiDest = path.join(distDir, uiDir);
    if (fs.existsSync(uiSrc)) {
      copyDirectory(uiSrc, uiDest);
    } else {
      console.warn(`⚠️  Warning: ${uiDir} directory not found`);
    }

    console.log('\n📝 Copying/Creating data files...\n');
    const dataDir = path.join(__dirname, 'data');
    const dataDestDir = path.join(distDir, 'data');
    // Copy data directory if it exists, otherwise create defaults
    if (fs.existsSync(dataDir)) {
      console.log('Found existing data directory, copying...');
      copyDirectory(dataDir, dataDestDir);
    } else {
      console.log('No existing data directory, creating defaults...');
      dataFiles.forEach(file => {
        createDataFile(file.name, file.content);
      });
    }
  }
  
  // Create README in dist
  const readmeContent = `# Fish Feeder - ${mode.toUpperCase()} Mode Deployment

This directory contains all files needed for ESP8266 deployment in ${mode} mode.

## Files included:
All Python files from the backend directory, including lib/ and ota/ folders

${mode === 'api' ? `
## Additional directories:
- UI/ (complete web interface)
- data/ (JSON persistence files)

## Deployment:
Upload all files to ESP8266 maintaining the directory structure.
The api.py will serve the UI files and handle API requests.
` : `
## Deployment:
Upload all files to ESP8266 maintaining the directory structure.
The main.py will run on boot and handle scheduled feedings.
`}

## Upload commands (using ampy):
\`\`\`bash
# Set your COM port
$PORT = "COM3"

${mode === 'battery' ? `
# Upload main files
ampy --port $PORT put main.py
ampy --port $PORT put config.py

# Create lib directory and upload drivers
ampy --port $PORT mkdir lib
ampy --port $PORT put lib/stepper.py lib/stepper.py
ampy --port $PORT put lib/rtc_handler.py lib/rtc_handler.py
ampy --port $PORT put lib/notification.py lib/notification.py
` : `
# Upload main files
ampy --port $PORT put api.py
ampy --port $PORT put config.py
ampy --port $PORT put services.py
ampy --port $PORT put last_fed_service.py
ampy --port $PORT put next_feed_service.py
ampy --port $PORT put quantity_service.py
ampy --port $PORT put microdot.py
ampy --port $PORT put urequests.py

# Create lib directory and upload drivers
ampy --port $PORT mkdir lib
ampy --port $PORT put lib/stepper.py lib/stepper.py
ampy --port $PORT put lib/rtc_handler.py lib/rtc_handler.py
ampy --port $PORT put lib/notification.py lib/notification.py

# Create data directory and upload data files
ampy --port $PORT mkdir data
ampy --port $PORT put data/schedule.json data/schedule.json
ampy --port $PORT put data/last_fed.json data/last_fed.json
ampy --port $PORT put data/next_feed.json data/next_feed.json
ampy --port $PORT put data/quantity.json data/quantity.json

# Upload UI directory (you may need to upload each file individually)
ampy --port $PORT mkdir UI
ampy --port $PORT put UI/index.html UI/index.html
ampy --port $PORT put UI/feednow.html UI/feednow.html
ampy --port $PORT put UI/setquantity.html UI/setquantity.html
ampy --port $PORT put UI/setschedule.html UI/setschedule.html
ampy --port $PORT mkdir UI/css
ampy --port $PORT put UI/css/styles.css UI/css/styles.css
ampy --port $PORT mkdir UI/assets
ampy --port $PORT mkdir UI/assets/images
# Add image files as needed
`}
\`\`\`

Generated on: ${new Date().toISOString()}
`;
  
  fs.writeFileSync(path.join(distDir, 'README.md'), readmeContent);
  console.log('\n📄 Created README.md\n');
  
  console.log(`✅ Build complete! Files are in: ${distDir}\n`);
  console.log(`📊 Total files: ${countFiles(distDir)}`);
  console.log(`📦 Total size: ${getDirectorySize(distDir)} bytes\n`);
}

function countFiles(dir) {
  let count = 0;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    if (entry.isDirectory()) {
      count += countFiles(path.join(dir, entry.name));
    } else {
      count++;
    }
  }
  
  return count;
}

function getDirectorySize(dir) {
  let size = 0;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      size += getDirectorySize(fullPath);
    } else {
      size += fs.statSync(fullPath).size;
    }
  }
  
  return size;
}

// Run the build
build();
