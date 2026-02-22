---
name: browse
description: Visually inspect InCube Portal using agent-browser. Take screenshots, check responsive design, test forms, verify UI elements against local or production URLs.
allowed-tools: Bash(agent-browser *), Bash(npx agent-browser*)
---

# Browse InCube Portal with Agent Browser

Use this skill to visually inspect the InCube Portal, check UI elements, verify agent responses, and test interactions using the agent-browser CLI tool.

## Project URLs

| Project | Local URL | Production URL |
|---------|-----------|----------------|
| **Backend API** | http://localhost:8000/docs | https://incube.motionmind.antikythera.co.za/api/docs |
| **Frontend** | http://localhost:3001 | https://incube.motionmind.antikythera.co.za |

## Quick Start

```bash
# Open the local frontend
agent-browser open http://localhost:3001

# Take a screenshot
agent-browser screenshot /tmp/page.png

# Get accessibility snapshot (element refs for clicking)
agent-browser snapshot -i

# Close browser when done
agent-browser close
```

## Common Workflows

### 1. Visual Inspection of Dashboard

```bash
# Open dashboard
agent-browser open http://localhost:3001

# Full page screenshot
agent-browser screenshot --full /tmp/dashboard-full.png

# Screenshot of specific section
agent-browser scroll down 800
agent-browser screenshot /tmp/canvas-section.png
```

### 2. Navigate and Inspect Pages

```bash
# Navigate to different pages
agent-browser open http://localhost:3001/dashboard
agent-browser open http://localhost:3001/canvas
agent-browser open http://localhost:3001/bank
agent-browser open http://localhost:3001/vdbas
agent-browser open http://localhost:3001/fundamentals
agent-browser open http://localhost:3001/settings

# Get page title
agent-browser get title

# Get current URL
agent-browser get url
```

### 3. Test Interactive Elements

```bash
# Get interactive elements snapshot
agent-browser snapshot -i

# Click element by ref (from snapshot output)
agent-browser click @e5

# Fill form field
agent-browser fill @e3 "test@example.com"

# Click submit button
agent-browser find role button click --name "Submit"
```

### 4. Check Responsive Design

```bash
# Desktop viewport
agent-browser set viewport 1920 1080
agent-browser screenshot /tmp/desktop.png

# Tablet viewport
agent-browser set viewport 768 1024
agent-browser screenshot /tmp/tablet.png

# Mobile viewport
agent-browser set viewport 375 812
agent-browser screenshot /tmp/mobile.png
```

### 5. Test Dark/Light Mode

```bash
# Force dark mode
agent-browser set media dark
agent-browser screenshot /tmp/dark-mode.png

# Force light mode
agent-browser set media light
agent-browser screenshot /tmp/light-mode.png
```

### 6. Test API Documentation

```bash
# Open Swagger UI
agent-browser open http://localhost:8000/docs
agent-browser screenshot --full /tmp/api-docs.png
```

---

## Complete CLI Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open <url>` | Navigate to URL | `agent-browser open http://localhost:3001` |
| `click <sel>` | Click element (CSS selector or @ref) | `agent-browser click @e2` |
| `dblclick <sel>` | Double-click element | `agent-browser dblclick "#button"` |
| `type <sel> <text>` | Type into element | `agent-browser type "#search" "query"` |
| `fill <sel> <text>` | Clear and fill input | `agent-browser fill "#email" "test@test.com"` |
| `press <key>` | Press keyboard key | `agent-browser press Enter` |
| `hover <sel>` | Hover over element | `agent-browser hover ".menu-item"` |
| `focus <sel>` | Focus element | `agent-browser focus "#input"` |
| `check <sel>` | Check checkbox | `agent-browser check "#terms"` |
| `uncheck <sel>` | Uncheck checkbox | `agent-browser uncheck "#newsletter"` |
| `select <sel> <val>` | Select dropdown option | `agent-browser select "#country" "US"` |
| `drag <src> <dst>` | Drag and drop | `agent-browser drag "#item" "#target"` |
| `upload <sel> <files>` | Upload files | `agent-browser upload "#file" ./doc.pdf` |
| `scroll <dir> [px]` | Scroll page | `agent-browser scroll down 500` |
| `scrollintoview <sel>` | Scroll element into view | `agent-browser scrollintoview "#footer"` |
| `wait <sel\|ms>` | Wait for element/time | `agent-browser wait "#modal"` or `wait 2000` |
| `screenshot [path]` | Take screenshot | `agent-browser screenshot /tmp/screen.png` |
| `pdf <path>` | Save page as PDF | `agent-browser pdf /tmp/page.pdf` |
| `snapshot` | Get accessibility tree with refs | `agent-browser snapshot -i` |
| `eval <js>` | Run JavaScript | `agent-browser eval "document.title"` |
| `close` | Close browser | `agent-browser close` |

### Navigation

| Command | Description |
|---------|-------------|
| `back` | Go back in history |
| `forward` | Go forward in history |
| `reload` | Reload current page |

### Get Information

```bash
agent-browser get <what> [selector]
```

| What | Description | Example |
|------|-------------|---------|
| `text` | Get text content | `agent-browser get text "#heading"` |
| `html` | Get innerHTML | `agent-browser get html "#content"` |
| `value` | Get input value | `agent-browser get value "#email"` |
| `attr <name>` | Get attribute | `agent-browser get attr href "a.link"` |
| `title` | Get page title | `agent-browser get title` |
| `url` | Get current URL | `agent-browser get url` |
| `count` | Count elements | `agent-browser get count ".card"` |
| `box` | Get bounding box | `agent-browser get box "#element"` |
| `styles` | Get computed styles | `agent-browser get styles "#element"` |

### Check State

```bash
agent-browser is <what> <selector>
```

| What | Description | Example |
|------|-------------|---------|
| `visible` | Check if visible | `agent-browser is visible "#modal"` |
| `enabled` | Check if enabled | `agent-browser is enabled "#submit"` |
| `checked` | Check if checked | `agent-browser is checked "#terms"` |

### Find Elements (Semantic Locators)

```bash
agent-browser find <locator> <value> <action> [options]
```

| Locator | Description | Example |
|---------|-------------|---------|
| `role` | By ARIA role | `agent-browser find role button click --name "Submit"` |
| `text` | By text content | `agent-browser find text "Sign In" click` |
| `label` | By label text | `agent-browser find label "Email" fill "test@test.com"` |
| `placeholder` | By placeholder | `agent-browser find placeholder "Search..." type "query"` |
| `alt` | By alt text | `agent-browser find alt "Logo" click` |
| `title` | By title attr | `agent-browser find title "Close" click` |
| `testid` | By data-testid | `agent-browser find testid "submit-btn" click` |
| `first` | First matching | `agent-browser find first ".card" click` |
| `last` | Last matching | `agent-browser find last ".card" click` |
| `nth` | Nth matching | `agent-browser find nth 3 ".card" click` |

### Mouse Actions

```bash
agent-browser mouse <action> [args]
```

| Action | Description | Example |
|--------|-------------|---------|
| `move <x> <y>` | Move mouse | `agent-browser mouse move 100 200` |
| `down [btn]` | Mouse button down | `agent-browser mouse down left` |
| `up [btn]` | Mouse button up | `agent-browser mouse up` |
| `wheel <dy> [dx]` | Scroll wheel | `agent-browser mouse wheel 100` |

### Browser Settings

```bash
agent-browser set <setting> [value]
```

| Setting | Description | Example |
|---------|-------------|---------|
| `viewport <w> <h>` | Set window size | `agent-browser set viewport 1920 1080` |
| `device <name>` | Emulate device | `agent-browser set device "iPhone 14"` |
| `geo <lat> <lng>` | Set geolocation | `agent-browser set geo 37.7749 -122.4194` |
| `offline [on\|off]` | Toggle offline | `agent-browser set offline on` |
| `headers <json>` | Set HTTP headers | `agent-browser set headers '{"Auth":"token"}'` |
| `credentials <u> <p>` | HTTP auth | `agent-browser set credentials user pass` |
| `media [scheme]` | Color scheme | `agent-browser set media dark` |

### Network Control

```bash
agent-browser network <action>
```

| Action | Description | Example |
|--------|-------------|---------|
| `route <url> [opts]` | Intercept requests | `agent-browser network route "**/api/*" --abort` |
| `unroute [url]` | Remove route | `agent-browser network unroute` |
| `requests [opts]` | View requests | `agent-browser network requests --filter "api"` |

### Storage

| Command | Description | Example |
|---------|-------------|---------|
| `cookies` | Get all cookies | `agent-browser cookies` |
| `cookies set <n> <v>` | Set cookie | `agent-browser cookies set token abc123` |
| `cookies clear` | Clear cookies | `agent-browser cookies clear` |
| `storage local` | Get localStorage | `agent-browser storage local` |
| `storage session` | Get sessionStorage | `agent-browser storage session` |

### Tabs

| Command | Description |
|---------|-------------|
| `tab new` | Open new tab |
| `tab list` | List open tabs |
| `tab close` | Close current tab |
| `tab <n>` | Switch to tab n |

### Debug & Recording

| Command | Description | Example |
|---------|-------------|---------|
| `trace start` | Start trace recording | `agent-browser trace start` |
| `trace stop [path]` | Stop and save trace | `agent-browser trace stop /tmp/trace.zip` |
| `record start <path>` | Start video recording | `agent-browser record start /tmp/video.webm` |
| `record stop` | Stop recording | `agent-browser record stop` |
| `console` | View console logs | `agent-browser console` |
| `errors` | View page errors | `agent-browser errors` |
| `highlight <sel>` | Highlight element | `agent-browser highlight "#button"` |

### Sessions

```bash
# Use isolated sessions for different projects
agent-browser --session incube-frontend open http://localhost:3001
agent-browser --session incube-api open http://localhost:8000/docs

# List active sessions
agent-browser session list

# Show current session
agent-browser session
```

### Global Options

| Option | Description |
|--------|-------------|
| `--session <name>` | Use isolated browser session |
| `--headers <json>` | Set HTTP headers for requests |
| `--headed` | Show browser window (not headless) |
| `--full, -f` | Full page screenshot |
| `--json` | Output in JSON format |
| `--debug` | Enable debug output |
| `--proxy <url>` | Use proxy server |

### Snapshot Options

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Only show interactive elements |
| `-c, --compact` | Remove empty structural elements |
| `-d, --depth <n>` | Limit tree depth |
| `-s, --selector <sel>` | Scope to CSS selector |

---

## InCube Portal Testing

### Test All App Routes

```bash
# Auth pages
agent-browser open http://localhost:3001/login
agent-browser screenshot --full /tmp/login.png

agent-browser open http://localhost:3001/register
agent-browser screenshot --full /tmp/register.png

# App pages (requires auth)
agent-browser open http://localhost:3001/dashboard
agent-browser screenshot --full /tmp/dashboard.png

agent-browser open http://localhost:3001/canvas
agent-browser screenshot --full /tmp/canvas.png

agent-browser open http://localhost:3001/bank
agent-browser screenshot --full /tmp/bank.png

agent-browser open http://localhost:3001/vdbas
agent-browser screenshot --full /tmp/vdbas.png

agent-browser open http://localhost:3001/fundamentals
agent-browser screenshot --full /tmp/fundamentals.png

agent-browser open http://localhost:3001/settings
agent-browser screenshot --full /tmp/settings.png
```

### Test Production Site

```bash
agent-browser open https://incube.motionmind.antikythera.co.za
agent-browser screenshot --full /tmp/prod-incube.png
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AGENT_BROWSER_SESSION` | Default session name |
| `AGENT_BROWSER_EXECUTABLE_PATH` | Custom browser path |
| `AGENT_BROWSER_STREAM_PORT` | WebSocket streaming port |

## Troubleshooting

### Browser fails to launch on Linux

```bash
agent-browser install --with-deps
# or
npx playwright install-deps chromium
```

### View browser window for debugging

```bash
agent-browser --headed open http://localhost:3001
```

### Check for console errors

```bash
agent-browser open http://localhost:3001
agent-browser errors
agent-browser console
```
