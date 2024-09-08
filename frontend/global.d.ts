import mapboxgl from 'mapbox-gl';

declare global {
  interface Window {
    currentMap: mapboxgl.Map;
  }
}