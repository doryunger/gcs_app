import React, { useState, useEffect, useRef, useCallback } from 'react';
import  useWebSocket  from '../hooks/useWebSocket';
import { useMap } from '../hooks/useMap';
import { updateUAVSource, updateFeatureProperty } from '../utils/mapActions';
import UAVTable from './UAVTable';
import 'mapbox-gl/dist/mapbox-gl.css';

const MapComponent: React.FC = () => {
  const [vertices, setVertices] = useState<number[][]>([]);
  const [showSubmit, setShowSubmit] = useState(false);
  const [receivedMessage, setReceivedMessage] = useState<any | null>(null);
  const [activeUAVs, setActiveUAVs] = useState<{ [key: string]: [number, number] }>({});
  const currentPolygon = useRef({ type: 'Feature', geometry: { type: 'Polygon', coordinates: [] }, properties: {} } as GeoJSON.Feature<GeoJSON.Polygon>);

  const handleWebSocketMessage = useCallback((event: MessageEvent) => {
    const response = JSON.parse(event.data as string);
    if (response.status === 'success' && response.message === 'Fenced area updated') {
      updateFeatureProperty(mapRef, currentPolygon.current, setActiveUAVs);
      setReceivedMessage('success');
      const swarm_uavs = response.data.swarm.uavs;
      for (let i = 0; i < swarm_uavs.length; i++) {
        updateUAVSource(mapRef, swarm_uavs[i], setActiveUAVs);
      }
    } else if (response.message === 'UAVs updated') {
      updateUAVSource(mapRef, response.data, setActiveUAVs);
    } else {
      setReceivedMessage(event.data);
    }
  }, []);

  const updateArea = useCallback(() => {
    const data = draw.current!.getAll();
    if (data.features.length > 1) deletePreviousDraw();
    if (data.features.length > 0) {
      const polygon = data.features[data.features.length - 1] as GeoJSON.Feature<GeoJSON.Polygon>;
      const coordinates = polygon.geometry.coordinates[0];
      currentPolygon.current.geometry = polygon.geometry;
      setVertices(coordinates);
      setShowSubmit(true);
    } else {
      setShowSubmit(false);
    }
  }, []);

  const ws = useWebSocket('ws://0.0.0.0:8765', handleWebSocketMessage);
  const { mapRef, draw } = useMap(updateArea);

  useEffect(() => {
    if (receivedMessage) {
      setReceivedMessage(receivedMessage);
    }
  }, [receivedMessage]);


  const handleSubmit = () => {
    const command = {
      command: 'update_fenced_area',
      data: vertices
    };
    ws.current!.send(JSON.stringify(command));
    setShowSubmit(false);
  };

  const deletePreviousDraw = () => {
    if (draw.current) {
      const draws = draw.current.getAll().features;
      if (draws.length > 0) {
        const firstId = draws[0].id;
        if (firstId) draw.current.delete(firstId.toString());
      }
    }
  };

  return (
    <div>
      <div id="map" style={{ width: '100vw', height: '100vh' }} />
      {showSubmit && (
        <button onClick={handleSubmit} style={{ height: '32px', position: 'absolute', top: '9px', right: '45px', fontSize: '20px', borderRadius: '5px' }}>
          ✓
        </button>
      )}
      <UAVTable activeUAVs={activeUAVs} />
    </div>
  );
};

export default MapComponent;