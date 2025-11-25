import { Routes, Route } from 'react-router-dom';
import StatusDashboard from '../components/machine-status/StatusDashboard';
import StatusUpdateForm from '../components/machine-status/StatusUpdateForm';
import StatusHistory from '../components/machine-status/StatusHistory';

const MachineStatusPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Routes>
        <Route index element={<StatusDashboard />} />
        <Route path="new" element={<StatusUpdateForm />} />
        <Route path="history/:assetId" element={<StatusHistory />} />
      </Routes>
    </div>
  );
};

export default MachineStatusPage;
