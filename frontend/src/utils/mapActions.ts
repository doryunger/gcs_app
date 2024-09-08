import { GeoJSONSource } from 'mapbox-gl';

export const updateUAVSource = (
  mapRef: React.MutableRefObject<mapboxgl.Map | null>,
  uav: any,
  setActiveUAVs: React.Dispatch<React.SetStateAction<{ [key: string]: [number, number] }>>
) => {
  if (mapRef.current) {
    const uavSource = mapRef.current.getSource('uavs') as GeoJSONSource;
    if (uavSource) {
      const data = uavSource._data as GeoJSON.FeatureCollection;
      const updatedFeatures: GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>[] = data.features.map((feature) => {
        if (feature.properties?.id === uav.id) {
          return {
            ...feature,
            geometry: {
              type: 'Point',
              coordinates: [uav.uav_coordinates[1], uav.uav_coordinates[0]],
            },
            properties: {
              ...feature.properties,
              ...uav,
              label: uav.id,
            },
          } as GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>;
        }
        return feature;
      });

      const featureExists = updatedFeatures.some((feature) => feature.properties?.id === uav.id);
      if (!featureExists) {
        updatedFeatures.push({
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [uav.uav_coordinates[1], uav.uav_coordinates[0]],
          },
          properties: { ...uav, label: uav.id },
        } as GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>);
      }

      uavSource.setData({
        type: 'FeatureCollection',
        features: updatedFeatures,
      });

      setActiveUAVs((prevState) => ({
        ...prevState,
        [uav.id]: [uav.uav_coordinates[0], uav.uav_coordinates[1]],
      }));
    }
  }
};

export const updateFeatureProperty = (
  mapRef: React.MutableRefObject<mapboxgl.Map | null>,
  feature: GeoJSON.Feature,
  setActiveUAVs: React.Dispatch<React.SetStateAction<{ [key: string]: [number, number] }>>
) => {
  if (feature) {
    if (mapRef.current) {
      const fencedAreaSource = mapRef.current.getSource('fenced-area') as GeoJSONSource;
      if (fencedAreaSource) {
        fencedAreaSource.setData({
          type: 'FeatureCollection',
          features: [feature],
        });
      }

      const uavsData = mapRef.current.getSource('uavs') as GeoJSONSource;
      uavsData.setData({
        type: 'FeatureCollection',
        features: [],
      });
      setActiveUAVs({});
    } else {
      console.log('no map');
    }
  } else {
    console.error('Feature not found');
  }
};