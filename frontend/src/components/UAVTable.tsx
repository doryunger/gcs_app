import React from 'react';

interface UAVTableProps {
  activeUAVs: { [key: string]: [number, number] };
}

const UAVTable: React.FC<UAVTableProps> = ({ activeUAVs }) => {
  return (
    <div className="uav-table-container">
      <table className="uav-table">
        <thead>
          <tr>
            <th colSpan={2} style={{ fontSize: '24px', textAlign: 'center' }}>Swarm UAVs</th>
          </tr>
          <tr>
            <th>UAV ID</th>
            <th>Coordinates</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(activeUAVs).map(([id, coordinates]) => (
            <tr key={id}>
              <td>{id}</td>
              <td>{coordinates.map(coord => coord.toFixed(3)).join(', ')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UAVTable;