import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';

mapboxgl.accessToken = 'pk.eyJ1IjoibW1lMTAyIiwiYSI6ImNqM3JzaXdqNjAwMG8yd3A2YWF6YTRxZzEifQ.JaFldB_ZHqtyprzoPiLwcw';

export const useMap = (updateArea: () => void) => {
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const draw = useRef<MapboxDraw | null>(null);

  useEffect(() => {
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
      const map = new mapboxgl.Map({
        container: mapContainer,
        style: 'mapbox://styles/mapbox/satellite-v9',
        center: [11.776759, 49.683292],
        zoom: 12
      });
      mapRef.current = map;
      draw.current = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
          polygon: true,
          trash: false
        },
        styles: [
          {
            'id': 'gl-draw-polygon-fill-edit',
            'type': 'fill',
            'paint': {
              'fill-color': '#e79f53',
              'fill-opacity': 0.5
            }
          },
          {
            'id': 'gl-draw-polygon-stroke',
            'type': 'line',
            'filter': ['all', ['==', '$type', 'Polygon']],
            'layout': {
              'line-cap': 'round',
              'line-join': 'round'
            },
            'paint': {
              'line-color': '#e79f53',
              'line-width': 2
            }
          }
        ]
      });

      map.addControl(draw.current);
      map.on('load', () => {
        map.loadImage('/images/uav.png', (error, image) => {
          if (error) throw error;
          if (image) map.addImage('uav', image);
        });

        map.addSource('uavs', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: [],
          },
        });

        map.addLayer({
          id: 'fenced-area',
          type: 'fill',
          source: {
            type: 'geojson',
            data: {
              type: 'FeatureCollection',
              features: []
            }
          },
          paint: {
            'fill-color': '#00ffff',
            'fill-opacity': 0.5
          }
        });

        map.addLayer({
          id: 'fenced-area-outline',
          type: 'line',
          source: 'fenced-area',
          paint: {
            'line-color': '#009999',
            'line-width': 2
          }
        });

        map.addLayer({
          id: 'uavsLayer',
          type: 'symbol',
          source: 'uavs',
          layout: {
            'icon-image': 'uav',
            'icon-size': 0.6,
            'text-field': ['get', 'label'],
            'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
            'text-size': 15,
            'text-offset': [0, -2],
            'text-anchor': 'top',
            'icon-allow-overlap': true,
          },
          paint: {
            'text-color': '#000000',
          },
        });
      });

      map.on('draw.create', updateArea);
      map.on('draw.update', updateArea);

      return () => {
        map.remove();
      };
    } else {
      console.error('Map container not found');
    }
  }, [updateArea]);

  return { mapRef, draw };
};