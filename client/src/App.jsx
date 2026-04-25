import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import MapSetup from './pages/MapSetup/MapSetup';
import GridEditor from './pages/GridEditor/GridEditor';
import AlgoSelector from './pages/AlgoSelector/AlgoSelector';
import Visualizer from './pages/Visualizer/Visualizer';

export default function App() {
  return (
    <AppProvider>
      <Routes>
        <Route path="/"            element={<MapSetup />}     />
        <Route path="/grid"        element={<GridEditor />}   />
        <Route path="/algorithm"   element={<AlgoSelector />} />
        <Route path="/visualizer"  element={<Visualizer />}   />
        <Route path="*"            element={<Navigate to="/" replace />} />
      </Routes>
    </AppProvider>
  );
}
