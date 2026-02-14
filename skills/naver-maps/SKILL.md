---
name: naver-maps
description: Naver Cloud Platform Maps API integration helper for React + Vite projects. Covers NCP console setup, SDK loading, map component patterns, marker/overlay APIs, and common pitfalls. Use when adding or modifying Naver Maps features, debugging map rendering issues, or setting up NCP credentials. Triggers include naver map, naver maps, NCP maps, map marker, map overlay, ncpKeyId, map tiles, map component, marker.
---

# Naver Cloud Platform Maps API - Helper Skill

## NCP Console Setup

### 1. Service Registration (Critical Path)

> Register under **Application Services > Maps**.
> NOT the "AI·NAVER API" category! Easy to confuse — be careful.

1. Go to [NCP Console](https://console.ncloud.com)
2. Navigate to **Console > Services > Application Services > Maps**
3. Click "Apply for use" (first time only)
4. **Register Application** > Select Web Dynamic Map

### 2. Authentication Key

1. My Page > Authentication Key Management > Check **NCP Authentication Key**
2. Copy the `ncpKeyId` value (different from Access Key ID!)

### 3. Web Service URL Registration (Required)

- **Register host only, exclude port**
  - `http://localhost` (O)
  - `http://localhost:7842` (X) — API calls rejected even if registered
  - `https://yourdomain.com` (O)
- Register both dev and production URLs

## SDK Loading

### Script Tag (Vite Environment)

```html
<!-- web/index.html -->
<head>
  <script src="https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=%VITE_NAVER_MAP_CLIENT_ID%"></script>
</head>
```

### SDK Parameter Warning

| Version | Parameter | Note |
|---------|-----------|------|
| Legacy | `clientId` | No longer used |
| Intermediate | `ncpClientId` | Still in some docs |
| **Current (v3)** | **`ncpKeyId`** | **Use this only** |

> If AI suggests `ncpClientId`, **ignore and replace with `ncpKeyId`**.
> Using legacy parameters results in "Unauthorized" or blank map.

### Environment Variables

```bash
# .local/.env (gitignored)
VITE_NAVER_MAP_CLIENT_ID=your_ncp_key_id_here
```

Vite config points `envDir` to `.local/`:
```ts
// web/vite.config.ts
export default defineConfig({
  envDir: path.resolve(__dirname, '..', '.local'),
})
```

### SDK Readiness Polling

SDK loads synchronously from `<head>`, but poll for safety:

```tsx
useEffect(() => {
  const interval = setInterval(() => {
    if (window.naver?.maps) {
      clearInterval(interval);
      initMap();
    }
  }, 100);
  return () => clearInterval(interval);
}, []);
```

## Map Container Styling (Critical)

### Must Use Inline Style

```tsx
// GOOD - always do this
<div
  ref={mapRef}
  className="naver-map"
  style={{ width: '100%', height: '100%' }}
/>

// BAD - tile rendering fails
<div ref={mapRef} className="absolute inset-0" />
<div ref={mapRef} className="w-full h-full" />
```

> Naver Maps SDK fails to calculate tile size in absolute-positioned containers.
> Tailwind classes (`w-full h-full`) are also unstable due to SDK internal timing.
> **Only inline styles work reliably.**

### Tailwind Preflight Conflict Fix

Tailwind's default reset (`img { max-width: 100% }`) breaks map tiles:

```css
/* web/src/index.css */
.naver-map img {
  max-width: none;
}
```

## Map Initialization Pattern

```tsx
const initMap = () => {
  const map = new window.naver.maps.Map(mapRef.current, {
    center: new window.naver.maps.LatLng(36.5, 127.5), // Korea center
    zoom: 7,
    minZoom: 6,
    maxZoom: 19,
    zoomControl: true,
    zoomControlOptions: {
      position: window.naver.maps.Position.TOP_RIGHT,
    },
  });

  // Track bounds via idle event
  window.naver.maps.Event.addListener(map, 'idle', () => {
    const bounds = map.getBounds();
    const center = map.getCenter();
    const zoom = map.getZoom();
    // update state...
  });

  mapInstanceRef.current = map;
};
```

## Marker API

### Basic Marker

```tsx
const marker = new window.naver.maps.Marker({
  position: new window.naver.maps.LatLng(lat, lng),
  map: mapInstance,
  icon: {
    content: `<div style="...">Custom HTML</div>`,
    anchor: new window.naver.maps.Point(15, 15),
  },
});

window.naver.maps.Event.addListener(marker, 'click', () => {
  // click handler
});
```

### SVG Marker (Dynamic Size)

```tsx
const size = Math.max(30, Math.min(80, count * 2));
const icon = {
  content: `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 2}"
        fill="rgba(59,130,246,0.6)" stroke="#2563eb" stroke-width="2"/>
      <text x="50%" y="50%" text-anchor="middle" dy=".35em"
        fill="white" font-size="${size * 0.3}px" font-weight="bold">
        ${count}
      </text>
    </svg>`,
  anchor: new window.naver.maps.Point(size/2, size/2),
};
```

### Marker Cleanup (Prevent Memory Leaks)

```tsx
// Remove existing markers before creating new ones
markersRef.current.forEach(m => m.setMap(null));
markersRef.current = [];
```

## InfoWindow

```tsx
const infoWindow = new window.naver.maps.InfoWindow({
  content: `<div style="padding:10px;">Content</div>`,
  borderWidth: 0,
  backgroundColor: 'transparent',
  disableAnchor: true,
});

infoWindow.open(mapInstance, marker);
// Or directly on coordinates: infoWindow.open(mapInstance, latLng);
```

## Zoom-Level Branching Pattern

```tsx
const zoom = map.getZoom();

if (zoom >= 13) {
  // Show individual markers
  renderShopMarkers(shops);
} else if (zoom >= 8) {
  // City/district level bubbles
  renderRegionBubbles(regionStats, 'sigungu');
} else {
  // Province level bubbles
  renderRegionBubbles(regionStats, 'sido');
}
```

## TypeScript Global Type

```tsx
// Top of component file or global.d.ts
declare global {
  interface Window {
    naver: any;
  }
}
```

> Official @types/navermaps package exists but has many v3 API mismatches.
> Using `any` type is practical. Define custom project-level types if needed.

## Cleanup (Component Unmount)

```tsx
useEffect(() => {
  return () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.destroy();
      mapInstanceRef.current = null;
    }
  };
}, []);
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank map (gray screen) | Using `ncpClientId` | Change to `ncpKeyId` |
| "Unauthorized" error | Web Service URL not registered or includes port | Register host only (`http://localhost`) |
| Broken/clipped tiles | Tailwind `img { max-width: 100% }` | `.naver-map img { max-width: none }` |
| Tiles not rendering | Absolute-positioned container | Use inline style `width:100%; height:100%` |
| Map size is 0 | Parent container has no height | Set explicit height on parent |
| SDK not loading | CSP policy blocking | Allow `oapi.map.naver.com` |
| Marker clicks not working | z-index overlap | Set marker `zIndex` option |
| Can't find API in console | Searching in "AI·NAVER API" | Go to **Application Services > Maps** |

## API Endpoints Reference

| API | URL Pattern |
|-----|------------|
| Web Dynamic Map | `https://oapi.map.naver.com/openapi/v3/maps.js` |
| Static Map | `https://naveropenapi.apigw.ntruss.com/map-static/v2/raster` |
| Geocoding | `https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode` |
| Reverse Geocoding | `https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc` |
| Directions | `https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving` |
